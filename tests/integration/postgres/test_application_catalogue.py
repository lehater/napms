import os
from datetime import datetime, timedelta, timezone
from importlib.resources import files
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy.application.ports import InteractionOutcome
from napms.access_policy.domain.model import RuleSemanticIdentity
from napms.application_catalogue.adapters.access_policy import (
    AccessPolicyCommunicationCatalogueAdapter,
)
from napms.application_catalogue.adapters.policy_export import (
    PolicyExportApplicationCatalogueAdapter,
)
from napms.application_catalogue.adapters.postgres import (
    PostgresApplicationCatalogueRepository,
)
from napms.application_catalogue.application.resolve import (
    ResolveApplicationProjection,
    ValidateDirectedInteraction,
)
from napms.policy_export.application.ports import ApplicationProjectionOutcome


pytestmark = pytest.mark.postgres
SOURCE = UUID(int=101)
DESTINATION = UUID(int=102)
DCS = UUID(int=103)
AS_OF = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
VALID_TO = AS_OF + timedelta(days=1)
IDENTITY = RuleSemanticIdentity(SOURCE, DESTINATION, DCS)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_acc(postgres_dsn):
    migrations = files("napms.application_catalogue.adapters.postgres").joinpath(
        "migrations"
    )
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        for migration in sorted(
            (path for path in migrations.iterdir() if path.name.endswith(".sql")),
            key=lambda path: path.name,
        ):
            connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_acc(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_application_catalogue.deployment_resource_bindings,
                napms_application_catalogue.dcs_revisions,
                napms_application_catalogue.component_deployments
            CASCADE
            """
        )


def seed_deployment(connection, deployment_id, provenance):
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.component_deployments (
            component_deployment_id,
            provenance_reference
        )
        VALUES (%s, %s)
        """,
        (deployment_id, provenance),
    )


