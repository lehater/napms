from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCommandReceipt,
    ApplicationCatalogueCurationAuthorityPort,
    CatalogueConcurrencyConflict,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
)
from napms.contexts.application_catalogue.application.target_curation import TargetMutationOutcome
from napms.contexts.application_catalogue.application.target_ports import (
    TargetApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.domain.model import CatalogueInvariantError


@dataclass(frozen=True, slots=True)
class UpdateApplicationDefinitionMetadataCommand:
    application_id: UUID
    display_name: str
    description: str | None
    domain: str | None
    owner_reference: str | None
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class UpdateComponentMetadataCommand:
    component_id: UUID
    display_name: str
    component_type: str | None
    description: str | None
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class UpdateApplicationDeploymentContextCommand:
    application_deployment_id: UUID
    company_reference: str
    environment: str
    scope_reference: str
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class TargetMetadataMutationResult:
    outcome: TargetMutationOutcome
    subject: object | None = None


def _fingerprint(payload: dict[str, object]) -> str:
    return sha256(
        json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        ).encode("utf-8")
    ).hexdigest()


def _authority_failure(
    authority: ApplicationCatalogueCurationAuthorityPort,
    *,
    actor_id: str,
    effective_time: datetime,
) -> TargetMutationOutcome | None:
    check = authority.check_curation(actor_id=actor_id, effective_time=effective_time)
    if check.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
        return TargetMutationOutcome.AUTHORITY_DENIED
    if (
        check.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
        or check.authority_reference is None
    ):
        return TargetMutationOutcome.AUTHORITY_UNKNOWN
    return None


def _commit(repository: TargetApplicationCatalogueRepository) -> TargetMutationOutcome | None:
    try:
        repository.commit()
    except CatalogueConcurrencyConflict:
        return TargetMutationOutcome.CONCURRENCY_CONFLICT
    except CatalogueIdempotencyConflict:
        return TargetMutationOutcome.IDEMPOTENCY_CONFLICT
    except CataloguePersistenceOutcomeUnknown:
        return TargetMutationOutcome.PERSISTENCE_UNKNOWN
    return None


def _replay(
    *,
    repository: TargetApplicationCatalogueRepository,
    actor_id: str,
    idempotency_key: str,
    command_kind: str,
    request_fingerprint: str,
    load,
) -> TargetMetadataMutationResult | None:
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
        return TargetMetadataMutationResult(TargetMutationOutcome.IDEMPOTENCY_CONFLICT)
    subject = load(receipt.result_id)
    if subject is None:
        return TargetMetadataMutationResult(TargetMutationOutcome.PERSISTENCE_UNKNOWN)
    return TargetMetadataMutationResult(TargetMutationOutcome.RESOLVED, subject)


class UpdateApplicationDefinitionMetadata:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: TargetApplicationCatalogueRepository,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue

    def execute(
        self,
        command: UpdateApplicationDefinitionMetadataCommand,
    ) -> TargetMetadataMutationResult:
        authority_failure = _authority_failure(
            self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority_failure is not None:
            return TargetMetadataMutationResult(authority_failure)
        idempotency_key = command.idempotency_key.strip() if command.idempotency_key else ""
        if not idempotency_key or command.expected_version < 1:
            return TargetMetadataMutationResult(TargetMutationOutcome.INPUT_INVALID)
        fingerprint = _fingerprint(
            {
                "applicationId": str(command.application_id),
                "displayName": command.display_name,
                "description": command.description,
                "domain": command.domain,
                "ownerReference": command.owner_reference,
                "expectedVersion": command.expected_version,
            }
        )
        replay = _replay(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind="UpdateApplicationDefinitionMetadata",
            request_fingerprint=fingerprint,
            load=self._catalogue.get_application,
        )
        if replay is not None:
            return replay
        current = self._catalogue.get_application(command.application_id)
        if current is None:
            return TargetMetadataMutationResult(TargetMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return TargetMetadataMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        try:
            updated = current.changed_metadata(
                display_name=command.display_name,
                description=command.description,
                domain=command.domain,
                owner_reference=command.owner_reference,
            )
        except CatalogueInvariantError:
            return TargetMetadataMutationResult(TargetMutationOutcome.INPUT_INVALID)
        try:
            self._catalogue.save_application(updated, expected_version=command.expected_version)
        except CatalogueConcurrencyConflict:
            return TargetMetadataMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind="UpdateApplicationDefinitionMetadata",
                request_fingerprint=fingerprint,
                result_id=updated.application_id,
                result_version=updated.version,
            ),
        )
        commit_outcome = _commit(self._catalogue)
        if commit_outcome is not None:
            return TargetMetadataMutationResult(commit_outcome)
        return TargetMetadataMutationResult(TargetMutationOutcome.UPDATED, updated)


