from napms.authority_management.application.check_authority import (
    AuthorityOutcome,
    CheckAuthority,
)
from napms.authority_management.application.list_scopes import (
    ListEffectiveAuthorityScopes,
)
from napms.contexts.connectivity_requirements.application.ports import (
    RequirementAuthorityAction,
    RequirementAuthorityCheck,
    RequirementScopeOptions,
    TernaryOutcome,
)


class ConnectivityRequirementsAuthorityAdapter:
    def __init__(self, *, checker: CheckAuthority) -> None:
        self._checker = checker

    def check(
        self,
        *,
        actor_id: str,
        action: RequirementAuthorityAction,
        scope: str,
        effective_time,
    ) -> RequirementAuthorityCheck:
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
        return RequirementAuthorityCheck(
            outcome=outcome,
            authority_reference=(
                decision.authority_reference
                if decision.outcome is AuthorityOutcome.PERMITTED
                else None
            ),
        )


class ConnectivityRequirementsDeclarationScopeAdapter:
    def __init__(self, *, discovery: ListEffectiveAuthorityScopes) -> None:
        self._discovery = discovery

    def list_effective_declaration_scopes(
        self,
        *,
        actor_id: str,
        effective_time,
    ) -> RequirementScopeOptions:
        result = self._discovery.execute(
            actor_id=actor_id,
            action=RequirementAuthorityAction.DECLARE.value,
            effective_time=effective_time,
        )
        return RequirementScopeOptions(
            permitted_scopes=result.permitted_scopes,
            ambiguous_scopes=result.ambiguous_scopes,
        )


class ConnectivityRequirementsReadScopeAdapter:
    def __init__(self, *, discovery: ListEffectiveAuthorityScopes) -> None:
        self._discovery = discovery

    def list_effective_read_scopes(
        self,
        *,
        actor_id: str,
        effective_time,
    ) -> RequirementScopeOptions:
        result = self._discovery.execute(
            actor_id=actor_id,
            action=RequirementAuthorityAction.READ.value,
            effective_time=effective_time,
        )
        return RequirementScopeOptions(
            permitted_scopes=result.permitted_scopes,
            ambiguous_scopes=result.ambiguous_scopes,
        )
