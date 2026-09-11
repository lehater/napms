from napms.contexts.access_policy.application.ports import (
    AccessRuleReadScopeOptions,
    AuthorityAction,
    AuthorityCheck,
    EffectivePolicyReadScopeOptions,
    ProposalScopeOptions,
    TernaryOutcome,
)
from napms.contexts.authority_management.application.check_authority import (
    AuthorityOutcome,
    CheckAuthority,
)
from napms.contexts.authority_management.application.list_scopes import (
    ListEffectiveAuthorityScopes,
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


class AccessPolicyProposalScopeAdapter:
    """Translate actor proposal-scope discovery to the Access Policy consumer contract."""

    def __init__(self, *, discovery: ListEffectiveAuthorityScopes) -> None:
        self._discovery = discovery

    def list_effective_proposal_scopes(
        self,
        *,
        actor_id: str,
        effective_time,
    ) -> ProposalScopeOptions:
        result = self._discovery.execute(
            actor_id=actor_id,
            action=AuthorityAction.PROPOSE_CONNECTIVITY.value,
            effective_time=effective_time,
        )
        return ProposalScopeOptions(
            permitted_scopes=result.permitted_scopes,
            ambiguous_scopes=result.ambiguous_scopes,
        )


class AccessPolicyRuleReadScopeAdapter:
    """Translate ReadAccessRule scope discovery to the Access Policy consumer contract."""

    def __init__(self, *, discovery: ListEffectiveAuthorityScopes) -> None:
        self._discovery = discovery

    def list_effective_read_rule_scopes(
        self,
        *,
        actor_id: str,
        effective_time,
    ) -> AccessRuleReadScopeOptions:
        result = self._discovery.execute(
            actor_id=actor_id,
            action=AuthorityAction.READ_ACCESS_RULE.value,
            effective_time=effective_time,
        )
        return AccessRuleReadScopeOptions(
            permitted_scopes=result.permitted_scopes,
            ambiguous_scopes=result.ambiguous_scopes,
        )


class AccessPolicyEffectivePolicyReadScopeAdapter:
    """Translate ReadEffectiveDesiredPolicy scope discovery to Access Policy."""

    def __init__(self, *, discovery: ListEffectiveAuthorityScopes) -> None:
        self._discovery = discovery

    def list_effective_policy_read_scopes(
        self,
        *,
        actor_id: str,
        effective_time,
    ) -> EffectivePolicyReadScopeOptions:
        result = self._discovery.execute(
            actor_id=actor_id,
            action=AuthorityAction.READ_EFFECTIVE_DESIRED_POLICY.value,
            effective_time=effective_time,
        )
        return EffectivePolicyReadScopeOptions(
            permitted_scopes=result.permitted_scopes,
            ambiguous_scopes=result.ambiguous_scopes,
        )
