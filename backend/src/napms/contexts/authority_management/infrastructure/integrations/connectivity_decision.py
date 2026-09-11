from napms.contexts.authority_management.application.check_authority import (
    AuthorityOutcome,
    CheckAuthority,
)
from napms.contexts.authority_management.application.list_scopes import (
    ListEffectiveAuthorityScopes,
)
from napms.contexts.connectivity_decision.application.ports import (
    DecisionAuthorityAction,
    DecisionAuthorityCheck,
    DecisionScopeOptions,
    TernaryOutcome,
)


class ConnectivityDecisionAuthorityAdapter:
    def __init__(self, *, checker: CheckAuthority) -> None:
        self._checker = checker

    def check(
        self,
        *,
        actor_id: str,
        action: DecisionAuthorityAction,
        scope: str,
        effective_time,
    ) -> DecisionAuthorityCheck:
        result = self._checker.execute(
            actor_id=actor_id,
            action=action.value,
            scope=scope,
            effective_time=effective_time,
        )
        outcome = {
            AuthorityOutcome.PERMITTED: TernaryOutcome.PERMITTED,
            AuthorityOutcome.DENIED: TernaryOutcome.DENIED,
            AuthorityOutcome.UNKNOWN: TernaryOutcome.UNKNOWN,
        }[result.outcome]
        return DecisionAuthorityCheck(
            outcome=outcome,
            authority_reference=(
                result.authority_reference
                if result.outcome is AuthorityOutcome.PERMITTED
                else None
            ),
        )


class ConnectivityDecisionScopeAdapter:
    def __init__(self, *, discovery: ListEffectiveAuthorityScopes) -> None:
        self._discovery = discovery

    def list_effective_decision_scopes(
        self,
        *,
        actor_id: str,
        effective_time,
    ) -> DecisionScopeOptions:
        result = self._discovery.execute(
            actor_id=actor_id,
            action=DecisionAuthorityAction.DECIDE.value,
            effective_time=effective_time,
        )
        return DecisionScopeOptions(
            permitted_scopes=result.permitted_scopes,
            ambiguous_scopes=result.ambiguous_scopes,
        )


class ConnectivityDecisionReadScopeAdapter:
    def __init__(self, *, discovery: ListEffectiveAuthorityScopes) -> None:
        self._discovery = discovery

    def list_effective_decision_read_scopes(
        self,
        *,
        actor_id: str,
        effective_time,
    ) -> DecisionScopeOptions:
        result = self._discovery.execute(
            actor_id=actor_id,
            action=DecisionAuthorityAction.READ.value,
            effective_time=effective_time,
        )
        return DecisionScopeOptions(
            permitted_scopes=result.permitted_scopes,
            ambiguous_scopes=result.ambiguous_scopes,
        )
