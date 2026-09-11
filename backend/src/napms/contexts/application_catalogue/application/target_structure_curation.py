from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCommandReceipt,
    ApplicationCatalogueCurationAuthorityPort,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
)
from napms.contexts.application_catalogue.application.target_curation import TargetMutationOutcome
from napms.contexts.application_catalogue.application.target_ports import (
    TargetApplicationCatalogueIdentityFactory,
    TargetApplicationCatalogueProvenanceFactory,
    TargetApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.domain.model import (
    CatalogueInvariantError,
    CatalogueLifecycleState,
    Component,
)


_CREATE_TARGET_COMPONENT = "CreateTargetComponent"


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

    def _resolve_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        fingerprint: str,
    ) -> TargetComponentMutationResult | None:
        receipt = self._catalogue.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _CREATE_TARGET_COMPONENT
            or receipt.request_fingerprint != fingerprint
        ):
            return TargetComponentMutationResult(TargetMutationOutcome.IDEMPOTENCY_CONFLICT)
        existing = self._catalogue.get_component(receipt.result_id)
        if existing is None:
            return TargetComponentMutationResult(TargetMutationOutcome.PERSISTENCE_UNKNOWN)
        return TargetComponentMutationResult(TargetMutationOutcome.RESOLVED, existing)

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
        replay = self._resolve_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )
        if replay is not None:
            return replay

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
                command_kind=_CREATE_TARGET_COMPONENT,
                request_fingerprint=fingerprint,
                result_id=component.component_id,
                result_version=component.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = self._resolve_receipt(
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                fingerprint=fingerprint,
            )
            return replay or TargetComponentMutationResult(
                TargetMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return TargetComponentMutationResult(TargetMutationOutcome.PERSISTENCE_UNKNOWN)
        return TargetComponentMutationResult(TargetMutationOutcome.CREATED, component)
