from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, ContextManager

import psycopg
from fastapi import FastAPI

from napms.contexts.access_policy.presentation.http.errors import (
    register_access_policy_http_error_handlers,
)
from napms.contexts.access_policy.presentation.http.routes import create_access_policy_router
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
from napms.contexts.application_catalogue.presentation.http.errors import (
    register_application_catalogue_http_error_handlers,
)
from napms.contexts.authority_management.presentation.http.errors import (
    register_authority_management_http_error_handlers,
)
from napms.contexts.connectivity_decision.presentation.http.errors import (
    register_connectivity_decision_http_error_handlers,
)
from napms.contexts.connectivity_decision.presentation.http.routes import (
    create_connectivity_decision_router,
)
from napms.contexts.connectivity_requirements.presentation.http.errors import (
    register_connectivity_requirements_http_error_handlers,
)
from napms.contexts.connectivity_requirements.presentation.http.routes import (
    create_connectivity_requirements_router,
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
from napms.platform.bootstrap.config import HttpRuntimeConfig
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
from napms.workflows.policy_export.presentation.http.errors import (
    register_policy_export_http_error_handlers,
)
from napms.workflows.policy_export.presentation.http.routes import create_policy_export_router
from napms.workflows.requirement_policy_alignment.presentation.http.routes import (
    create_requirement_policy_alignment_router,
)
from napms.workflows.scoped_connectivity_inventory.presentation.http.routes import (
    create_scoped_connectivity_inventory_router,
)
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
from napms.platform.http.api import (
    HttpApiDependencies as ProcessHttpApiDependencies,
    create_http_api as create_process_http_api,
)
from napms.workflows.traffic_analysis.presentation.http.routes import create_traffic_analysis_router


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class HttpApiDependencies:
    """Feature-aware dependencies retained at the bootstrap assembly boundary."""

    authenticator: LocalPasswordAuthenticator
    sessions: InMemorySessionStore
    open_scope: Callable[[], ContextManager[Any]]
    decisions: Any
    readiness: Callable[[], bool]
    clock: Callable[[], datetime] = _utc_now
    secure_cookie: bool = False


def create_http_api(dependencies: HttpApiDependencies) -> FastAPI:
    """Build the generic process shell and attach core feature HTTP adapters."""

    app = create_process_http_api(
        ProcessHttpApiDependencies(
            authenticator=dependencies.authenticator,
            sessions=dependencies.sessions,
            readiness=dependencies.readiness,
            clock=dependencies.clock,
            secure_cookie=dependencies.secure_cookie,
        )
    )
    register_access_policy_http_error_handlers(app)
    register_connectivity_decision_http_error_handlers(app)
    register_connectivity_requirements_http_error_handlers(app)
    register_authority_management_http_error_handlers(app)
    register_policy_export_http_error_handlers(app)
    register_application_catalogue_http_error_handlers(app)
    app.include_router(
        create_scoped_connectivity_inventory_router(
            sessions=dependencies.sessions, open_scope=dependencies.open_scope
        )
    )
    app.include_router(
        create_requirement_policy_alignment_router(
            sessions=dependencies.sessions, open_scope=dependencies.open_scope
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
            sessions=dependencies.sessions, open_scope=dependencies.open_scope
        )
    )
    return app


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
