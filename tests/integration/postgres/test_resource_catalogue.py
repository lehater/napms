import os
from datetime import datetime, timedelta, timezone
from importlib.resources import files

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.policy_export.application.ports import (
    ResourceRealizationOutcome,
    ResourceReference,
)
from napms.resource_catalogue.adapters.policy_export import (
    PolicyExportResourceCatalogueAdapter,
)
from napms.resource_catalogue.adapters.postgres import (
    PostgresResourceCatalogueRepository,
)
from napms.resource_catalogue.application.ports import ResourceCataloguePersistenceError
from napms.resource_catalogue.application.resolve import ResolveResourceRealization


pytestmark = pytest.mark.postgres
AS_OF = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
VALID_FROM = AS_OF - timedelta(days=1)
VALID_TO = AS_OF + timedelta(days=1)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_resource_catalogue(postgres_dsn):
    migrations = files("napms.resource_catalogue.adapters.postgres").joinpath(
        "migrations"
    )
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        for migration in sorted(
            (path for path in migrations.iterdir() if path.name.endswith(".sql")),
            key=lambda path: path.name,
        ):
            connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_resource_catalogue(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resources
            CASCADE
            """
        )


def seed_resource(connection, reference="resource-1"):
    connection.execute(
        """
        INSERT INTO napms_resource_catalogue.resources (
            resource_reference,
            provenance_reference
        )
        VALUES (%s, %s)
        """,
        (reference, f"resource-provenance-{reference}"),
    )


def seed_realization(
    connection,
    *,
    fact="fact-1",
    resource="resource-1",
    valid_from=VALID_FROM,
    valid_to=VALID_TO,
    endpoints=(("endpoint-b", "203.0.113.2"), ("endpoint-a", "203.0.113.1")),
):
    connection.execute(
        """
        INSERT INTO napms_resource_catalogue.resource_realization_versions (
            fact_reference,
            resource_reference,
            valid_from,
            valid_to,
            provenance_reference
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (
            fact,
            resource,
            valid_from,
            valid_to,
            f"provenance-{fact}",
        ),
    )
    for endpoint_reference, technical_address in endpoints:
        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resource_endpoints (
                fact_reference,
                endpoint_reference,
                technical_address
            )
            VALUES (%s, %s, %s)
            """,
            (fact, endpoint_reference, technical_address),
        )


def adapter(connection):
    return PolicyExportResourceCatalogueAdapter(
        resolver=ResolveResourceRealization(
            catalogue=PostgresResourceCatalogueRepository(connection)
        )
    )


def test_postgres_resource_catalogue_resolves_multiple_endpoints_deterministically(
    postgres_dsn,
):
    with psycopg.connect(postgres_dsn) as connection:
        seed_resource(connection)
        seed_realization(connection)
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        result = adapter(connection).resolve_realization(
            resource_reference=ResourceReference("resource-1"),
            as_of=AS_OF,
        )

    assert result.outcome is ResourceRealizationOutcome.RESOLVED
    assert result.resource_reference == ResourceReference("resource-1")
    assert result.as_of == AS_OF
    assert tuple(
        (endpoint.endpoint_reference, endpoint.technical_address)
        for endpoint in result.endpoint_realizations
    ) == (
        ("endpoint-a", "203.0.113.1"),
        ("endpoint-b", "203.0.113.2"),
    )
    assert result.fact_reference == "fact-1"
    assert result.validity_reference == "rc-validity:fact-1"
    assert result.provenance_reference == "provenance-fact-1"


def test_postgres_resource_validity_is_half_open(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_resource(connection)
        seed_realization(
            connection,
            valid_from=AS_OF,
            valid_to=VALID_TO,
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        service = adapter(connection)
        at_start = service.resolve_realization(
            resource_reference=ResourceReference("resource-1"),
            as_of=AS_OF,
        )
        at_end = service.resolve_realization(
            resource_reference=ResourceReference("resource-1"),
            as_of=VALID_TO,
        )

    assert at_start.outcome is ResourceRealizationOutcome.RESOLVED
    assert at_end.outcome is ResourceRealizationOutcome.STALE


def test_unknown_resource_is_missing(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        result = adapter(connection).resolve_realization(
            resource_reference=ResourceReference("missing"),
            as_of=AS_OF,
        )

    assert result.outcome is ResourceRealizationOutcome.MISSING


def test_known_resource_with_only_expired_fact_is_stale(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_resource(connection)
        seed_realization(
            connection,
            valid_from=AS_OF - timedelta(days=2),
            valid_to=AS_OF - timedelta(days=1),
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        result = adapter(connection).resolve_realization(
            resource_reference=ResourceReference("resource-1"),
            as_of=AS_OF,
        )

    assert result.outcome is ResourceRealizationOutcome.STALE


def test_overlapping_effective_realization_versions_fail_closed_unknown(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_resource(connection)
        seed_realization(connection, fact="fact-1")
        seed_realization(
            connection,
            fact="fact-2",
            endpoints=(("endpoint-c", "203.0.113.3"),),
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        result = adapter(connection).resolve_realization(
            resource_reference=ResourceReference("resource-1"),
            as_of=AS_OF,
        )

    assert result.outcome is ResourceRealizationOutcome.UNKNOWN


def test_database_rejects_invalid_realization_validity(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_resource(connection)
        with pytest.raises(psycopg.errors.CheckViolation):
            seed_realization(
                connection,
                fact="invalid",
                valid_from=VALID_TO,
                valid_to=AS_OF,
            )


def test_database_requires_endpoint_for_resolved_domain_hydration(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_resource(connection)
        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resource_realization_versions (
                fact_reference,
                resource_reference,
                valid_from,
                valid_to,
                provenance_reference
            )
            VALUES (%s, %s, %s, %s, %s)
            """,
            ("fact-empty", "resource-1", VALID_FROM, VALID_TO, "provenance-empty"),
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        with pytest.raises(ResourceCataloguePersistenceError):
            adapter(connection).resolve_realization(
                resource_reference=ResourceReference("resource-1"),
                as_of=AS_OF,
            )
