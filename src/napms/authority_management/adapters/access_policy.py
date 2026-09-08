from napms.access_policy.application.ports import (
    AuthorityAction,
    AuthorityCheck,
    TernaryOutcome,
)
from napms.authority_management.application.check_authority import (
    AuthorityOutcome,
    CheckAuthority,
)


class AccessPolicyAuthorityAdapter:
    """Translate the Authority Management application contract to Access Policy."""

    def __init__(self, *, checker: CheckAuthority) -> None:
        self._checker = checker

    def check(
        self,
        *,
        actor_id: str,
        action: AuthorityAction,
        scope: str,
        effective_time,
    ) -> AuthorityCheck:
        decision = self._checker.execute(
            actor_id=actor_id,
            action=action.value,
            scope=scope,
            effective_time=effective_time,
        )
        outcome = {
            AuthorityOutcome.PERMITTED: TernaryOutcome.PERMITTED,
            AuthorityOutcome.DENIED: TernaryOutcome.DENIED,
            AuthorityOutcome.UNKNOWN: TernaryOutcome.UNKNOWN,
        }[decision.outcome]
        return AuthorityCheck(
            outcome=outcome,
            authority_reference=(
                decision.authority_reference
                if decision.outcome is AuthorityOutcome.PERMITTED
                else None
            ),
        )