class UpdateComponentMetadata:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: TargetApplicationCatalogueRepository,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue

    def execute(self, command: UpdateComponentMetadataCommand) -> TargetMetadataMutationResult:
        authority_failure = _authority_failure(
            self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority_failure is not None:
            return TargetMetadataMutationResult(authority_failure)
        idempotency_key = command.idempotency_key.strip() if command.idempotency_key else ""
        if not idempotency_key or command.expected_version < 1:
            return TargetMetadataMutationResult(TargetMutationOutcome.INPUT_INVALID)
        fingerprint = _fingerprint(
            {
                "componentId": str(command.component_id),
                "displayName": command.display_name,
                "componentType": command.component_type,
                "description": command.description,
                "expectedVersion": command.expected_version,
            }
        )
        replay = _replay(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind="UpdateComponentMetadata",
            request_fingerprint=fingerprint,
            load=self._catalogue.get_component,
        )
        if replay is not None:
            return replay
        current = self._catalogue.get_component(command.component_id)
        if current is None:
            return TargetMetadataMutationResult(TargetMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return TargetMetadataMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        try:
            updated = current.changed_metadata(
                display_name=command.display_name,
                component_type=command.component_type,
                description=command.description,
            )
        except CatalogueInvariantError:
            return TargetMetadataMutationResult(TargetMutationOutcome.INPUT_INVALID)
        try:
            self._catalogue.save_component(updated, expected_version=command.expected_version)
        except CatalogueConcurrencyConflict:
            return TargetMetadataMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind="UpdateComponentMetadata",
                request_fingerprint=fingerprint,
                result_id=updated.component_id,
                result_version=updated.version,
            ),
        )
        commit_outcome = _commit(self._catalogue)
        if commit_outcome is not None:
            return TargetMetadataMutationResult(commit_outcome)
        return TargetMetadataMutationResult(TargetMutationOutcome.UPDATED, updated)


class UpdateApplicationDeploymentContext:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: TargetApplicationCatalogueRepository,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue

    def execute(
        self,
        command: UpdateApplicationDeploymentContextCommand,
    ) -> TargetMetadataMutationResult:
        authority_failure = _authority_failure(
            self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority_failure is not None:
            return TargetMetadataMutationResult(authority_failure)
        idempotency_key = command.idempotency_key.strip() if command.idempotency_key else ""
        if not idempotency_key or command.expected_version < 1:
            return TargetMetadataMutationResult(TargetMutationOutcome.INPUT_INVALID)
        fingerprint = _fingerprint(
            {
                "applicationDeploymentId": str(command.application_deployment_id),
                "companyReference": command.company_reference,
                "environment": command.environment,
                "scopeReference": command.scope_reference,
                "expectedVersion": command.expected_version,
            }
        )
        replay = _replay(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind="UpdateApplicationDeploymentContext",
            request_fingerprint=fingerprint,
            load=self._catalogue.get_application_deployment,
        )
        if replay is not None:
            return replay
        current = self._catalogue.get_application_deployment(command.application_deployment_id)
        if current is None:
            return TargetMetadataMutationResult(TargetMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return TargetMetadataMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        try:
            updated = current.changed_context(
                company_reference=command.company_reference,
                environment=command.environment,
                scope_reference=command.scope_reference,
            )
        except CatalogueInvariantError:
            return TargetMetadataMutationResult(TargetMutationOutcome.INPUT_INVALID)
        try:
            self._catalogue.save_application_deployment(
                updated,
                expected_version=command.expected_version,
            )
        except CatalogueConcurrencyConflict:
            return TargetMetadataMutationResult(TargetMutationOutcome.CONCURRENCY_CONFLICT)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind="UpdateApplicationDeploymentContext",
                request_fingerprint=fingerprint,
                result_id=updated.application_deployment_id,
                result_version=updated.version,
            ),
        )
        commit_outcome = _commit(self._catalogue)
        if commit_outcome is not None:
            return TargetMetadataMutationResult(commit_outcome)
        return TargetMetadataMutationResult(TargetMutationOutcome.UPDATED, updated)
