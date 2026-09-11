import os
from datetime import datetime, timedelta, timezone

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.platform.bootstrap.config import ApplicationConfig, PostgresConfig
from napms.platform.bootstrap.greenfield import apply_greenfield_migrations
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.transactional_curation_repository import (
    TransactionalPostgresResourceCatalogueCurationRepository,
)
from napms.contexts.resource_catalogue.application.curation_read import ListResourceCatalogue


pytestmark = pytest.mark.postgres
NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
PAST = NOW - timedelta(days=2)
EXPIRED = NOW - timedelta(days=1)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated(postgres_dsn):
    apply_greenfield_migrations(
        ApplicationConfig(
            environment="local-dev",
            postgres=PostgresConfig(postgres_dsn),
        )
    )


@pytest.fixture(autouse=True)
def clean(postgres_dsn, migrated):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_resource_catalogue.curation_command_receipts,
                napms_resource_catalogue.resource_responsibilities,
                napms_resource_catalogue.resource_scope_affiliations,
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resources
            CASCADE
            """
        )


def _seed(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        for reference, name in (
            ("res-orders", "Orders database"),
            ("res-payments", "Payments cache"),
            ("res-legacy", "Legacy worker"),
        ):
            connection.execute(
                """
                INSERT INTO napms_resource_catalogue.resources (
                    resource_reference, provenance_reference, display_name,
                    lifecycle_state, version
                )
                VALUES (%s, %s, %s, 'Active', 1)
                """,
                (reference, f"prov:{reference}", name),
            )

        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resource_realization_versions (
                fact_reference, resource_reference, valid_from, valid_to,
                provenance_reference, version
            )
            VALUES
                ('fact:orders', 'res-orders', %s, NULL, 'prov:fact:orders', 1),
                ('fact:legacy', 'res-legacy', %s, %s, 'prov:fact:legacy', 1)
            """,
            (PAST, PAST, EXPIRED),
        )
        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resource_endpoints (
                fact_reference, endpoint_reference, technical_address
            )
            VALUES
                ('fact:orders', 'endpoint:orders', '203.0.113.10'),
                ('fact:legacy', 'endpoint:legacy', '192.0.2.10')
            """
        )

        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resource_scope_affiliations (
                affiliation_reference, resource_reference, responsibility_scope,
                valid_from, valid_to, provenance_reference, version
            )
            VALUES
                ('aff:orders', 'res-orders', 'payments-team', %s, NULL, 'prov:aff:orders', 1),
                ('aff:payments', 'res-payments', 'payments-team', %s, NULL, 'prov:aff:payments', 1),
                ('aff:legacy', 'res-legacy', 'payments-team', %s, %s, 'prov:aff:legacy', 1)
            """,
            (PAST, PAST, PAST, EXPIRED),
        )

        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resource_responsibilities (
                assignment_reference, resource_reference, party_reference,
                party_kind, role, display_name, contact,
                valid_from, valid_to, provenance_reference, version
            )
            VALUES
                ('resp:orders', 'res-orders', 'team:orders', 'Team', 'TechnicalOwner',
                 'Orders Platform', 'orders-owner@example.test', %s, NULL, 'prov:resp:orders', 1),
                ('resp:payments', 'res-payments', 'team:payments', 'Team', 'TechnicalOwner',
                 'Payments Platform', NULL, %s, NULL, 'prov:resp:payments', 1),
                ('resp:legacy', 'res-legacy', 'team:legacy', 'Team', 'TechnicalOwner',
                 'Legacy Platform', 'legacy@example.test', %s, %s, 'prov:resp:legacy', 1)
            """,
            (PAST, PAST, PAST, EXPIRED),
        )
        connection.commit()


def test_postgres_resource_workspace_filters_effective_scope_and_current_contact_search(
    postgres_dsn,
):
    _seed(postgres_dsn)

    with psycopg.connect(postgres_dsn) as connection:
        query = ListResourceCatalogue(
            catalogue=TransactionalPostgresResourceCatalogueCurationRepository(connection)
        )
        page = query.execute_workspace(
            page=1,
            page_size=50,
            search="orders-owner@example.test",
            responsibility_scope="payments-team",
            as_of=NOW,
        )

    assert tuple(item.resource.resource_reference for item in page.items) == ("res-orders",)
    item = page.items[0]
    assert item.has_effective_realization is True
    assert item.has_effective_scope_affiliation is True
    assert item.has_effective_responsibility is True
    assert item.has_effective_contact is True


def test_postgres_resource_workspace_completeness_ignores_expired_facts(postgres_dsn):
    _seed(postgres_dsn)

    with psycopg.connect(postgres_dsn) as connection:
        query = ListResourceCatalogue(
            catalogue=TransactionalPostgresResourceCatalogueCurationRepository(connection)
        )
        page = query.execute_workspace(
            page=1,
            page_size=50,
            as_of=NOW,
        )

    by_reference = {item.resource.resource_reference: item for item in page.items}
    orders = by_reference["res-orders"]
    assert orders.has_effective_realization is True
    assert orders.has_effective_scope_affiliation is True
    assert orders.has_effective_responsibility is True
    assert orders.has_effective_contact is True

    payments = by_reference["res-payments"]
    assert payments.has_effective_realization is False
    assert payments.has_effective_scope_affiliation is True
    assert payments.has_effective_responsibility is True
    assert payments.has_effective_contact is False

    legacy = by_reference["res-legacy"]
    assert legacy.has_effective_realization is False
    assert legacy.has_effective_scope_affiliation is False
    assert legacy.has_effective_responsibility is False
    assert legacy.has_effective_contact is False

    with psycopg.connect(postgres_dsn) as connection:
        query = ListResourceCatalogue(
            catalogue=TransactionalPostgresResourceCatalogueCurationRepository(connection)
        )
        scoped = query.execute_workspace(
            page=1,
            page_size=50,
            responsibility_scope="payments-team",
            as_of=NOW,
        )

    assert tuple(item.resource.resource_reference for item in scoped.items) == (
        "res-orders",
        "res-payments",
    )
