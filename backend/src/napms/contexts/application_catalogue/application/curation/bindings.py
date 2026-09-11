from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json
from typing import Protocol
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCommandReceipt,
    ApplicationCatalogueCurationAuthorityPort,
    CatalogueConcurrencyConflict,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
    CatalogueMutationOutcome,
)
from napms.contexts.application_catalogue.domain.model import (
    CatalogueInvariantError,
    CatalogueLifecycleState,
    ComponentDeployment,
    DeploymentResourceBinding,
)


_CREATE_BINDING = "CreateDeploymentResourceBinding"
_END_BINDING = "EndDeploymentResourceBinding"


class BindingTargetOutcome(str, Enum):
    ACTIVE = "Active"
    MISSING = "Missing"
    INACTIVE = "Inactive"
    UNKNOWN = "Unknown"


class DeploymentBindingResourceTargetPort(Protocol):
    def check_target(
        self,
        *,
        resource_reference: str,
        effective_time: datetime,
    ) -> BindingTargetOutcome: ...


class DeploymentBindingIdentityFactory(Protocol):
    def new_binding_reference(self) -> str: ...


class DeploymentBindingProvenanceFactory(Protocol):
    def for_binding(
        self,
        *,
        binding_reference: str,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_binding_end(
        self,
        *,
        binding_reference: str,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...


class DeploymentBindingCurationRepository(Protocol):
    def get_component_deployment(
        self,
        deployment_id: UUID,
    ) -> ComponentDeployment | None: ...

    def get_binding(self, reference_id: str) -> DeploymentResourceBinding | None: ...

    def find_overlapping_bindings(
        self,
        *,
        component_deployment_id: UUID,
        resource_reference: str,
        valid_from: datetime,
        valid_to: datetime | None,
    ) -> tuple[DeploymentResourceBinding, ...]: ...

    def add_binding(self, binding: DeploymentResourceBinding) -> None: ...

    def save_binding(
        self,
        binding: DeploymentResourceBinding,
        *,
        expected_version: int,
    ) -> None: ...

    def find_command_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
    ) -> ApplicationCatalogueCommandReceipt | None: ...

    def record_command_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        receipt: ApplicationCatalogueCommandReceipt,
    ) -> None: ...

    def commit(self) -> None: ...


@dataclass(frozen=True, slots=True)
class CreateDeploymentResourceBindingCommand:
    component_deployment_id: UUID
    resource_reference: str
    valid_from: datetime
    valid_to: datetime | None
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class EndDeploymentResourceBindingCommand:
    binding_reference: str
    valid_to: datetime
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class DeploymentBindingMutationResult:
    outcome: CatalogueMutationOutcome
    binding: DeploymentResourceBinding | None = None
    result_version: int | None = None


def _required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def _aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def _valid_interval(valid_from: datetime, valid_to: datetime | None) -> bool:
    if not _aware(valid_from):
        return False
    if valid_to is None:
        return True
    return _aware(valid_to) and valid_from < valid_to


def _fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def _resolve_receipt(
    *,
    repository: DeploymentBindingCurationRepository,
    actor_id: str,
    idempotency_key: str,
    command_kind: str,
    request_fingerprint: str,
) -> DeploymentBindingMutationResult | None:
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
        return DeploymentBindingMutationResult(
            CatalogueMutationOutcome.IDEMPOTENCY_CONFLICT
        )
    binding = repository.get_binding(str(receipt.result_id))
    if binding is None:
        return DeploymentBindingMutationResult(
            CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
        )
    return DeploymentBindingMutationResult(
        CatalogueMutationOutcome.RESOLVED,
        binding=binding,
        result_version=receipt.result_version,
    )


def _authority_failure(check):
    if check.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
        return CatalogueMutationOutcome.AUTHORITY_DENIED
    if (
        check.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
        or check.authority_reference is None
    ):
        return CatalogueMutationOutcome.AUTHORITY_UNKNOWN
    return None


