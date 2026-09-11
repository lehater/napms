from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from napms.contexts.authority_management.application.ports import (
    AuthorityAssignmentRepository,
)


class AuthorityOutcome(str, Enum):
    PERMITTED = "Permitted"
    DENIED = "Denied"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class AuthorityDecision:
    outcome: AuthorityOutcome
    authority_reference: str | None = None
    provenance_reference: str | None = None


class CheckAuthority:
    def __init__(self, *, assignments: AuthorityAssignmentRepository) -> None:
        self._assignments = assignments

    def execute(
        self,
        *,
        actor_id: str,
        action: str,
        scope: str,
        effective_time: datetime,
    ) -> AuthorityDecision:
        matches = self._assignments.find_effective(
            actor_id=actor_id,
            action=action,
            scope=scope,
            effective_time=effective_time,
        )
        if not matches:
            return AuthorityDecision(AuthorityOutcome.DENIED)
        if len(matches) != 1:
            return AuthorityDecision(AuthorityOutcome.UNKNOWN)

        assignment = matches[0]
        if not assignment.is_effective_at(effective_time):
            return AuthorityDecision(AuthorityOutcome.UNKNOWN)

        return AuthorityDecision(
            AuthorityOutcome.PERMITTED,
            authority_reference=assignment.reference_id,
            provenance_reference=assignment.provenance_reference,
        )
