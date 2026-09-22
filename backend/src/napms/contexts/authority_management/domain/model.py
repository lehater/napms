from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class AuthorityGrant:
    action: str
    scope: str
    effective_from: datetime | None = None
    effective_until: datetime | None = None

    def is_effective(self, *, action: str, scope: str, evaluated_at: datetime) -> bool:
        if self.action != action or self.scope != scope:
            return False
        if self.effective_from is not None and evaluated_at < self.effective_from:
            return False
        if self.effective_until is not None and evaluated_at >= self.effective_until:
            return False
        return True


@dataclass(frozen=True)
class Principal:
    subject: str
    instance_permissions: frozenset[str] = frozenset()
    authority_grants: tuple[AuthorityGrant, ...] = ()

    def __post_init__(self) -> None:
        if not self.subject.strip():
            raise ValueError("principal subject must be non-empty")


@dataclass(frozen=True)
class AuthorityEvidence:
    action: str
    scope: str
    evaluated_at: datetime
    effective_from: datetime | None
    effective_until: datetime | None
