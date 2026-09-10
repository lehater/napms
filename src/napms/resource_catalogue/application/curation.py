from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json

from napms.resource_catalogue.application.ports import (
    ResourceCatalogueAuthorityOutcome,
    ResourceCatalogueCommandReceipt,
    ResourceCatalogueCurationAuthorityPort,
    ResourceCatalogueCurationRepository,
    ResourceCatalogueIdentityFactory,
    ResourceCatalogueProvenanceFactory,
)
from napms.resource_catalogue.domain.model import Resource, ResourceCatalogueInvariantError


_CREATE_RESOURCE = "CreateResource"


class CreateResourceOutcome(str, Enum):
    CREATED = "Created"
    RESOLVED = "Resolved"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    INPUT_INVALID = "InputInvalid"
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


def _normalize_optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def _normalize_required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def _fingerprint(*, display_name: str | None) -> str:
    payload = json.dumps(
        {"displayName": display_name},
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


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

    def execute(self, command: CreateResourceCommand) -> CreateResourceResult:
        authority = self._authority.check_curation(
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

        fingerprint = _fingerprint(display_name=display_name)
        receipt = self._resources.find_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is not None:
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
        self._resources.commit()

        return CreateResourceResult(
            CreateResourceOutcome.CREATED,
            resource=resource,
        )
