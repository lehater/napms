from napms.contexts.authority_management.application.check_authority import (
    AuthorityOutcome,
    CheckAuthority,
)
from napms.contexts.authority_management.application.list_scopes import (
    ListEffectiveAuthorityScopes,
)
from napms.contexts.authority_management.application.ports import AuthorityPersistenceError
from napms.scoped_connectivity_inventory.application.ports import (
    DependencyAvailability,
    ScopeAdmissionOutcome,
    ScopeAdmissionResult,
    ScopeDiscoveryResult,
)


_ACTION = "ReadScopedConnectivity"


class AuthorityManagementScopedConnectivityAdapter:
    def __init__(
        self,
        *,
        checker: CheckAuthority,
        scope_lister: ListEffectiveAuthorityScopes,
    ) -> None:
        self._checker = checker
        self._scope_lister = scope_lister

    def discover_scopes(self, *, actor_id, as_of) -> ScopeDiscoveryResult:
        try:
            discovered = self._scope_lister.execute(
                actor_id=actor_id,
                action=_ACTION,
                effective_time=as_of,
            )
        except AuthorityPersistenceError:
            return ScopeDiscoveryResult(DependencyAvailability.UNAVAILABLE)

        return ScopeDiscoveryResult(
            DependencyAvailability.AVAILABLE,
            permitted_scopes=discovered.permitted_scopes,
            ambiguous_scopes=discovered.ambiguous_scopes,
        )

    def check_scope(self, *, actor_id, scope, as_of) -> ScopeAdmissionResult:
        try:
            checked = self._checker.execute(
                actor_id=actor_id,
                action=_ACTION,
                scope=scope,
                effective_time=as_of,
            )
        except AuthorityPersistenceError:
            return ScopeAdmissionResult(ScopeAdmissionOutcome.UNKNOWN)

        if checked.outcome is AuthorityOutcome.PERMITTED:
            if checked.authority_reference is None:
                return ScopeAdmissionResult(ScopeAdmissionOutcome.UNKNOWN)
            return ScopeAdmissionResult(
                ScopeAdmissionOutcome.PERMITTED,
                checked.authority_reference,
            )
        if checked.outcome is AuthorityOutcome.DENIED:
            return ScopeAdmissionResult(ScopeAdmissionOutcome.DENIED)
        return ScopeAdmissionResult(ScopeAdmissionOutcome.AMBIGUOUS)
