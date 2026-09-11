import os
from importlib.resources import files
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")


pytestmark = pytest.mark.postgres
LEGACY_DEPLOYMENT = UUID("00000000-0000-0000-0000-00000000a001")
IMPORTED_APPLICATION = UUID("506918c2-afff-018a-d9e2-900b43852c1e")


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


def _migration(name: str) -> str:
    return (
        files("napms.contexts.application_catalogue.infrastructure.persistence.postgres")
        .joinpath("migrations", name)
        .read_text(encoding="utf-8")
    )


def test_hierarchy_migration_backfills_legacy_deployment_once(postgres_dsn):
    migration_0003 = _migration("0003_catalogue_hierarchy.sql")

    with psycopg.connect(postgres_dsn) as connection:
        # Make the test self-contained when selected in isolation. All DDL below is
        # transactional and is rolled back with the fixture mutation at the end.
        connection.execute(_migration("0001_application_catalogue.sql"))
        connection.execute(_migration("0002_display_metadata.sql"))
        connection.execute(migration_0003)

        connection.execute(
            """
            TRUNCATE TABLE
                napms_application_catalogue.deployment_resource_bindings,
                napms_application_catalogue.dcs_revisions,
                napms_application_catalogue.component_deployments,
                napms_application_catalogue.components,
                napms_application_catalogue.applications
            CASCADE
            """
        )

        # Recreate the shape immediately before I27: the deployment row exists but
        # the new parent column has not yet been made mandatory/backfilled.
        connection.execute(
            """
            ALTER TABLE napms_application_catalogue.component_deployments
            ALTER COLUMN component_id DROP NOT NULL
            """
        )
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.component_deployments (
                component_deployment_id,
                provenance_reference,
                display_name
            )
            VALUES (%s, %s, %s)
            """,
            (LEGACY_DEPLOYMENT, "legacy:deployment", "Legacy Orders API"),
        )

        connection.execute(migration_0003)

        first = connection.execute(
            """
            SELECT d.component_deployment_id,
                   d.component_id,
                   c.application_id,
                   c.display_name,
                   a.display_name
            FROM napms_application_catalogue.component_deployments AS d
            JOIN napms_application_catalogue.components AS c
              ON c.component_id = d.component_id
            JOIN napms_application_catalogue.applications AS a
              ON a.application_id = c.application_id
            WHERE d.component_deployment_id = %s
            """,
            (LEGACY_DEPLOYMENT,),
        ).fetchone()

        assert first is not None
        assert first[0] == LEGACY_DEPLOYMENT
        assert first[1] is not None
        assert first[2] == IMPORTED_APPLICATION
        assert first[3] == "Legacy Orders API"
        assert first[4] == "Imported catalogue"

        component_id = first[1]
        connection.execute(migration_0003)

        assert connection.execute(
            "SELECT count(*) FROM napms_application_catalogue.applications"
        ).fetchone()[0] == 1
        assert connection.execute(
            "SELECT count(*) FROM napms_application_catalogue.components"
        ).fetchone()[0] == 1
        assert connection.execute(
            """
            SELECT component_id
            FROM napms_application_catalogue.component_deployments
            WHERE component_deployment_id = %s
            """,
            (LEGACY_DEPLOYMENT,),
        ).fetchone()[0] == component_id

        connection.rollback()
