from dataclasses import dataclass
from datetime import datetime


class AuthorityInvariantError(Exception):
    """Raised when Authority Management state is structurally invalid."""


def _require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AuthorityInvariantError(f"{field_name} must be offset-aware")


@dataclass(frozen=True, slots=True)
class AuthorityAssignment:
    reference_id: str
    actor_id: str
    action: str
    scope: str
    valid_from: datetime
    valid_to: datetime | None
    provenance_reference: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("reference_id", self.reference_id),
            ("actor_id", self.actor_id),
            ("action", self.action),
            ("scope", self.scope),
            ("provenance_reference", self.provenance_reference),
        ):
            if not value:
                raise AuthorityInvariantError(f"{field_name} must be non-empty")

        _require_aware(self.valid_from, field_name="valid_from")
        if self.valid_to is not None:
            _require_aware(self.valid_to, field_name="valid_to")
            if self.valid_from >= self.valid_to:
                raise AuthorityInvariantError("valid_from must be before valid_to")

    def is_effective_at(self, effective_time: datetime) -> bool:
        _require_aware(effective_time, field_name="effective_time")
        return self.valid_from <= effective_time and (
            self.valid_to is None or effective_time < self.valid_to
        )
