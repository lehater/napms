from napms.contexts.authority_management.application.check_authority import AuthorityOutcome, CheckAuthority
from napms.contexts.authority_management.application.ports import AuthorityPersistenceError
from napms.network_operator_view.application import AuthorityResult

_ACTION = "ReadNetworkOperatorRealization"


class AuthorityManagementNetworkOperatorViewAdapter:
    def __init__(self, *, checker: CheckAuthority) -> None:
        self._checker = checker

    def check(self, *, actor_id, scope, as_of) -> AuthorityResult:
        try:
            result = self._checker.execute(
                actor_id=actor_id,
                action=_ACTION,
                scope=scope,
                effective_time=as_of,
            )
        except AuthorityPersistenceError:
            return AuthorityResult(None)

        if result.outcome is AuthorityOutcome.PERMITTED:
            if not result.authority_reference:
                return AuthorityResult(None)
            return AuthorityResult(True, result.authority_reference)
        if result.outcome is AuthorityOutcome.DENIED:
            return AuthorityResult(False)
        return AuthorityResult(None)