def seed_dcs(
    connection,
    *,
    source=SOURCE,
    destination=DESTINATION,
    revision=DCS,
    payload=b'{"version":1,"alternatives":[]}',
):
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.dcs_revisions (
            revision_id,
            source_component_deployment_id,
            destination_component_deployment_id,
            projection_payload,
            provenance_reference
        )
        VALUES (%s, %s, %s, %s, %s)
        """,
        (revision, source, destination, payload, "dcs-provenance-1"),
    )


def seed_binding(
    connection,
    *,
    reference,
    deployment,
    resource,
    valid_from=AS_OF - timedelta(days=1),
    valid_to=VALID_TO,
):
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.deployment_resource_bindings (
            reference_id,
            component_deployment_id,
            resource_reference,
            valid_from,
            valid_to,
            provenance_reference
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            reference,
            deployment,
            resource,
            valid_from,
            valid_to,
            f"provenance-{reference}",
        ),
    )


def seed_base(connection, *, dcs_source=SOURCE):
    seed_deployment(connection, SOURCE, "source-deployment-provenance")
    seed_deployment(connection, DESTINATION, "destination-deployment-provenance")
    if dcs_source not in {SOURCE, DESTINATION}:
        seed_deployment(connection, dcs_source, "other-deployment-provenance")
    seed_dcs(connection, source=dcs_source)


def repository(connection):
    return PostgresApplicationCatalogueRepository(connection)


def test_postgres_acc_validates_exact_dcs_subject(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_base(connection)
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        adapter = AccessPolicyCommunicationCatalogueAdapter(
            validator=ValidateDirectedInteraction(catalogue=repository(connection))
        )
        result = adapter.resolve_directed_interaction(
            identity=IDENTITY,
            effective_time=AS_OF,
        )

    assert result.outcome is InteractionOutcome.VALID
    assert result.identity == IDENTITY
    assert result.provenance_reference == "dcs-provenance-1"


def test_postgres_acc_rejects_dcs_subject_mismatch(postgres_dsn):
    other_source = UUID(int=999)
    with psycopg.connect(postgres_dsn) as connection:
        seed_base(connection, dcs_source=other_source)
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        adapter = AccessPolicyCommunicationCatalogueAdapter(
            validator=ValidateDirectedInteraction(catalogue=repository(connection))
        )
        result = adapter.resolve_directed_interaction(
            identity=IDENTITY,
            effective_time=AS_OF,
        )

    assert result.outcome is InteractionOutcome.INVALID


def test_postgres_projection_resolves_distinct_resources_at_as_of(postgres_dsn):
    payload = b'{"version":1,"alternatives":[{"protocol":"tcp"}]}'
    with psycopg.connect(postgres_dsn) as connection:
        seed_base(connection)
        connection.execute(
            """
            UPDATE napms_application_catalogue.dcs_revisions
            SET projection_payload = %s
            WHERE revision_id = %s
            """,
            (payload, DCS),
        )
        seed_binding(
            connection,
            reference="source-a",
            deployment=SOURCE,
            resource="resource-source-a",
        )
        seed_binding(
            connection,
            reference="source-b",
            deployment=SOURCE,
            resource="resource-source-b",
        )
        seed_binding(
            connection,
            reference="destination-a",
            deployment=DESTINATION,
            resource="resource-destination-a",
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        adapter = PolicyExportApplicationCatalogueAdapter(
            resolver=ResolveApplicationProjection(catalogue=repository(connection))
        )
        result = adapter.resolve_projection(subject=IDENTITY, as_of=AS_OF)

    assert result.outcome is ApplicationProjectionOutcome.RESOLVED
    assert result.subject == IDENTITY
    assert result.as_of == AS_OF
    assert tuple(ref.value for ref in result.source_resource_references) == (
        "resource-source-a",
        "resource-source-b",
    )
    assert tuple(ref.value for ref in result.destination_resource_references) == (
        "resource-destination-a",
    )
    assert result.dcs_projection_payload == payload
    assert result.fact_reference.startswith("acc-projection:")
    assert "source-a" in result.validity_reference
    assert "destination-a" in result.validity_reference
    assert result.provenance_reference.startswith("acc-provenance:")


def test_binding_validity_is_half_open(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_base(connection)
        seed_binding(
            connection,
            reference="source",
            deployment=SOURCE,
            resource="resource-source",
            valid_from=AS_OF,
            valid_to=VALID_TO,
        )
        seed_binding(
            connection,
            reference="destination",
            deployment=DESTINATION,
            resource="resource-destination",
            valid_from=AS_OF,
            valid_to=VALID_TO,
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        adapter = PolicyExportApplicationCatalogueAdapter(
            resolver=ResolveApplicationProjection(catalogue=repository(connection))
        )
        at_start = adapter.resolve_projection(subject=IDENTITY, as_of=AS_OF)
        at_end = adapter.resolve_projection(subject=IDENTITY, as_of=VALID_TO)

    assert at_start.outcome is ApplicationProjectionOutcome.RESOLVED
    assert at_end.outcome is ApplicationProjectionOutcome.MISSING


def test_overlapping_versions_for_same_resource_fail_closed_unknown(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_base(connection)
        seed_binding(
            connection,
            reference="source-v1",
            deployment=SOURCE,
            resource="resource-source",
        )
        seed_binding(
            connection,
            reference="source-v2",
            deployment=SOURCE,
            resource="resource-source",
        )
        seed_binding(
            connection,
            reference="destination",
            deployment=DESTINATION,
            resource="resource-destination",
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        adapter = PolicyExportApplicationCatalogueAdapter(
            resolver=ResolveApplicationProjection(catalogue=repository(connection))
        )
        result = adapter.resolve_projection(subject=IDENTITY, as_of=AS_OF)

    assert result.outcome is ApplicationProjectionOutcome.UNKNOWN


def test_database_rejects_invalid_binding_validity(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_base(connection)
        with pytest.raises(psycopg.errors.CheckViolation):
            seed_binding(
                connection,
                reference="invalid",
                deployment=SOURCE,
                resource="resource-source",
                valid_from=VALID_TO,
                valid_to=AS_OF,
            )
