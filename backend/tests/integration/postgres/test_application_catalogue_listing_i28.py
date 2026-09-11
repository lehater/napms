import os
from importlib.resources import files
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.application_catalogue.adapters.postgres.curation_repository import (
    PostgresApplicationCatalogueCurationRepository,
)
from napms.application_catalogue.domain.model import Application


pytestmark = pytest.mark.postgres


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_application_catalogue(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        migrations = files("napms.application_catalogue.adapters.postgres").joinpath(
            "migrations"
        )
        for migration in sorted(
            (path for path in migrations.iterdir() if path.name.endswith(".sql")),
            key=lambda path: path.name,
        ):
            connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_application_catalogue(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            "TRUNCATE TABLE napms_application_catalogue.applications CASCADE"
        )


def test_postgres_application_listing_supports_empty_and_text_search(postgres_dsn):
    orders_id = UUID("00000000-0000-0000-0000-000000008001")
    billing_id = UUID("00000000-0000-0000-0000-000000008002")

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresApplicationCatalogueCurationRepository(connection)
        repository.add_application(
            Application(orders_id, "Order Management Platform", "prov:orders")
        )
        repository.add_application(
            Application(billing_id, "Billing", "prov:billing")
        )
        connection.commit()

        all_active = repository.list_applications(
            offset=0,
            limit=50,
            search=None,
            include_retired=False,
        )
        searched = repository.list_applications(
            offset=0,
            limit=50,
            search="order management",
            include_retired=False,
        )

    assert {item.application_id for item in all_active} == {orders_id, billing_id}
    assert [item.application_id for item in searched] == [orders_id]
