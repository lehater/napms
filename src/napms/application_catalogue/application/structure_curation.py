from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from uuid import UUID

from napms.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCommandReceipt,
    ApplicationCatalogueConcurrencyConflict,
    ApplicationCatalogueCurationAuthorityPort,
    ApplicationCatalogueCurationRepository,
    ApplicationCatalogueIdentityFactory,
    ApplicationCatalogueProvenanceFactory,
    CatalogueConcurrencyConflict,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
)
from napms.application_catalogue.domain.model import (
    CatalogueInvariantError,
    CatalogueLifecycleState,
    Component,
)


_CREATE_COMPONENT = "CreateComponent"
_RENAME_APPLICATION = "RenameApplication"
_RETIRE_APPLICATION = "RetireApplication"
_RENAME_COMPONENT = "RenameComponent"
_RETIRE_COMPONENT = "RetireComponent"


class CatalogueMutationOutcome(str, Enum):
    CREATED = "Created"
    UPDATED = "Updated"
    RESOLVED = "Resolved"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    NOT_FOUND = "NotFound"
    PARENT_INACTIVE = "ParentInactive"
    RETIREMENT_BLOCKED = "RetirementBlocked"
    INPUT_INVALID = "InputInvalid"
    CONCURRENCY_CONFLICT = "ConcurrencyConflict"
    IDEMPOTENCY_CONFLICT = "IdempotencyConflict"
    PERSISTENCE_UNKNOWN = "PersistenceUnknown"


@dataclass(frozen=True, slots=True)
class RenameApplicationCommand:
    application_id: UUID
    display_name: str
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RetireApplicationCommand:
    application_id: UUID
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ApplicationMutationResult:
    outcome: CatalogueMutationOutcome
    application: object | None = None
    result_version: int | None = None


@dataclass(frozen=True, slots=True)
class CreateComponentCommand:
    application_id: UUID
    display_name: str
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RenameComponentCommand:
    component_id: UUID
    display_name: str
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RetireComponentCommand:
    component_id: UUID
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ComponentMutationResult:
    outcome: CatalogueMutationOutcome
    component: Component | None = None
    result_version: int | None = None


def _required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _authorize(
    authority: ApplicationCatalogueCurationAuthorityPort,
    *,
    actor_id: str,
    effective_time: datetime,
) -> ApplicationCatalogueAuthorityCheck:
    return authority.check_curation(
        actor_id=actor_id,
        effective_time=effective_time,
    )


def _authority_failure(check: ApplicationCatalogueAuthorityCheck):
    if check.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
        return CatalogueMutationOutcome.AUTHORITY_DENIED
    if (
        check.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
        or check.authority_reference is None
    ):
        return CatalogueMutationOutcome.AUTHORITY_UNKNOWN
    return None


def _resolve_application_receipt(
    *,
    repository: ApplicationCatalogueCurationRepository,
    actor_id: str,
    idempotency_key: str,
    command_kind: str,
    request_fingerprint: str,
) -> ApplicationMutationResult | None:
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
        return ApplicationMutationResult(CatalogueMutationOutcome.IDEMPOTENCY_CONFLICT)
    application = repository.get_application(receipt.result_id)
    if application is None:
        return ApplicationMutationResult(CatalogueMutationOutcome.PERSISTENCE_UNKNOWN)
    return ApplicationMutationResult(
        CatalogueMutationOutcome.RESOLVED,
        application=application,
        result_version=receipt.result_version,
    )


def _resolve_component_receipt(
    *,
    repository: ApplicationCatalogueCurationRepository,
    actor_id: str,
    idempotency_key: str,
    command_kind: str,
    request_fingerprint: str,
) -> ComponentMutationResult | None:
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
        return ComponentMutationResult(CatalogueMutationOutcome.IDEMPOTENCY_CONFLICT)
    component = repository.get_component(receipt.result_id)
    if component is None:
        return ComponentMutationResult(CatalogueMutationOutcome.PERSISTENCE_UNKNOWN)
    return ComponentMutationResult(
        CatalogueMutationOutcome.RESOLVED,
        component=component,
        result_version=receipt.result_version,
    )


