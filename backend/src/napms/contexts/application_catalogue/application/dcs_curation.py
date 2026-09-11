from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueCommandReceipt,
    ApplicationCatalogueCurationAuthorityPort,
    ApplicationCatalogueCurationRepository,
    ApplicationCatalogueIdentityFactory,
    ApplicationCatalogueProvenanceFactory,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
    DcsProjectionAuthoringEncoder,
)
from napms.contexts.application_catalogue.application.structure_curation import (
    CatalogueMutationOutcome,
)
from napms.contexts.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    canonical_dcs_alternatives,
)
from napms.contexts.application_catalogue.domain.model import (
    CatalogueInvariantError,
    CatalogueLifecycleState,
    DcsRevision,
)


_CREATE_DCS_REVISION = "CreateDcsRevision"


@dataclass(frozen=True, slots=True)
class CreateDcsRevisionCommand:
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    display_name: str | None
    traffic_alternatives: tuple[AuthoredDcsTrafficAlternative, ...]
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class DcsRevisionMutationResult:
    outcome: CatalogueMutationOutcome
    revision: DcsRevision | None = None
    result_version: int | None = None


def _required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def _optional(value: str | None) -> tuple[bool, str | None]:
    if value is None:
        return True, None
    normalized = value.strip()
    return (bool(normalized), normalized or None)


def _constraint_payload(value: DcsPortConstraint) -> dict[str, object]:
    return {
        "kind": value.kind.value,
        "ranges": [[item.first, item.last] for item in value.ranges],
    }


def _alternative_payload(value: AuthoredDcsTrafficAlternative) -> dict[str, object]:
    return {
        "protocol": value.protocol,
        "sourcePorts": _constraint_payload(value.source_ports),
        "destinationPorts": _constraint_payload(value.destination_ports),
        "serviceReference": value.service_reference,
    }


def _fingerprint(
    *,
    source_id: UUID,
    destination_id: UUID,
    display_name: str | None,
    alternatives: tuple[AuthoredDcsTrafficAlternative, ...],
) -> str:
    encoded = json.dumps(
        {
            "sourceComponentDeploymentId": str(source_id),
            "destinationComponentDeploymentId": str(destination_id),
            "displayName": display_name,
            "trafficAlternatives": [_alternative_payload(item) for item in alternatives],
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _resolve_receipt(
    *,
    repository: ApplicationCatalogueCurationRepository,
    actor_id: str,
    idempotency_key: str,
    request_fingerprint: str,
) -> DcsRevisionMutationResult | None:
    receipt = repository.find_command_receipt(
        actor_id=actor_id,
        idempotency_key=idempotency_key,
    )
    if receipt is None:
        return None
    if (
        receipt.command_kind != _CREATE_DCS_REVISION
        or receipt.request_fingerprint != request_fingerprint
    ):
        return DcsRevisionMutationResult(
            CatalogueMutationOutcome.IDEMPOTENCY_CONFLICT
        )
    revision = repository.get_dcs_revision(receipt.result_id)
    if revision is None:
        return DcsRevisionMutationResult(
            CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
        )
    return DcsRevisionMutationResult(
        CatalogueMutationOutcome.RESOLVED,
        revision=revision,
        result_version=receipt.result_version,
    )


class CreateDcsRevision:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: ApplicationCatalogueCurationRepository,
        identities: ApplicationCatalogueIdentityFactory,
        provenance: ApplicationCatalogueProvenanceFactory,
        encoder: DcsProjectionAuthoringEncoder,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._identities = identities
        self._provenance = provenance
        self._encoder = encoder

    def execute(self, command: CreateDcsRevisionCommand) -> DcsRevisionMutationResult:
        from napms.contexts.application_catalogue.application.ports import (
            ApplicationCatalogueAuthorityOutcome,
        )

        check = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if check.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
            return DcsRevisionMutationResult(
                CatalogueMutationOutcome.AUTHORITY_DENIED
            )
        if (
            check.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
            or check.authority_reference is None
        ):
            return DcsRevisionMutationResult(
                CatalogueMutationOutcome.AUTHORITY_UNKNOWN
            )

        idempotency_key = _required(command.idempotency_key)
        display_valid, display_name = _optional(command.display_name)
        if idempotency_key is None or not display_valid:
            return DcsRevisionMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        try:
            alternatives = canonical_dcs_alternatives(command.traffic_alternatives)
        except CatalogueInvariantError:
            return DcsRevisionMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        request_fingerprint = _fingerprint(
            source_id=command.source_component_deployment_id,
            destination_id=command.destination_component_deployment_id,
            display_name=display_name,
            alternatives=alternatives,
        )
        replay = _resolve_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        source = self._catalogue.get_component_deployment(
            command.source_component_deployment_id
        )
        destination = self._catalogue.get_component_deployment(
            command.destination_component_deployment_id
        )
        if source is None or destination is None:
            return DcsRevisionMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if (
            source.lifecycle_state is not CatalogueLifecycleState.ACTIVE
            or destination.lifecycle_state is not CatalogueLifecycleState.ACTIVE
        ):
            return DcsRevisionMutationResult(
                CatalogueMutationOutcome.PARENT_INACTIVE
            )

        projection_payload = self._encoder.encode(alternatives)
        revision_id = self._identities.new_dcs_revision_id()
        provenance_reference = self._provenance.for_dcs_revision(
            revision_id=revision_id,
            actor_id=command.actor_id,
            authority_reference=check.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            revision = DcsRevision(
                revision_id=revision_id,
                source_component_deployment_id=source.deployment_id,
                destination_component_deployment_id=destination.deployment_id,
                projection_payload=projection_payload,
                provenance_reference=provenance_reference,
                display_name=display_name,
            )
        except CatalogueInvariantError:
            return DcsRevisionMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        self._catalogue.add_dcs_revision(revision)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_CREATE_DCS_REVISION,
                request_fingerprint=request_fingerprint,
                result_id=revision.revision_id,
                result_version=1,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                request_fingerprint=request_fingerprint,
            )
            return replay or DcsRevisionMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return DcsRevisionMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )

        return DcsRevisionMutationResult(
            CatalogueMutationOutcome.CREATED,
            revision=revision,
            result_version=1,
        )