class CreateDeploymentResourceBinding:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: DeploymentBindingCurationRepository,
        resources: DeploymentBindingResourceTargetPort,
        identities: DeploymentBindingIdentityFactory,
        provenance: DeploymentBindingProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._resources = resources
        self._identities = identities
        self._provenance = provenance

    def execute(
        self,
        command: CreateDeploymentResourceBindingCommand,
    ) -> DeploymentBindingMutationResult:
        check = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        authority_failure = _authority_failure(check)
        if authority_failure is not None:
            return DeploymentBindingMutationResult(authority_failure)

        resource_reference = _required(command.resource_reference)
        idempotency_key = _required(command.idempotency_key)
        if (
            resource_reference is None
            or idempotency_key is None
            or not _valid_interval(command.valid_from, command.valid_to)
        ):
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        request_fingerprint = _fingerprint(
            {
                "componentDeploymentId": str(command.component_deployment_id),
                "resourceReference": resource_reference,
                "validFrom": command.valid_from.isoformat(),
                "validTo": command.valid_to.isoformat() if command.valid_to else None,
            }
        )
        replay = _resolve_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_CREATE_BINDING,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        deployment = self._catalogue.get_component_deployment(
            command.component_deployment_id
        )
        if deployment is None:
            return DeploymentBindingMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if deployment.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.PARENT_INACTIVE
            )

        target = self._resources.check_target(
            resource_reference=resource_reference,
            effective_time=command.effective_time,
        )
        if target is BindingTargetOutcome.MISSING:
            return DeploymentBindingMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if target is BindingTargetOutcome.INACTIVE:
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.PARENT_INACTIVE
            )
        if target is not BindingTargetOutcome.ACTIVE:
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )

        if self._catalogue.find_overlapping_bindings(
            component_deployment_id=deployment.deployment_id,
            resource_reference=resource_reference,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
        ):
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        binding_reference = self._identities.new_binding_reference()
        provenance_reference = self._provenance.for_binding(
            binding_reference=binding_reference,
            actor_id=command.actor_id,
            authority_reference=check.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            binding = DeploymentResourceBinding(
                reference_id=binding_reference,
                component_deployment_id=deployment.deployment_id,
                resource_reference=resource_reference,
                valid_from=command.valid_from,
                valid_to=command.valid_to,
                provenance_reference=provenance_reference,
            )
        except CatalogueInvariantError:
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        self._catalogue.add_binding(binding)
        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_CREATE_BINDING,
                request_fingerprint=request_fingerprint,
                result_id=binding.reference_id,  # type: ignore[arg-type]
                result_version=binding.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_CREATE_BINDING,
                request_fingerprint=request_fingerprint,
            )
            return replay or DeploymentBindingMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )

        return DeploymentBindingMutationResult(
            CatalogueMutationOutcome.CREATED,
            binding=binding,
            result_version=binding.version,
        )


class EndDeploymentResourceBinding:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        catalogue: DeploymentBindingCurationRepository,
        provenance: DeploymentBindingProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._provenance = provenance

    def execute(
        self,
        command: EndDeploymentResourceBindingCommand,
    ) -> DeploymentBindingMutationResult:
        check = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        authority_failure = _authority_failure(check)
        if authority_failure is not None:
            return DeploymentBindingMutationResult(authority_failure)

        binding_reference = _required(command.binding_reference)
        idempotency_key = _required(command.idempotency_key)
        if (
            binding_reference is None
            or idempotency_key is None
            or command.expected_version < 1
            or not _aware(command.valid_to)
        ):
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        request_fingerprint = _fingerprint(
            {
                "bindingReference": binding_reference,
                "validTo": command.valid_to.isoformat(),
                "expectedVersion": command.expected_version,
            }
        )
        replay = _resolve_receipt(
            repository=self._catalogue,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_END_BINDING,
            request_fingerprint=request_fingerprint,
        )
        if replay is not None:
            return replay

        current = self._catalogue.get_binding(binding_reference)
        if current is None:
            return DeploymentBindingMutationResult(CatalogueMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.CONCURRENCY_CONFLICT
            )

        end_provenance = self._provenance.for_binding_end(
            binding_reference=binding_reference,
            actor_id=command.actor_id,
            authority_reference=check.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            ended = current.ended(
                valid_to=command.valid_to,
                end_provenance_reference=end_provenance,
            )
        except CatalogueInvariantError:
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.INPUT_INVALID
            )

        try:
            self._catalogue.save_binding(
                ended,
                expected_version=command.expected_version,
            )
        except CatalogueConcurrencyConflict:
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.CONCURRENCY_CONFLICT
            )

        self._catalogue.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_END_BINDING,
                request_fingerprint=request_fingerprint,
                result_id=ended.reference_id,  # type: ignore[arg-type]
                result_version=ended.version,
            ),
        )
        try:
            self._catalogue.commit()
        except CatalogueIdempotencyConflict:
            replay = _resolve_receipt(
                repository=self._catalogue,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_END_BINDING,
                request_fingerprint=request_fingerprint,
            )
            return replay or DeploymentBindingMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return DeploymentBindingMutationResult(
                CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
            )

        return DeploymentBindingMutationResult(
            CatalogueMutationOutcome.UPDATED,
            binding=ended,
            result_version=ended.version,
        )
