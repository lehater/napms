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
    "DiscoverConnectivityRequirementScopes",
    "DiscoverConnectivityRequirementInteractions",
    "DeclareConnectivityRequirement",
    "ListConnectivityRequirements",
    "GetConnectivityRequirement",
    "SetConnectivityRequirementApplicability",
    "SetConnectivityRequirementJustification",
    "RetireConnectivityRequirement",
    "DiscoverConnectivityDecisionScopes",
    "DiscoverConnectivityDecisionInteractions",
    "RecordConnectivityDecision",
    "ListConnectivityDecisions",
    "GetConnectivityDecision",
}


def create_http_api(dependencies: HttpApiDependencies):
    """Build the process API and replace migrated legacy routes with owner-local routers."""

    # Import lazily so owner adapters may reuse the stable transport contract
    # re-exported by this module without creating an import cycle.
    from napms.connectivity_decision.adapters.http import (
        create_connectivity_decision_router,
    )
    from napms.connectivity_requirements.adapters.http import (
        create_connectivity_requirements_router,
    )

    app = _create_legacy_http_api(dependencies)
    app.router.routes[:] = [
        route
        for route in app.router.routes
        if getattr(route, "name", None) not in _MIGRATED_ROUTE_NAMES
    ]
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
    return app
