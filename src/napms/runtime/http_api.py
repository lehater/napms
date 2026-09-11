"""Process-level HTTP assembly while feature routes migrate out of the legacy module."""

from napms.runtime.legacy_http_api import (
    CORRELATION_HEADER,
    SESSION_COOKIE_NAME,
    HttpApiDependencies,
    PublicApiError,
    configure_json_logging,
    create_http_api as _create_legacy_http_api,
)


_MIGRATED_ROUTE_NAMES = {
    "DiscoverScopedConnectivityScopes",
    "ReadScopedConnectivityInventory",
    "DiscoverConnectivityRequirementScopes",
    "DiscoverConnectivityRequirementInteractions",
    "DeclareConnectivityRequirement",
    "ListConnectivityRequirements",
    "ListConnectivityRequirementAlignment",
    "GetConnectivityRequirementAlignment",
    "GetConnectivityRequirement",
    "SetConnectivityRequirementApplicability",
    "SetConnectivityRequirementJustification",
    "RetireConnectivityRequirement",
    "DiscoverConnectivityDecisionScopes",
    "DiscoverConnectivityDecisionInteractions",
    "RecordConnectivityDecision",
    "ListConnectivityDecisions",
    "GetConnectivityDecision",
    "DiscoverProposalScopes",
    "DiscoverProposalInteractions",
    "SubmitAccessRuleProposal",
    "ListAccessRules",
    "GetAccessRule",
    "SetAccessRuleOperationalState",
    "SetAccessRuleEffectiveWindow",
    "DiscoverPolicyViewScopes",
    "GetEffectiveDesiredPolicy",
    "GetNormalizedPolicy",
}


def create_http_api(dependencies: HttpApiDependencies):
    """Build the process API and replace migrated legacy routes with owner-local routers."""

    # Import lazily so owner adapters may reuse the stable transport contract
    # re-exported by this module without creating an import cycle.
    from napms.access_policy.adapters.http import create_access_policy_router
    from napms.connectivity_decision.adapters.http import (
        create_connectivity_decision_router,
    )
    from napms.connectivity_requirements.adapters.http import (
        create_connectivity_requirements_router,
    )
    from napms.policy_export.adapters.http import create_policy_export_router
    from napms.requirement_policy_alignment.adapters.http import (
        create_requirement_policy_alignment_router,
    )
    from napms.scoped_connectivity_inventory.adapters.http import (
        create_scoped_connectivity_inventory_router,
    )

    app = _create_legacy_http_api(dependencies)
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if getattr(route, "name", None) not in _MIGRATED_ROUTE_NAMES
    ]

    app.include_router(
        create_scoped_connectivity_inventory_router(
            sessions=dependencies.sessions,
            open_scope=dependencies.open_scope,
        )
    )
    # Keep static alignment paths ahead of the generic requirement-id route.
    app.include_router(
        create_requirement_policy_alignment_router(
            sessions=dependencies.sessions,
            open_scope=dependencies.open_scope,
        )
    )
    app.include_router(
        create_connectivity_requirements_router(
            sessions=dependencies.sessions,
            open_scope=dependencies.open_scope,
            clock=dependencies.clock,
        )
    )
    app.include_router(
        create_connectivity_decision_router(
            sessions=dependencies.sessions,
            open_scope=dependencies.open_scope,
            clock=dependencies.clock,
        )
    )
    app.include_router(
        create_access_policy_router(
            sessions=dependencies.sessions,
            open_scope=dependencies.open_scope,
            decisions=dependencies.decisions,
            clock=dependencies.clock,
        )
    )
    app.include_router(
        create_policy_export_router(
            sessions=dependencies.sessions,
            open_scope=dependencies.open_scope,
        )
    )
    return app
