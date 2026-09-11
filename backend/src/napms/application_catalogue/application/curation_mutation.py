from datetime import datetime
from enum import Enum
from hashlib import sha256
import json

from napms.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
    ApplicationCatalogueCurationAuthorityPort,
)


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


def required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def authorize(
    authority: ApplicationCatalogueCurationAuthorityPort,
    *,
    actor_id: str,
    effective_time: datetime,
) -> ApplicationCatalogueAuthorityCheck:
    return authority.check_curation(
        actor_id=actor_id,
        effective_time=effective_time,
    )


def authority_failure(
    check: ApplicationCatalogueAuthorityCheck,
) -> CatalogueMutationOutcome | None:
    if check.outcome is ApplicationCatalogueAuthorityOutcome.DENIED:
        return CatalogueMutationOutcome.AUTHORITY_DENIED
    if (
        check.outcome is not ApplicationCatalogueAuthorityOutcome.PERMITTED
        or check.authority_reference is None
    ):
        return CatalogueMutationOutcome.AUTHORITY_UNKNOWN
    return None