class RenameApplication:
    def __init__(self, *, authority, catalogue) -> None:
        self._authority = authority
        self._catalogue = catalogue

    def execute(self, command: RenameApplicationCommand) -> ApplicationMutationResult:
        check = _authorize(
            self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        failure = _authority_failure(check)
        if failure is not None:
            return ApplicationMutationResult(failure)

        display_name = _required(command.display_name)
        idempotency_key = _required(command.idempotency_key)
        if display_name is None or idempotency_key is None or command.expected_version < 1:
            return ApplicationMutationResult(CatalogueMutationOutcome.INPUT_INVALID)

        request_fingerprint = _fingerprint(
            {
                "applicationId": str(command.application_id),
                "displayName": display_name,
                "expectedVersion": command.expected_version,
            }
        )
        replay = _resolve_application_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_RENAME_APPLICATION,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        current = self._catalogue.get_application(command.application_id)
        if current is None:
            return ApplicationMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return ApplicationMutationResult(CatalogueMutationOutcome.CONCURRENCY_CONFLICT)
        try:
            updated = current.renamed(display_name)
        except CatalogueInvariantError:
            return ApplicationMutationResult(CatalogueMutationOutcome.INPUT_INVALID)

        try:
            self._catalogue.save_application(updated, expected_version=command.expected_version)
        except CatalogueConcurrencyConflict:
            return ApplicationMutationResult(CatalogueMutationOutcome.CONCURRENCY_CONFLICT)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_RENAME_APPLICATION,
                request_fingerprint=request_fingerprint,
                result_id=updated.application_id,
                result_version=updated.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_application_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_RENAME_APPLICATION,
                request_fingerprint=request_fingerprint,
            )
            return replay or ApplicationMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return ApplicationMutationResult(CatalogueMutationOutcome.PERSISTENCE_UNKNOWN)
        return ApplicationMutationResult(
            CatalogueMutationOutcome.UPDATED,
            application=updated,
            result_version=updated.version,
        )


