from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from napms.contexts.application_catalogue.application.curation.mutation import (
    CatalogueMutationOutcome,
    authority_failure,
    authorize,
    fingerprint,
    required,
)
from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueCommandReceipt,
    ApplicationCatalogueCurationRepository,
    CatalogueConcurrencyConflict,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
)
from napms.contexts.application_catalogue.domain.model import CatalogueInvariantError


_RENAME_APPLICATION = "RenameApplication"
_RETIRE_APPLICATION = "RetireApplication"


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


class RenameApplication:
    def __init__(self, *, authority, catalogue) -> None:
        self._authority = authority
        self._catalogue = catalogue

    def execute(self, command: RenameApplicationCommand) -> ApplicationMutationResult:
        check = authorize(
            self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        failure = authority_failure(check)
        if failure is not None:
            return ApplicationMutationResult(failure)

        display_name = required(command.display_name)
        idempotency_key = required(command.idempotency_key)
        if display_name is None or idempotency_key is None or command.expected_version < 1:
            return ApplicationMutationResult(CatalogueMutationOutcome.INPUT_INVALID)

        request_fingerprint = fingerprint(
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
        check = authorize(
            self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        failure = authority_failure(check)
        if failure is not None:
            return ApplicationMutationResult(failure)

        idempotency_key = required(command.idempotency_key)
        if idempotency_key is None or command.expected_version < 1:
            return ApplicationMutationResult(CatalogueMutationOutcome.INPUT_INVALID)
        request_fingerprint = fingerprint(
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
