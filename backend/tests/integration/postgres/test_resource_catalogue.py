import os
from datetime import datetime, timedelta, timezone
from importlib.resources import files

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.workflows.policy_export.application.ports import (
    ResourceRealizationOutcome,
    ResourceReference,
)
from napms.contexts.resource_catalogue.infrastructure.integrations.policy_export import (
    PolicyExportResourceCatalogueAdapter,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres import (
    PostgresResourceCatalogueRepository,
)
from napms.contexts.resource_catalogue.infrastructure.integrations.scoped_connectivity_inventory import (
    ResourceCatalogueScopedConnectivityAdapter,
)
from napms.contexts.resource_catalogue.application.list_scope_resources import (
    ListResourcesInResponsibilityScope,
)
from napms.contexts.resource_catalogue.application.ports import ResourceCataloguePersistenceError
from napms.contexts.resource_catalogue.application.resolve import ResolveResourceRealization
from napms.scoped_connectivity_inventory.application.model import RealizationState


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
    migrations = files("napms.contexts.resource_catalogue.infrastructure.persistence.postgres").joinpath(
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


def seed_scope_affiliation(
    connection,
    *,
    affiliation="affiliation-1",
    resource="resource-1",
    scope="scope-a",
    valid_from=VALID_FROM,
    valid_to=VALID_TO,
):
    connection.execute(
        """
        INSERT INTO napms_resource_catalogue.resource_scope_affiliations (
            affiliation_reference,
            resource_reference,
            responsibility_scope,
            valid_from,
            valid_to,
            provenance_reference
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            affiliation,
            resource,
            scope,
            valid_from,
            valid_to,
            f"provenance-{affiliation}",
        ),
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



def test_postgres_lists_only_effective_resources_for_responsibility_scope(
    postgres_dsn,
):
    with psycopg.connect(postgres_dsn) as connection:
        for reference in ("resource-a", "resource-b", "resource-c"):
            seed_resource(connection, reference)
        seed_scope_affiliation(
            connection,
            affiliation="aff-a",
            resource="resource-a",
            scope="scope-a",
        )
        seed_scope_affiliation(
            connection,
            affiliation="aff-b",
            resource="resource-b",
            scope="scope-a",
        )
        seed_scope_affiliation(
            connection,
            affiliation="aff-c",
            resource="resource-c",
            scope="scope-b",
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        service = ListResourcesInResponsibilityScope(
            affiliations=PostgresResourceCatalogueRepository(connection)
        )
        result = service.execute(
            responsibility_scope="scope-a",
            as_of=AS_OF,
            page=1,
            page_size=10,
        )

    assert result.resource_references == ("resource-a", "resource-b")
    assert result.has_more is False


def test_resource_scope_affiliation_validity_is_half_open(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_resource(connection)
        seed_scope_affiliation(
            connection,
            valid_from=AS_OF,
            valid_to=VALID_TO,
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        service = ListResourcesInResponsibilityScope(
            affiliations=PostgresResourceCatalogueRepository(connection)
        )
        at_start = service.execute(
            responsibility_scope="scope-a",
            as_of=AS_OF,
        )
        at_end = service.execute(
            responsibility_scope="scope-a",
            as_of=VALID_TO,
        )

    assert at_start.resource_references == ("resource-1",)
    assert at_end.resource_references == ()


def test_overlapping_resource_scope_affiliations_fail_closed(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_resource(connection)
        seed_scope_affiliation(
            connection,
            affiliation="aff-1",
        )
        seed_scope_affiliation(
            connection,
            affiliation="aff-2",
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        service = ListResourcesInResponsibilityScope(
            affiliations=PostgresResourceCatalogueRepository(connection)
        )
        with pytest.raises(ResourceCataloguePersistenceError):
            service.execute(
                responsibility_scope="scope-a",
                as_of=AS_OF,
            )


def test_scoped_resource_adapter_preserves_resource_without_realization(
    postgres_dsn,
):
    with psycopg.connect(postgres_dsn) as connection:
        seed_resource(connection)
        seed_scope_affiliation(connection)
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresResourceCatalogueRepository(connection)
        service = ResourceCatalogueScopedConnectivityAdapter(
            lister=ListResourcesInResponsibilityScope(
                affiliations=repository
            ),
            catalogue=repository,
        )
        result = service.list_local_resources(
            responsibility_scope="scope-a",
            as_of=AS_OF,
            page=1,
            page_size=50,
            search=None,
        )

    assert result.page is not None
    assert result.page.resources[0].resource_reference == "resource-1"
    assert result.page.resources[0].realization_state is RealizationState.UNRESOLVED
    assert result.page.resources[0].endpoints == ()



def test_batch_resource_realization_read_does_not_query_endpoints_per_resource(
    postgres_dsn,
):
    with psycopg.connect(postgres_dsn) as connection:
        for reference, fact, address in (
            ("resource-a", "fact-a", "203.0.113.10"),
            ("resource-b", "fact-b", "203.0.113.20"),
        ):
            seed_resource(connection, reference)
            seed_realization(
                connection,
                fact=fact,
                resource=reference,
                endpoints=((f"endpoint-{reference}", address),),
            )
        connection.commit()

    class CountingConnection:
        def __init__(self, delegate):
            self.delegate = delegate
            self.statements = []

        def execute(self, sql, params=None):
            self.statements.append(sql)
            return self.delegate.execute(sql, params)

    with psycopg.connect(postgres_dsn) as connection:
        counted = CountingConnection(connection)
        repository = PostgresResourceCatalogueRepository(counted)
        rows = repository.find_effective_realizations_for_resources(
            resource_references=("resource-a", "resource-b"),
            as_of=AS_OF,
        )

    assert len(rows) == 2
    endpoint_queries = [
        sql
        for sql in counted.statements
        if "FROM napms_resource_catalogue.resource_endpoints" in sql
    ]
    assert len(endpoint_queries) == 1
