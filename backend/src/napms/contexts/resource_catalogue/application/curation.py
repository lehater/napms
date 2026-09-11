from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json

from napms.contexts.resource_catalogue.application.ports import (
    ResourceCatalogueAuthorityCheck,
    ResourceCatalogueAuthorityOutcome,
    ResourceCatalogueCommandReceipt,
    ResourceCatalogueConcurrencyConflict,
    ResourceCatalogueCurationAuthorityPort,
    ResourceCatalogueCurationRepository,
    ResourceCatalogueIdempotencyConflict,
    ResourceCatalogueIdentityFactory,
    ResourceCataloguePersistenceOutcomeUnknown,
    ResourceCatalogueProvenanceFactory,
)
from napms.contexts.resource_catalogue.domain.model import Resource, ResourceCatalogueInvariantError


_CREATE_RESOURCE = "CreateResource"
_RENAME_RESOURCE = "RenameResource"
_RETIRE_RESOURCE = "RetireResource"


class CreateResourceOutcome(str, Enum):
    CREATED = "Created"
    RESOLVED = "Resolved"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    INPUT_INVALID = "InputInvalid"
    IDEMPOTENCY_CONFLICT = "IdempotencyConflict"
    PERSISTENCE_UNKNOWN = "PersistenceUnknown"


class ResourceMutationOutcome(str, Enum):
    UPDATED = "Updated"
    RESOLVED = "Resolved"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    NOT_FOUND = "NotFound"
    INPUT_INVALID = "InputInvalid"
    CONCURRENCY_CONFLICT = "ConcurrencyConflict"
    RETIREMENT_BLOCKED = "RetirementBlocked"
    IDEMPOTENCY_CONFLICT = "IdempotencyConflict"
    PERSISTENCE_UNKNOWN = "PersistenceUnknown"


@dataclass(frozen=True, slots=True)
class CreateResourceCommand:
    display_name: str | None
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class CreateResourceResult:
    outcome: CreateResourceOutcome
    resource: Resource | None = None


@dataclass(frozen=True, slots=True)
class RenameResourceCommand:
    resource_reference: str
    display_name: str
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class RetireResourceCommand:
    resource_reference: str
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class ResourceMutationResult:
    outcome: ResourceMutationOutcome
    resource: Resource | None = None
    result_version: int | None = None


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_required(value: str) -> str | None:
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
    *,
    authority: ResourceCatalogueCurationAuthorityPort,
    actor_id: str,
    effective_time: datetime,
) -> ResourceCatalogueAuthorityCheck:
    return authority.check_curation(
        actor_id=actor_id,
        effective_time=effective_time,
    )


def _resolve_mutation_receipt(
    *,
    resources: ResourceCatalogueCurationRepository,
    actor_id: str,
    idempotency_key: str,
    command_kind: str,
    fingerprint: str,
) -> ResourceMutationResult | None:
    receipt = resources.find_command_receipt(
        actor_id=actor_id,
        idempotency_key=idempotency_key,
    )
    if receipt is None:
        return None
    if (
        receipt.command_kind != command_kind
        or receipt.request_fingerprint != fingerprint
    ):
        return ResourceMutationResult(ResourceMutationOutcome.IDEMPOTENCY_CONFLICT)
    current = resources.get_resource(receipt.result_reference)
    if current is None:
        return ResourceMutationResult(ResourceMutationOutcome.PERSISTENCE_UNKNOWN)
    return ResourceMutationResult(
        ResourceMutationOutcome.RESOLVED,
        resource=current,
        result_version=receipt.result_version,
    )


