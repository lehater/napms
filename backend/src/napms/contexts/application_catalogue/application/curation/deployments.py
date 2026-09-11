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
    CatalogueConcurrencyConflict,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
)
from napms.contexts.application_catalogue.application.curation.structure import (
    CatalogueMutationOutcome,
)
from napms.contexts.application_catalogue.domain.model import (
    CatalogueInvariantError,
    CatalogueLifecycleState,
    ComponentDeployment,
)


_CREATE_DEPLOYMENT = "CreateComponentDeployment"
_RENAME_DEPLOYMENT = "RenameComponentDeployment"
_RETIRE_DEPLOYMENT = "RetireComponentDeployment"


@dataclass(frozen=True, slots=True)
class CreateComponentDeploymentCommand:
    component_id: UUID
    display_name: str | None
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RenameComponentDeploymentCommand:
    deployment_id: UUID
    display_name: str | None
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RetireComponentDeploymentCommand:
    deployment_id: UUID
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ComponentDeploymentMutationResult:
    outcome: CatalogueMutationOutcome
    deployment: ComponentDeployment | None = None
    result_version: int | None = None


def _required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def _optional(value: str | None) -> tuple[bool, str | None]:
    if value is None:
        return True, None
    normalized = value.strip()
    return (bool(normalized), normalized or None)


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _authority_failure(check):
    from napms.contexts.application_catalogue.application.ports import (
        ApplicationCatalogueAuthorityOutcome,
    )

    if check.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
        return CatalogueMutationOutcome.AUTHORITY_DENIED
    if (
        check.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
        or check.authority_reference is None
    ):
        return CatalogueMutationOutcome.AUTHORITY_UNKNOWN
    return None


def _resolve_receipt(
    *,
    repository: ApplicationCatalogueCurationRepository,
    actor_id: str,
    idempotency_key: str,
    command_kind: str,
    request_fingerprint: str,
) -> ComponentDeploymentMutationResult | None:
    receipt = repository.find_command_receipt(
        actor_id=actor_id,
        idempotency_key=idempotency_key,
    )
    if receipt is None:
        return None
    if (
        receipt.command_kind != command_kind
        or receipt.request_fingerprint != request_fingerprint
    ):
        return ComponentDeploymentMutationResult(
            CatalogueMutationOutcome.IDEMPOTENCY_CONFLICT
        )
    deployment = repository.get_component_deployment(receipt.result_id)
    if deployment is None:
        return ComponentDeploymentMutationResult(
            CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
        )
    return ComponentDeploymentMutationResult(
        CatalogueMutationOutcome.RESOLVED,
        deployment=deployment,
        result_version=receipt.result_version,
    )


def _active_parent_chain(
    *,
    repository: ApplicationCatalogueCurationRepository,
    component_id: UUID,
) -> CatalogueMutationOutcome | None:
    component = repository.get_component(component_id)
    if component is None:
        return CatalogueMutationOutcome.NOT_FOUND
    if component.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
        return CatalogueMutationOutcome.PARENT_INACTIVE

    application = repository.get_application(component.application_id)
    if application is None:
        return CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
    if application.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
        return CatalogueMutationOutcome.PARENT_INACTIVE
    return None


class CreateComponentDeployment:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: ApplicationCatalogueCurationRepository,
        identities: ApplicationCatalogueIdentityFactory,
        provenance: ApplicationCatalogueProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._identities = identities
        self._provenance = provenance

    def execute(
        self,
        command: CreateComponentDeploymentCommand,
    ) -> ComponentDeploymentMutationResult:
        check = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        authority_failure = _authority_failure(check)
        if authority_failure is not None:
            return ComponentDeploymentMutationResult(authority_failure)

        idempotency_key = _required(command.idempotency_key)
        display_valid, display_name = _optional(command.display_name)
        if idempotency_key is None or not display_valid:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        request_fingerprint = _fingerprint(
            {
                "componentId": str(command.component_id),
                "displayName": display_name,
            }
        )
        replay = _resolve_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_CREATE_DEPLOYMENT,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        parent_failure = _active_parent_chain(
            repository=self._catalogue,
            component_id=command.component_id,
        )
        if parent_failure is not None:
            return ComponentDeploymentMutationResult(parent_failure)

        deployment_id = self._identities.new_component_deployment_id()
        provenance_reference = self._provenance.for_component_deployment(
            deployment_id=deployment_id,
            actor_id=command.actor_id,
            authority_reference=check.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            deployment = ComponentDeployment(
                deployment_id=deployment_id,
                component_id=command.component_id,
                provenance_reference=provenance_reference,
                display_name=display_name,
            )
        except CatalogueInvariantError:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        self._catalogue.add_component_deployment(deployment)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_CREATE_DEPLOYMENT,
                request_fingerprint=request_fingerprint,
                result_id=deployment.deployment_id,
                result_version=deployment.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_CREATE_DEPLOYMENT,
                request_fingerprint=request_fingerprint,
            )
            return replay or ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )

        return ComponentDeploymentMutationResult(
            CatalogueMutationOutcome.CREATED,
            deployment=deployment,
            result_version=deployment.version,
        )


