from typing import Callable

import psycopg
from fastapi import FastAPI

from napms.access_policy.application.ports import ConnectivityDecisionPort
from napms.composition.greenfield_postgres import open_greenfield_scope
from napms.runtime.auth import InMemorySessionStore, LocalPasswordAuthenticator
from napms.runtime.config import HttpRuntimeConfig
from napms.runtime.http_api import HttpApiDependencies, create_http_api
from napms.runtime.local_decision import LocalDevAllowedConnectivityDecisionAdapter


def build_http_api(
    *,
    config: HttpRuntimeConfig,
    decisions: ConnectivityDecisionPort,
    readiness_probe: Callable[[], bool] | None = None,
) -> FastAPI:
    """Compose the I8 HTTP process while keeping Decision Domain behind its port."""

    authenticator = LocalPasswordAuthenticator(config.local_credential)
    sessions = InMemorySessionStore()

    def open_scope():
        return open_greenfield_scope(config.application)

    def default_readiness() -> bool:
        try:
            with psycopg.connect(config.application.postgres.dsn) as connection:
                connection.execute("SELECT 1").fetchone()
            return True
        except psycopg.Error:
            return False

    return create_http_api(
        HttpApiDependencies(
            authenticator=authenticator,
            sessions=sessions,
            open_scope=open_scope,
            decisions=decisions,
            readiness=readiness_probe or default_readiness,
            secure_cookie=False,
        )
    )


def build_local_dev_http_api(
    *,
    config: HttpRuntimeConfig,
    readiness_probe: Callable[[], bool] | None = None,
) -> FastAPI:
    if config.application.environment != "local-dev":
        raise ValueError("local-dev decision adapter is admitted only for local-dev")
    return build_http_api(
        config=config,
        decisions=LocalDevAllowedConnectivityDecisionAdapter(),
        readiness_probe=readiness_probe,
    )