class CreateResource:
    def __init__(
        self,
        *,
        authority: ResourceCatalogueCurationAuthorityPort,
        resources: ResourceCatalogueCurationRepository,
        identities: ResourceCatalogueIdentityFactory,
        provenance: ResourceCatalogueProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._resources = resources
        self._identities = identities
        self._provenance = provenance

    def _resolve_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        fingerprint: str,
    ) -> CreateResourceResult | None:
        receipt = self._resources.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _CREATE_RESOURCE
            or receipt.request_fingerprint != fingerprint
        ):
            return CreateResourceResult(CreateResourceOutcome.IDEMPOTENCY_CONFLICT)
        existing = self._resources.get_resource(receipt.result_reference)
        if existing is None:
            return CreateResourceResult(CreateResourceOutcome.PERSISTENCE_UNKNOWN)
        return CreateResourceResult(
            CreateResourceOutcome.RESOLVED,
            resource=existing,
        )

    def execute(self, command: CreateResourceCommand) -> CreateResourceResult:
        authority = _authorize(
            authority=self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ResourceCatalogueAuthorityOutcome.DENIED:
            return CreateResourceResult(CreateResourceOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not ResourceCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return CreateResourceResult(CreateResourceOutcome.AUTHORITY_UNKNOWN)

        idempotency_key = _normalize_required(command.idempotency_key)
        if idempotency_key is None:
            return CreateResourceResult(CreateResourceOutcome.INPUT_INVALID)

        display_name = _normalize_optional(command.display_name)
        if command.display_name is not None and display_name is None:
            return CreateResourceResult(CreateResourceOutcome.INPUT_INVALID)

        fingerprint = _fingerprint({"displayName": display_name})
        replay = self._resolve_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )
        if replay is not None:
            return replay

        resource_reference = self._identities.new_resource_reference()
        provenance_reference = self._provenance.for_resource(
            resource_reference=resource_reference,
            actor_id=command.actor_id,
            authority_reference=authority.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            resource = Resource(
                resource_reference=resource_reference,
                display_name=display_name,
                provenance_reference=provenance_reference,
            )
        except ResourceCatalogueInvariantError:
            return CreateResourceResult(CreateResourceOutcome.INPUT_INVALID)

        self._resources.add_resource(resource)
        self._resources.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ResourceCatalogueCommandReceipt(
                command_kind=_CREATE_RESOURCE,
                request_fingerprint=fingerprint,
                result_reference=resource.resource_reference,
                result_version=resource.version,
            ),
        )
        try:
            self._resources.commit()
        except ResourceCatalogueIdempotencyConflict:
            replay = self._resolve_receipt(
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                fingerprint=fingerprint,
            )
            return replay or CreateResourceResult(
                CreateResourceOutcome.PERSISTENCE_UNKNOWN
            )
        except ResourceCataloguePersistenceOutcomeUnknown:
            return CreateResourceResult(CreateResourceOutcome.PERSISTENCE_UNKNOWN)

        return CreateResourceResult(
            CreateResourceOutcome.CREATED,
            resource=resource,
        )


class RenameResource:
    def __init__(
        self,
        *,
        authority: ResourceCatalogueCurationAuthorityPort,
        resources: ResourceCatalogueCurationRepository,
    ) -> None:
        self._authority = authority
        self._resources = resources

    def execute(self, command: RenameResourceCommand) -> ResourceMutationResult:
        authority = _authorize(
            authority=self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ResourceCatalogueAuthorityOutcome.DENIED:
            return ResourceMutationResult(ResourceMutationOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not ResourceCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return ResourceMutationResult(ResourceMutationOutcome.AUTHORITY_UNKNOWN)

        resource_reference = _normalize_required(command.resource_reference)
        display_name = _normalize_required(command.display_name)
        idempotency_key = _normalize_required(command.idempotency_key)
        if (
            resource_reference is None
            or display_name is None
            or idempotency_key is None
            or command.expected_version < 1
        ):
            return ResourceMutationResult(ResourceMutationOutcome.INPUT_INVALID)

        fingerprint = _fingerprint(
            {
                "resourceReference": resource_reference,
                "displayName": display_name,
                "expectedVersion": command.expected_version,
            }
        )
        replay = _resolve_mutation_receipt(
            resources=self._resources,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_RENAME_RESOURCE,
            fingerprint=fingerprint,
        )
        if replay is not None:
            return replay

        current = self._resources.get_resource(resource_reference)
        if current is None:
            return ResourceMutationResult(ResourceMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return ResourceMutationResult(ResourceMutationOutcome.CONCURRENCY_CONFLICT)

        try:
            updated = current.renamed(display_name)
        except ResourceCatalogueInvariantError:
            return ResourceMutationResult(ResourceMutationOutcome.INPUT_INVALID)

        try:
            self._resources.save_resource(
                updated,
                expected_version=command.expected_version,
            )
        except ResourceCatalogueConcurrencyConflict:
            return ResourceMutationResult(ResourceMutationOutcome.CONCURRENCY_CONFLICT)

        self._resources.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ResourceCatalogueCommandReceipt(
                command_kind=_RENAME_RESOURCE,
                request_fingerprint=fingerprint,
                result_reference=updated.resource_reference,
                result_version=updated.version,
            ),
        )
        try:
            self._resources.commit()
        except ResourceCatalogueIdempotencyConflict:
            replay = _resolve_mutation_receipt(
                resources=self._resources,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_RENAME_RESOURCE,
                fingerprint=fingerprint,
            )
            return replay or ResourceMutationResult(
                ResourceMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except ResourceCataloguePersistenceOutcomeUnknown:
            return ResourceMutationResult(ResourceMutationOutcome.PERSISTENCE_UNKNOWN)

        return ResourceMutationResult(
            ResourceMutationOutcome.UPDATED,
            resource=updated,
            result_version=updated.version,
        )


class RetireResource:
    def __init__(
        self,
        *,
        authority: ResourceCatalogueCurationAuthorityPort,
        resources: ResourceCatalogueCurationRepository,
        provenance: ResourceCatalogueProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._resources = resources
        self._provenance = provenance

    def execute(self, command: RetireResourceCommand) -> ResourceMutationResult:
        authority = _authorize(
            authority=self._authority,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ResourceCatalogueAuthorityOutcome.DENIED:
            return ResourceMutationResult(ResourceMutationOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not ResourceCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return ResourceMutationResult(ResourceMutationOutcome.AUTHORITY_UNKNOWN)

        resource_reference = _normalize_required(command.resource_reference)
        idempotency_key = _normalize_required(command.idempotency_key)
        if (
            resource_reference is None
            or idempotency_key is None
            or command.expected_version < 1
        ):
            return ResourceMutationResult(ResourceMutationOutcome.INPUT_INVALID)

        fingerprint = _fingerprint(
            {
                "resourceReference": resource_reference,
                "expectedVersion": command.expected_version,
            }
        )
        replay = _resolve_mutation_receipt(
            resources=self._resources,
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            command_kind=_RETIRE_RESOURCE,
            fingerprint=fingerprint,
        )
        if replay is not None:
            return replay

        current = self._resources.get_resource(resource_reference)
        if current is None:
            return ResourceMutationResult(ResourceMutationOutcome.NOT_FOUND)
        if current.version != command.expected_version:
            return ResourceMutationResult(ResourceMutationOutcome.CONCURRENCY_CONFLICT)

        if self._resources.has_effective_scope_affiliations(
            resource_reference=resource_reference,
            as_of=command.effective_time,
        ) or self._resources.has_effective_responsibilities(
            resource_reference=resource_reference,
            as_of=command.effective_time,
        ):
            return ResourceMutationResult(ResourceMutationOutcome.RETIREMENT_BLOCKED)

        retirement_provenance_reference = self._provenance.for_resource_retirement(
            resource_reference=resource_reference,
            actor_id=command.actor_id,
            authority_reference=authority.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            updated = current.retired(
                retirement_provenance_reference=retirement_provenance_reference,
            )
        except ResourceCatalogueInvariantError:
            return ResourceMutationResult(ResourceMutationOutcome.INPUT_INVALID)

        try:
            self._resources.save_resource(
                updated,
                expected_version=command.expected_version,
            )
        except ResourceCatalogueConcurrencyConflict:
            return ResourceMutationResult(ResourceMutationOutcome.CONCURRENCY_CONFLICT)

        self._resources.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ResourceCatalogueCommandReceipt(
                command_kind=_RETIRE_RESOURCE,
                request_fingerprint=fingerprint,
                result_reference=updated.resource_reference,
                result_version=updated.version,
            ),
        )
        try:
            self._resources.commit()
        except ResourceCatalogueIdempotencyConflict:
            replay = _resolve_mutation_receipt(
                resources=self._resources,
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                command_kind=_RETIRE_RESOURCE,
                fingerprint=fingerprint,
            )
            return replay or ResourceMutationResult(
                ResourceMutationOutcome.PERSISTENCE_UNKNOWN
            )
        except ResourceCataloguePersistenceOutcomeUnknown:
            return ResourceMutationResult(ResourceMutationOutcome.PERSISTENCE_UNKNOWN)

        return ResourceMutationResult(
            ResourceMutationOutcome.UPDATED,
            resource=updated,
            result_version=updated.version,
        )