class RenameComponentDeployment:
    def __init__(self, *, authority, catalogue) -> None:
        self._authority = authority
        self._catalogue = catalogue

    def execute(
        self,
        command: RenameComponentDeploymentCommand,
    ) -> ComponentDeploymentMutationResult:
        check = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        authority_failure = _authority_failure(check)
        if authority_failure is not None:
            return ComponentDeploymentMutationResult(authority_failure)

        idempotency_key = _required(command.idempotency_key)
        display_valid, display_name = _optional(command.display_name)
        if (
            idempotency_key is None
            or not display_valid
            or command.expected_version < 1
        ):
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        request_fingerprint = _fingerprint(
            {
                "deploymentId": str(command.deployment_id),
                "displayName": display_name,
                "expectedVersion": command.expected_version,
            }
        )
        replay = _resolve_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_RENAME_DEPLOYMENT,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        current = self._catalogue.get_component_deployment(command.deployment_id)
        if current is None:
            return ComponentDeploymentMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.CONCURRENCY_CONFLICT
            )

        try:
            updated = current.renamed(display_name)
        except CatalogueInvariantError:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        try:
            self._catalogue.save_component_deployment(
                updated,
                expected_version=command.expected_version,
            )
        except CatalogueConcurrencyConflict:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.CONCURRENCY_CONFLICT
            )

        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_RENAME_DEPLOYMENT,
                request_fingerprint=request_fingerprint,
                result_id=updated.deployment_id,
                result_version=updated.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_RENAME_DEPLOYMENT,
                request_fingerprint=request_fingerprint,
            )
            return replay or ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )

        return ComponentDeploymentMutationResult(
            CatalogueMutationOutcome.UPDATED,
            deployment=updated,
            result_version=updated.version,
        )


class RetireComponentDeployment:
    def __init__(self, *, authority, catalogue, provenance) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._provenance = provenance

    def execute(
        self,
        command: RetireComponentDeploymentCommand,
    ) -> ComponentDeploymentMutationResult:
        check = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        authority_failure = _authority_failure(check)
        if authority_failure is not None:
            return ComponentDeploymentMutationResult(authority_failure)

        idempotency_key = _required(command.idempotency_key)
        if idempotency_key is None or command.expected_version < 1:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        request_fingerprint = _fingerprint(
            {
                "deploymentId": str(command.deployment_id),
                "expectedVersion": command.expected_version,
            }
        )
        replay = _resolve_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_RETIRE_DEPLOYMENT,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        current = self._catalogue.get_component_deployment(command.deployment_id)
        if current is None:
            return ComponentDeploymentMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.CONCURRENCY_CONFLICT
            )

        retirement_provenance = (
            self._provenance.for_component_deployment_retirement(
                deployment_id=command.deployment_id,
                actor_id=command.actor_id,
                authority_reference=check.authority_reference,
                effective_time=command.effective_time,
            )
        )
        try:
            updated = current.retired(
                retirement_provenance_reference=retirement_provenance,
            )
        except CatalogueInvariantError:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        try:
            self._catalogue.save_component_deployment(
                updated,
                expected_version=command.expected_version,
            )
        except CatalogueConcurrencyConflict:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.CONCURRENCY_CONFLICT
            )

        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_RETIRE_DEPLOYMENT,
                request_fingerprint=request_fingerprint,
                result_id=updated.deployment_id,
                result_version=updated.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_RETIRE_DEPLOYMENT,
                request_fingerprint=request_fingerprint,
            )
            return replay or ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )

        return ComponentDeploymentMutationResult(
            CatalogueMutationOutcome.UPDATED,
            deployment=updated,
            result_version=updated.version,
        )
