from datetime import datetime, timezone
from typing import Callable

import psycopg
from fastapi import FastAPI

from napms.contexts.access_policy.infrastructure.integrations.connectivity_decision import (
    ConnectivityDecisionConsumerAdapter,
)
from napms.contexts.access_policy.application.ports import (
    ConnectivityDecision as AccessPolicyConnectivityDecision,
    ConnectivityDecisionPort,
    DecisionOutcome as AccessPolicyDecisionOutcome,
)
from napms.contexts.application_catalogue.presentation.http.application_workspace import (
    create_catalogue_application_workspace_router,
)
from napms.contexts.application_catalogue.presentation.http.discovery import (
    create_catalogue_discovery_router,
)
from napms.contexts.application_catalogue.presentation.http.legacy_curation import (
    create_application_catalogue_curation_router,
)
from napms.contexts.application_catalogue.presentation.http.legacy_temporal import (
    create_application_catalogue_temporal_router,
)
from napms.contexts.application_catalogue.presentation.http.target import create_catalogue_target_router
from napms.contexts.application_catalogue.presentation.http.target_retirement import (
    create_catalogue_target_retirement_router,
)
from napms.bootstrap.config import HttpRuntimeConfig
from napms.platform.bootstrap.catalogue_curation import open_catalogue_curation_scope
from napms.platform.bootstrap.application_catalogue_target import open_catalogue_target_scope
from napms.platform.bootstrap.greenfield import open_greenfield_scope
from napms.platform.bootstrap.network_operator_view import (
    open_network_operator_view_scope,
)
from napms.platform.bootstrap.traffic_analysis import open_traffic_analysis_scope
from napms.contexts.connectivity_decision.infrastructure.persistence.postgres import (
    PostgresConnectivityDecisionRepository,
)
from napms.contexts.connectivity_decision.application.ports import DecisionPersistenceError
from napms.contexts.connectivity_decision.application.select import SelectEffectiveConnectivityDecision
from napms.workflows.network_operator_view.presentation.http.routes import create_network_operator_view_router
from napms.contexts.resource_catalogue.presentation.http.curation import (
    create_resource_catalogue_curation_router,
)
from napms.contexts.resource_catalogue.presentation.http.temporal import (
    create_resource_catalogue_temporal_router,
)
from napms.contexts.resource_catalogue.presentation.http.workspace import (
    create_catalogue_resource_workspace_router,
)
from napms.platform.auth.local import InMemorySessionStore, LocalPasswordAuthenticator
from napms.platform.http.api import HttpApiDependencies, create_http_api
from napms.workflows.traffic_analysis.presentation.http.routes import create_traffic_analysis_router


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


class _PostgresConnectivityDecisionPort:
    """Open Decision persistence per Access Policy selection in local HTTP process."""

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
    """Compose the HTTP process while keeping semantic owners behind explicit ports."""

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
        create_application_catalogue_curation_router(
            sessions=sessions,
            open_scope=open_curation_scope,
            clock=_utc_now,
        )
    )
    app.include_router(
        create_resource_catalogue_curation_router(
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
        create_resource_catalogue_temporal_router(
            sessions=sessions,
            open_scope=open_curation_scope,
            clock=_utc_now,
        )
    )
    app.include_router(
        create_application_catalogue_temporal_router(
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
