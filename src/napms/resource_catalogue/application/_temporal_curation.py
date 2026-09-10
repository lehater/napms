from datetime import datetime
from enum import Enum
from hashlib import sha256
import json


class TemporalCurationOutcome(str, Enum):
    CREATED = "Created"
    UPDATED = "Updated"
    RESOLVED = "Resolved"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    NOT_FOUND = "NotFound"
    RESOURCE_INACTIVE = "ResourceInactive"
    INPUT_INVALID = "InputInvalid"
    OVERLAP_CONFLICT = "OverlapConflict"
    CONCURRENCY_CONFLICT = "ConcurrencyConflict"
    IDEMPOTENCY_CONFLICT = "IdempotencyConflict"
    PERSISTENCE_UNKNOWN = "PersistenceUnknown"


def required(value: str) -> str | None:
    normalized = value.strip() if value else ""
    return normalized or None


def optional(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None


def instant(value: datetime | None) -> str | None:
    return value.isoformat() if value is not None else None


def fingerprint(payload: dict[str, object]) -> str:
    encoded = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    return sha256(encoded).hexdigest()


def is_aware(value: datetime) -> bool:
    return value.tzinfo is not None and value.utcoffset() is not None


def valid_interval(valid_from: datetime, valid_to: datetime | None) -> bool:
    if not is_aware(valid_from):
        return False
    if valid_to is None:
        return True
    return is_aware(valid_to) and valid_from < valid_to
