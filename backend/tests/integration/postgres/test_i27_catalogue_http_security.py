import os
from datetime import datetime, timedelta, timezone

import pytest

psycopg = pytest.importorskip("psycopg")
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from napms.platform.bootstrap.catalogue_curation import open_catalogue_curation_scope
from napms.platform.bootstrap.config import ApplicationConfig, PostgresConfig
from napms.platform.bootstrap.greenfield import apply_greenfield_migrations
from napms.contexts.resource_catalogue.application.curation import CreateResourceCommand
from napms.contexts.resource_catalogue.presentation.http.curation import (
    create_resource_catalogue_curation_router,
)
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_api import PublicApiError


pytestmark = pytest.mark.postgres

CURATOR = "i27-http-curator"
READER = "i27-http-reader"
NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
VALID_FROM = NOW - timedelta(days=1)
VALID_TO = NOW + timedelta(days=1)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session")
def config(postgres_dsn):
    value = ApplicationConfig(
        environment="local-dev",
        postgres=PostgresConfig(postgres_dsn),
    )
    apply_greenfield_migrations(value)
    return value


@pytest.fixture(autouse=True)
def clean_security_state(postgres_dsn, config):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_application_catalogue.deployment_resource_bindings,
                napms_resource_catalogue.curation_command_receipts,
                napms_resource_catalogue.resource_responsibilities,
                napms_resource_catalogue.resource_scope_affiliations,
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resources
            CASCADE
            """
        )
        connection.execute("TRUNCATE TABLE napms_authority.authority_assignments")


def grant_resource_curation(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO napms_authority.authority_assignments (
                reference_id,
                actor_id,
                action,
                scope,
                valid_from,
                valid_to,
                provenance_reference
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                "authority:i27:http-resource-curation",
                CURATOR,
                "CurateResourceCatalogue",
                "resource-catalogue",
                VALID_FROM,
                VALID_TO,
                "provenance:authority:i27:http-resource-curation",
            ),
        )
        connection.commit()


def test_authenticated_reader_can_read_catalogue_but_backend_denies_mutation(
    postgres_dsn,
    config,
):
    grant_resource_curation(postgres_dsn)

    with open_catalogue_curation_scope(config) as curation:
        created = curation.resources.create_resource.execute(
            CreateResourceCommand(
                display_name="Visible resource",
                actor_id=CURATOR,
                effective_time=NOW,
                idempotency_key="visible-resource",
            )
        )
    assert created.outcome.value == "Created"
    assert created.resource is not None

    sessions = InMemorySessionStore(new_session_id=lambda: "reader-session")
    sessions.create(AuthenticatedActor(actor_id=READER, login="reader"))

    def open_scope():
        return open_catalogue_curation_scope(config)

    app = FastAPI()

    @app.exception_handler(PublicApiError)
    async def public_api_error_handler(request: Request, exc: PublicApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    app.include_router(
        create_resource_catalogue_curation_router(
            sessions=sessions,
            open_scope=open_scope,
            clock=lambda: NOW,
        )
    )
    client = TestClient(app)
    cookies = {"napms_session": "reader-session"}

    readable = client.get(
        "/api/v1/catalogues/resources",
        cookies=cookies,
    )
    assert readable.status_code == 200
    assert [item["resourceReference"] for item in readable.json()["items"]] == [
        created.resource.resource_reference
    ]

    denied = client.post(
        "/api/v1/catalogues/resources",
        json={"displayName": "Must not be created"},
        headers={"Idempotency-Key": "reader-create-attempt"},
        cookies=cookies,
    )
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "CatalogueAuthorityDenied"

    with psycopg.connect(postgres_dsn) as connection:
        resource_count = connection.execute(
            "SELECT count(*) FROM napms_resource_catalogue.resources"
        ).fetchone()[0]
    assert resource_count == 1
