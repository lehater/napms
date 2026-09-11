from datetime import datetime, timezone
from typing import Callable

import psycopg
from fastapi import FastAPI

from napms.access_policy.adapters.connectivity_decision import (
    ConnectivityDecisionConsumerAdapter,
)
from napms.access_policy.application.ports import (
    ConnectivityDecision as AccessPolicyConnectivityDecision,
    ConnectivityDecisionPort,
    DecisionOutcome as AccessPolicyDecisionOutcome,
)
from napms.application_catalogue.adapters.http.target import create_catalogue_target_router
from napms.application_catalogue.adapters.http.target_retirement import (
    create_catalogue_target_retirement_router,
)
from napms.application_catalogue.domain.model import CatalogueInvariantError
from napms.composition.catalogue_curation_postgres import (
    open_catalogue_curation_scope,
)
from napms.composition.catalogue_target_postgres import open_catalogue_target_scope
from napms.composition.greenfield_postgres import open_greenfield_scope
from napms.composition.network_operator_view_postgres import (
    open_network_operator_view_scope,
)
from napms.composition.traffic_analysis_postgres import open_traffic_analysis_scope
from napms.connectivity_decision.adapters.postgres import (
    PostgresConnectivityDecisionRepository,
)
from napms.connectivity_decision.application.ports import DecisionPersistenceError
from napms.connectivity_decision.application.select import (
    SelectEffectiveConnectivityDecision,
)
from napms.runtime.auth import InMemorySessionStore, LocalPasswordAuthenticator
from napms.runtime.catalogue_application_workspace_http import (
    create_catalogue_application_workspace_router,
)
from napms.runtime.catalogue_curation_http import create_catalogue_curation_router
from napms.runtime.catalogue_discovery_http import create_catalogue_discovery_router
from napms.runtime.catalogue_error_http import catalogue_invariant_error_handler
from napms.runtime.catalogue_resource_workspace_http import (
    create_catalogue_resource_workspace_router,
)
from napms.runtime.catalogue_temporal_curation_http import (
    create_catalogue_temporal_curation_router,
)
from napms.runtime.config import HttpRuntimeConfig
from napms.runtime.http_api import HttpApiDependencies, create_http_api
from napms.runtime.network_operator_view_http import (
    create_network_operator_view_router,
)
from napms.runtime.traffic_analysis_http import create_traffic_analysis_router


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class _PostgresConnectivityDecisionPort:
    """Open Decision persistence per Access Policy selection in local HTTP runtime."""

    def __init__(self, dsn: str) -> None:
        self._dsn = dsn

    def obtain(self, *, subject, governance_scope, as_of):
        try:
            with psycopg.connect(self._dsn) as connection:
                return ConnectivityDecisionConsumerAdapter(
                    select_effective_decision=SelectEffectiveConnectivityDecision(
                        decisions=PostgresConnectivityDecisionRepository(connection),
                    )
                ).obtain(
                    subject=subject,
                    governance_scope=governance_scope,
                    as_of=as_of,
                )
        except (psycopg.Error, DecisionPersistenceError):
            return AccessPolicyConnectivityDecision(
                outcome=AccessPolicyDecisionOutcome.UNKNOWN,
                subject=subject,
                governance_scope=governance_scope,
                valid_from=None,
            )


def build_http_api(
    *,
    config: HttpRuntimeConfig,
    decisions: ConnectivityDecisionPort,
    readiness_probe: Callable[[], bool] | None = None,
) -> FastAPI:
    """Compose the HTTP process while keeping domain owners behind explicit ports."""

    authenticator = LocalPasswordAuthenticator(config.local_credential)
    sessions = InMemorySessionStore()

    def open_scope():
        return open_greenfield_scope(config.application)

    def open_operator_scope(actor_id: str):
        return open_network_operator_view_scope(
            config.application,
            actor_id=actor_id,
        )

    def open_checker_scope():
        return open_traffic_analysis_scope(config.application)

    def open_curation_scope():
        return open_catalogue_curation_scope(config.application)

    def open_target_scope():
        return open_catalogue_target_scope(config.application)

    def default_readiness() -> bool:
        try:
            with psycopg.connect(config.application.postgres.dsn) as connection:
                connection.execute("SELECT 1").fetchone()
            return True
        except psycopg.Error:
            return False

    app = create_http_api(
        HttpApiDependencies(
            authenticator=authenticator,
            sessions=sessions,
            open_scope=open_scope,
            decisions=decisions,
            readiness=readiness_probe or default_readiness,
            secure_cookie=False,
        )
    )
    app.add_exception_handler(
        CatalogueInvariantError,
        catalogue_invariant_error_handler,
    )
    app.include_router(
        create_network_operator_view_router(
            sessions=sessions,
            open_scope=open_operator_scope,
        )
    )
    app.include_router(
        create_traffic_analysis_router(
            sessions=sessions,
            open_scope=open_checker_scope,
        )
    )
    app.include_router(
        create_catalogue_discovery_router(
            sessions=sessions,
            open_scope=open_curation_scope,
        )
    )
    app.include_router(
        create_catalogue_curation_router(
            sessions=sessions,
            open_scope=open_curation_scope,
            clock=_utc_now,
        )
    )
    app.include_router(
        create_catalogue_application_workspace_router(
            sessions=sessions,
            open_scope=open_curation_scope,
            clock=_utc_now,
        )
    )
    app.include_router(
        create_catalogue_resource_workspace_router(
            sessions=sessions,
            open_scope=open_curation_scope,
            clock=_utc_now,
        )
    )
    app.include_router(
        create_catalogue_temporal_curation_router(
            sessions=sessions,
            open_scope=open_curation_scope,
            clock=_utc_now,
        )
    )
    app.include_router(
        create_catalogue_target_router(
            sessions=sessions,
            open_scope=open_target_scope,
            clock=_utc_now,
        )
    )
    app.include_router(
        create_catalogue_target_retirement_router(
            sessions=sessions,
            open_scope=open_target_scope,
            clock=_utc_now,
        )
    )
    return app


def build_local_dev_http_api(
    *,
    config: HttpRuntimeConfig,
    readiness_probe: Callable[[], bool] | None = None,
) -> FastAPI:
    if config.application.environment != "local-dev":
        raise ValueError("local-dev HTTP composition requires local-dev environment")
    return build_http_api(
        config=config,
        decisions=_PostgresConnectivityDecisionPort(config.application.postgres.dsn),
        readiness_probe=readiness_probe,
    )
