from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from hashlib import sha256
import json

from napms.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCommandReceipt,
    ApplicationCatalogueCurationAuthorityPort,
    ApplicationCatalogueCurationRepository,
    ApplicationCatalogueIdentityFactory,
    ApplicationCatalogueProvenanceFactory,
    CatalogueIdempotencyConflict,
    CataloguePersistenceOutcomeUnknown,
)
from napms.application_catalogue.domain.model import Application, CatalogueInvariantError


_CREATE_APPLICATION = "CreateApplication"


class CreateApplicationOutcome(str, Enum):
    CREATED = "Created"
    RESOLVED = "Resolved"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    INPUT_INVALID = "InputInvalid"
    IDEMPOTENCY_CONFLICT = "IdempotencyConflict"
    PERSISTENCE_UNKNOWN = "PersistenceUnknown"


@dataclass(frozen=True, slots=True)
class CreateApplicationCommand:
    display_name: str
    actor_id: str
    effective_time: datetime
    idempotency_key: str
    description: str | None = None
    domain: str | None = None
    owner_reference: str | None = None


@dataclass(frozen=True, slots=True)
class CreateApplicationResult:
    outcome: CreateApplicationOutcome
    application: Application | None = None


def _normalize_required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def _normalize_optional(value: str | None) -> tuple[str | None, bool]:
    if value is None:
        return None, True
    normalized = value.strip()
    return (normalized or None), bool(normalized)


def _fingerprint(
    *,
    display_name: str,
    description: str | None,
    domain: str | None,
    owner_reference: str | None,
) -> str:
    # Keep the pre-I31 fingerprint byte-for-byte compatible when target metadata
    # is absent so an old create retry still resolves its persisted receipt.
    document: dict[str, object] = {"displayName": display_name}
    if description is not None:
        document["description"] = description
    if domain is not None:
        document["domain"] = domain
    if owner_reference is not None:
        document["ownerReference"] = owner_reference
    payload = json.dumps(
        document,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(payload).hexdigest()


class CreateApplication:
    def __init__(
        self,
        *,
        authority: ApplicationCatalogueCurationAuthorityPort,
        applications: ApplicationCatalogueCurationRepository,
        identities: ApplicationCatalogueIdentityFactory,
        provenance: ApplicationCatalogueProvenanceFactory,
    ) -> None:
        self._authority = authority
        self._applications = applications
        self._identities = identities
        self._provenance = provenance

    def _resolve_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        fingerprint: str,
    ) -> CreateApplicationResult | None:
        receipt = self._applications.find_command_receipt(
            actor_id=actor_id,
            idempotency_key=idempotency_key,
        )
        if receipt is None:
            return None
        if (
            receipt.command_kind != _CREATE_APPLICATION
            or receipt.request_fingerprint != fingerprint
        ):
            return CreateApplicationResult(CreateApplicationOutcome.IDEMPOTENCY_CONFLICT)
        existing = self._applications.get_application(receipt.result_id)
        if existing is None:
            return CreateApplicationResult(CreateApplicationOutcome.PERSISTENCE_UNKNOWN)
        return CreateApplicationResult(
            CreateApplicationOutcome.RESOLVED,
            application=existing,
        )

    def execute(self, command: CreateApplicationCommand) -> CreateApplicationResult:
        authority = self._authority.check_curation(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
        )
        if authority.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
            return CreateApplicationResult(CreateApplicationOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return CreateApplicationResult(CreateApplicationOutcome.AUTHORITY_UNKNOWN)

        display_name = _normalize_required(command.display_name)
        idempotency_key = _normalize_required(command.idempotency_key)
        description, description_valid = _normalize_optional(command.description)
        domain, domain_valid = _normalize_optional(command.domain)
        owner_reference, owner_valid = _normalize_optional(command.owner_reference)
        if (
            display_name is None
            or idempotency_key is None
            or not description_valid
            or not domain_valid
            or not owner_valid
        ):
            return CreateApplicationResult(CreateApplicationOutcome.INPUT_INVALID)

        fingerprint = _fingerprint(
            display_name=display_name,
            description=description,
            domain=domain,
            owner_reference=owner_reference,
        )
        replay = self._resolve_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            fingerprint=fingerprint,
        )
        if replay is not None:
            return replay

        application_id = self._identities.new_application_id()
        provenance_reference = self._provenance.for_application(
            application_id=application_id,
            actor_id=command.actor_id,
            authority_reference=authority.authority_reference,
            effective_time=command.effective_time,
        )
        try:
            application = Application(
                application_id=application_id,
                display_name=display_name,
                provenance_reference=provenance_reference,
                description=description,
                domain=domain,
                owner_reference=owner_reference,
            )
        except CatalogueInvariantError:
            return CreateApplicationResult(CreateApplicationOutcome.INPUT_INVALID)

        self._applications.add_application(application)
        self._applications.record_command_receipt(
            actor_id=command.actor_id,
            idempotency_key=idempotency_key,
            receipt=ApplicationCatalogueCommandReceipt(
                command_kind=_CREATE_APPLICATION,
                request_fingerprint=fingerprint,
                result_id=application.application_id,
                result_version=application.version,
            ),
        )
        try:
            self._applications.commit()
        except CatalogueIdempotencyConflict:
            replay = self._resolve_receipt(
                actor_id=command.actor_id,
                idempotency_key=idempotency_key,
                fingerprint=fingerprint,
            )
            return replay or CreateApplicationResult(
                CreateApplicationOutcome.PERSISTENCE_UNKNOWN
            )
        except CataloguePersistenceOutcomeUnknown:
            return CreateApplicationResult(CreateApplicationOutcome.PERSISTENCE_UNKNOWN)

        return CreateApplicationResult(
            CreateApplicationOutcome.CREATED,
            application=application,
        )