class RetireApplication:
    def __init__(self, *, authority, catalogue, provenance) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._provenance = provenance

    def execute(self, command: RetireApplicationCommand) -> ApplicationMutationResult:
        check = _authorize(
            self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        failure = _authority_failure(check)
        if failure is not None:
            return ApplicationMutationResult(failure)

        idempotency_key = _required(command.idempotency_key)
        if idempotency_key is None or command.expected_version < 1:
            return ApplicationMutationResult(CatalogueMutationOutcome.INPUT_INVALID)
        request_fingerprint = _fingerprint(
            {
                "applicationId": str(command.application_id),
                "expectedVersion": command.expected_version,
            }
        )
        replay = _resolve_application_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_RETIRE_APPLICATION,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        current = self._catalogue.get_application(command.application_id)
        if current is None:
            return ApplicationMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return ApplicationMutationResult(CatalogueMutationOutcome.CONCURRENCY_CONFLICT)
        if self._catalogue.has_active_components(application_id=command.application_id):
            return ApplicationMutationResult(CatalogueMutationOutcome.RETIREMENT_BLOCKED)

        retirement_provenance = self._provenance.for_application_retirement(
            application_id=command.application_id,
            actor_id=command.actor_id,
            authority_reference=check.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            updated = current.retired(
                retirement_provenance_reference=retirement_provenance,
            )
        except CatalogueInvariantError:
            return ApplicationMutationResult(CatalogueMutationOutcome.INPUT_INVALID)
        try:
            self._catalogue.save_application(updated, expected_version=command.expected_version)
        except CatalogueConcurrencyConflict:
            return ApplicationMutationResult(CatalogueMutationOutcome.CONCURRENCY_CONFLICT)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_RETIRE_APPLICATION,
                request_fingerprint=request_fingerprint,
                result_id=updated.application_id,
                result_version=updated.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_application_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_RETIRE_APPLICATION,
                request_fingerprint=request_fingerprint,
            )
            return replay or ApplicationMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return ApplicationMutationResult(CatalogueMutationOutcome.PERSISTENCE_UNKNOWN)
        return ApplicationMutationResult(
            CatalogueMutationOutcome.UPDATED,
            application=updated,
            result_version=updated.version,
        )


class CreateComponent:
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

    def execute(self, command: CreateComponentCommand) -> ComponentMutationResult:
        check = _authorize(
            self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        failure = _authority_failure(check)
        if failure is not None:
            return ComponentMutationResult(failure)

        display_name = _required(command.display_name)
        idempotency_key = _required(command.idempotency_key)
        if display_name is None or idempotency_key is None:
            return ComponentMutationResult(CatalogueMutationOutcome.INPUT_INVALID)
        request_fingerprint = _fingerprint(
            {
                "applicationId": str(command.application_id),
                "displayName": display_name,
            }
        )
        replay = _resolve_component_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_CREATE_COMPONENT,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        application = self._catalogue.get_application(command.application_id)
        if application is None:
            return ComponentMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if application.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
            return ComponentMutationResult(CatalogueMutationOutcome.PARENT_INACTIVE)

        component_id = self._identities.new_component_id()
        provenance_reference = self._provenance.for_component(
            component_id=component_id,
            actor_id=command.actor_id,
            authority_reference=check.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            component = Component(
                component_id=component_id,
                application_id=command.application_id,
                display_name=display_name,
                provenance_reference=provenance_reference,
            )
        except CatalogueInvariantError:
            return ComponentMutationResult(CatalogueMutationOutcome.INPUT_INVALID)

        self._catalogue.add_component(component)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_CREATE_COMPONENT,
                request_fingerprint=request_fingerprint,
                result_id=component.component_id,
                result_version=component.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_component_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_CREATE_COMPONENT,
                request_fingerprint=request_fingerprint,
            )
            return replay or ComponentMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return ComponentMutationResult(CatalogueMutationOutcome.PERSISTENCE_UNKNOWN)
        return ComponentMutationResult(
            CatalogueMutationOutcome.CREATED,
            component=component,
            result_version=component.version,
        )


class RenameComponent:
    def __init__(self, *, authority, catalogue) -> None:
        self._authority = authority
        self._catalogue = catalogue

    def execute(self, command: RenameComponentCommand) -> ComponentMutationResult:
        check = _authorize(
            self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        failure = _authority_failure(check)
        if failure is not None:
            return ComponentMutationResult(failure)

        display_name = _required(command.display_name)
        idempotency_key = _required(command.idempotency_key)
        if display_name is None or idempotency_key is None or command.expected_version < 1:
            return ComponentMutationResult(CatalogueMutationOutcome.INPUT_INVALID)
        request_fingerprint = _fingerprint(
            {
                "componentId": str(command.component_id),
                "displayName": display_name,
                "expectedVersion": command.expected_version,
            }
        )
        replay = _resolve_component_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_RENAME_COMPONENT,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        current = self._catalogue.get_component(command.component_id)
        if current is None:
            return ComponentMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return ComponentMutationResult(CatalogueMutationOutcome.CONCURRENCY_CONFLICT)
        try:
            updated = current.renamed(display_name)
        except CatalogueInvariantError:
            return ComponentMutationResult(CatalogueMutationOutcome.INPUT_INVALID)
        try:
            self._catalogue.save_component(updated, expected_version=command.expected_version)
        except CatalogueConcurrencyConflict:
            return ComponentMutationResult(CatalogueMutationOutcome.CONCURRENCY_CONFLICT)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_RENAME_COMPONENT,
                request_fingerprint=request_fingerprint,
                result_id=updated.component_id,
                result_version=updated.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_component_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_RENAME_COMPONENT,
                request_fingerprint=request_fingerprint,
            )
            return replay or ComponentMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return ComponentMutationResult(CatalogueMutationOutcome.PERSISTENCE_UNKNOWN)
        return ComponentMutationResult(
            CatalogueMutationOutcome.UPDATED,
            component=updated,
            result_version=updated.version,
        )


class RetireComponent:
    def __init__(self, *, authority, catalogue, provenance) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._provenance = provenance

    def execute(self, command: RetireComponentCommand) -> ComponentMutationResult:
        check = _authorize(
            self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        failure = _authority_failure(check)
        if failure is not None:
            return ComponentMutationResult(failure)

        idempotency_key = _required(command.idempotency_key)
        if idempotency_key is None or command.expected_version < 1:
            return ComponentMutationResult(CatalogueMutationOutcome.INPUT_INVALID)
        request_fingerprint = _fingerprint(
            {
                "componentId": str(command.component_id),
                "expectedVersion": command.expected_version,
            }
        )
        replay = _resolve_component_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_RETIRE_COMPONENT,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        current = self._catalogue.get_component(command.component_id)
        if current is None:
            return ComponentMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return ComponentMutationResult(CatalogueMutationOutcome.CONCURRENCY_CONFLICT)
        if self._catalogue.has_active_component_deployments(component_id=command.component_id):
            return ComponentMutationResult(CatalogueMutationOutcome.RETIREMENT_BLOCKED)

        retirement_provenance = self._provenance.for_component_retirement(
            component_id=command.component_id,
            actor_id=command.actor_id,
            authority_reference=check.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            updated = current.retired(
                retirement_provenance_reference=retirement_provenance,
            )
        except CatalogueInvariantError:
            return ComponentMutationResult(CatalogueMutationOutcome.INPUT_INVALID)
        try:
            self._catalogue.save_component(updated, expected_version=command.expected_version)
        except CatalogueConcurrencyConflict:
            return ComponentMutationResult(CatalogueMutationOutcome.CONCURRENCY_CONFLICT)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_RETIRE_COMPONENT,
                request_fingerprint=request_fingerprint,
                result_id=updated.component_id,
                result_version=updated.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_component_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_RETIRE_COMPONENT,
                request_fingerprint=request_fingerprint,
            )
            return replay or ComponentMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return ComponentMutationResult(CatalogueMutationOutcome.PERSISTENCE_UNKNOWN)
        return ComponentMutationResult(
            CatalogueMutationOutcome.UPDATED,
            component=updated,
            result_version=updated.version,
        )
