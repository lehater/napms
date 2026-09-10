from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from uuid import UUID

from napms.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCommandReceipt,
    ApplicationCatalogueCurationAuthorityPort,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
)
from napms.application_catalogue.application.target_curation import TargetMutationOutcome
from napms.application_catalogue.application.target_ports import (
    TargetApplicationCatalogueIdentityFactory,
    TargetApplicationCatalogueProvenanceFactory,
    TargetApplicationCatalogueRepository,
)
from napms.application_catalogue.domain.model import (
    CatalogueInvariantError,
    CatalogueLifecycleState,
    Component,
)


@dataclass(frozen=True, slots=True)
class CreateTargetComponentCommand:
    application_id: UUID
    display_name: str
    actor_id: str
    effective_time: datetime
    idempotency_key: str
    component_type: str | None = None
    description: str | None = None


@dataclass(frozen=True, slots=True)
class TargetComponentMutationResult:
    outcome: TargetMutationOutcome
    component: Component | None = None


def _required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def _optional(value: str | None) -> tuple[str | None, bool]:
    if value is None:
        return None, True
    normalized = value.strip()
    return (normalized or None), bool(normalized)


def _fingerprint(payload: dict[str, object]) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


class CreateTargetComponent:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: TargetApplicationCatalogueRepository,
        identities: TargetApplicationCatalogueIdentityFactory,
        provenance: TargetApplicationCatalogueProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._identities = identities
        self._provenance = provenance

    def execute(self, command: CreateTargetComponentCommand) -> TargetComponentMutationResult:
        check = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if check.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
            return TargetComponentMutationResult(TargetMutationOutcome.AUTHORITY_DENIED)
        if (
            check.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
            or check.authority_reference is None
        ):
            return TargetComponentMutationResult(TargetMutationOutcome.AUTHORITY_UNKNOWN)

        display_name = _required(command.display_name)
        idempotency_key = _required(command.idempotency_key)
        component_type, component_type_valid = _optional(command.component_type)
        description, description_valid = _optional(command.description)
        if (
            display_name is None
            or idempotency_key is None
            or not component_type_valid
            or not description_valid
        ):
            return TargetComponentMutationResult(TargetMutationOutcome.INPUT_INVALID)

        fingerprint = _fingerprint(
            {
                "applicationId": str(command.application_id),
                "displayName": display_name,
                "componentType": component_type,
                "description": description,
            }
        )
        receipt = self._catalogue.find_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is not None:
            if (
                receipt.command_kind != "CreateTargetComponent"
                or receipt.request_fingerprint != fingerprint
            ):
                return TargetComponentMutationResult(
                    TargetMutationOutcome.IDEMPOTENCY_CONFLICT
                )
            existing = self._catalogue.get_component(receipt.result_id)
            if existing is None:
                return TargetComponentMutationResult(
                    TargetMutationOutcome.PERSISTENCE_UNKNOWN
                )
            return TargetComponentMutationResult(
                TargetMutationOutcome.RESOLVED,
                existing,
            )

        application = self._catalogue.get_application(command.application_id)
        if application is None:
            return TargetComponentMutationResult(TargetMutationOutcome.NOT_FOUND)
        if application.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
            return TargetComponentMutationResult(TargetMutationOutcome.PARENT_INACTIVE)

        component_id = self._identities.new_component_id()
        try:
            component = Component(
                component_id=component_id,
                application_id=application.application_id,
                display_name=display_name,
                provenance_reference=self._provenance.for_component(
                    component_id=component_id,
                    actor_id=command.actor_id,
                    authority_reference=check.authority_reference,
                    effective_time=command.effective_time,
                ),
                component_type=component_type,
                description=description,
            )
        except CatalogueInvariantError:
            return TargetComponentMutationResult(TargetMutationOutcome.INPUT_INVALID)

        self._catalogue.add_component(component)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind="CreateTargetComponent",
                request_fingerprint=fingerprint,
                result_id=component.component_id,
                result_version=component.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            return TargetComponentMutationResult(TargetMutationOutcome.IDEMPOTENCY_CONFLICT)
        except CataloguePersistenceOutcomeUnknown:
            return TargetComponentMutationResult(TargetMutationOutcome.PERSISTENCE_UNKNOWN)
        return TargetComponentMutationResult(TargetMutationOutcome.CREATED, component)
