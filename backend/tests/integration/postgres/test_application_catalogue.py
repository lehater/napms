import os
from datetime import datetime, timedelta, timezone
from importlib.resources import files
from uuid import UUID, uuid5

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy.application.ports import InteractionOutcome
from napms.access_policy.domain.model import RuleSemanticIdentity
from napms.contexts.application_catalogue.infrastructure.integrations.access_policy import (
    AccessPolicyCommunicationCatalogueAdapter,
    AccessPolicyProposalInteractionCatalogueAdapter,
)
from napms.contexts.application_catalogue.infrastructure.integrations.dcs_json_codec import JsonDcsProjectionCodec
from napms.contexts.application_catalogue.infrastructure.integrations.policy_export import (
    PolicyExportApplicationCatalogueAdapter,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres import (
    PostgresApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.infrastructure.integrations.scoped_connectivity_inventory import (
    ApplicationCatalogueScopedConnectivityAdapter,
)
from napms.contexts.application_catalogue.application.describe_interactions import (
    DescribeDirectedInteractions,
)
from napms.contexts.application_catalogue.application.list_interactions import ListDirectedInteractions
from napms.contexts.application_catalogue.application.resolve import (
    ResolveApplicationProjection,
    ValidateDirectedInteraction,
)
from napms.contexts.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortRange,
)
from napms.policy_export.application.ports import ApplicationProjectionOutcome
from napms.scoped_connectivity_inventory.application.ports import (
    DependencyAvailability,
)


pytestmark = pytest.mark.postgres
SOURCE = UUID(int=101)
DESTINATION = UUID(int=102)
DCS = UUID(int=103)
TEST_APPLICATION = UUID("00000000-0000-0000-0000-000000009001")
TEST_COMPONENT_NAMESPACE = UUID("00000000-0000-0000-0000-000000009002")
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
    migrations = files("napms.contexts.application_catalogue.infrastructure.persistence.postgres").joinpath(
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
                napms_application_catalogue.component_deployments,
                napms_application_catalogue.components,
                napms_application_catalogue.applications
            CASCADE
            """
        )


def _component_id_for(deployment_id):
    return uuid5(TEST_COMPONENT_NAMESPACE, str(deployment_id))


def seed_deployment(
    connection,
    deployment_id,
    provenance,
    display_name=None,
):
    component_id = _component_id_for(deployment_id)
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.applications (
            application_id,
            display_name,
            provenance_reference
        )
        VALUES (%s, %s, %s)
        ON CONFLICT (application_id) DO NOTHING
        """,
        (TEST_APPLICATION, "Integration test application", "test:application"),
    )
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.components (
            component_id,
            application_id,
            display_name,
            provenance_reference
        )
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (component_id) DO NOTHING
        """,
        (
            component_id,
            TEST_APPLICATION,
            f"Component {deployment_id}",
            f"test:component:{deployment_id}",
        ),
    )
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.component_deployments (
            component_deployment_id,
            component_id,
            provenance_reference,
            display_name
        )
        VALUES (%s, %s, %s, %s)
        """,
        (deployment_id, component_id, provenance, display_name),
    )


def seed_dcs(
    connection,
    *,
    source=SOURCE,
    destination=DESTINATION,
    revision=DCS,
    payload=b'{"version":1,"alternatives":[]}',
    display_name=None,
):
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.dcs_revisions (
            revision_id,
            source_component_deployment_id,
            destination_component_deployment_id,
            projection_payload,
            provenance_reference,
            display_name
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            revision,
            source,
            destination,
            payload,
            "dcs-provenance-1",
            display_name,
        ),
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


def test_postgres_reads_component_parent_and_lifecycle_for_deployment(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_deployment(connection, SOURCE, "source-deployment-provenance", "Frontend")
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        deployment = repository(connection).get_component_deployments((SOURCE,))[0]

    assert deployment.deployment_id == SOURCE
    assert deployment.component_id == _component_id_for(SOURCE)
    assert deployment.display_name == "Frontend"
    assert deployment.lifecycle_state.value == "Active"
    assert deployment.version == 1


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


def test_postgres_acc_discovers_directed_interaction_identities(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_base(connection)
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        adapter = AccessPolicyProposalInteractionCatalogueAdapter(
            discovery=ListDirectedInteractions(catalogue=repository(connection))
        )
        result = adapter.list_directed_interactions(page=1, page_size=50)

    assert result.identities == (IDENTITY,)
    assert result.page == 1
    assert result.page_size == 50
    assert result.has_more is False


def test_postgres_acc_searches_human_readable_interactions(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_deployment(
            connection,
            SOURCE,
            "source-provenance",
            "Checkout Web",
        )
        seed_deployment(
            connection,
            DESTINATION,
            "destination-provenance",
            "Orders API",
        )
        seed_dcs(
            connection,
            display_name="HTTPS Orders",
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        query = ListDirectedInteractions(catalogue=repository(connection))
        by_source = query.execute(search="checkout")
        by_destination = query.execute(search="orders api")
        by_dcs = query.execute(search="https orders")
        missing = query.execute(search="does-not-exist")

    assert tuple(item.dcs_contract_revision_id for item in by_source.items) == (DCS,)
    assert tuple(item.dcs_contract_revision_id for item in by_destination.items) == (DCS,)
    assert tuple(item.dcs_contract_revision_id for item in by_dcs.items) == (DCS,)
    assert missing.items == ()


def test_postgres_acc_batch_describes_exact_interaction_labels(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_deployment(
            connection,
            SOURCE,
            "source-provenance",
            "Checkout Web",
        )
        seed_deployment(
            connection,
            DESTINATION,
            "destination-provenance",
            "Orders API",
        )
        seed_dcs(
            connection,
            display_name="HTTPS Orders",
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        descriptions = DescribeDirectedInteractions(
            catalogue=repository(connection)
        ).execute(
            (DirectedInteractionIdentity(SOURCE, DESTINATION, DCS),)
        )

    assert len(descriptions) == 1
    description = descriptions[0]
    assert description.source_display_name == "Checkout Web"
    assert description.destination_display_name == "Orders API"
    assert description.dcs_display_name == "HTTPS Orders"
    assert description.dcs_projection_payload is not None


def test_database_rejects_blank_display_metadata(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        with pytest.raises(psycopg.errors.CheckViolation):
            seed_deployment(
                connection,
                SOURCE,
                "source-provenance",
                "   ",
            )


def test_scoped_connectivity_catalogue_adapter_batches_bindings_and_interactions(
    postgres_dsn,
):
    payload = JsonDcsProjectionCodec().encode(
        (
            DcsTrafficAlternative(
                protocol="tcp",
                source_ports=PortConstraint.any(),
                destination_ports=PortConstraint.ranged(PortRange(443, 443)),
                service_reference="https",
            ),
        )
    )
    with psycopg.connect(postgres_dsn) as connection:
        seed_deployment(
            connection,
            SOURCE,
            "source-provenance",
            display_name="Frontend",
        )
        seed_deployment(
            connection,
            DESTINATION,
            "destination-provenance",
            display_name="Orders API",
        )
        seed_dcs(
            connection,
            payload=payload,
            display_name="HTTPS Orders",
        )
        seed_binding(
            connection,
            reference="source-binding",
            deployment=SOURCE,
            resource="resource-source",
        )
        seed_binding(
            connection,
            reference="destination-binding",
            deployment=DESTINATION,
            resource="resource-destination",
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        adapter = ApplicationCatalogueScopedConnectivityAdapter(
            catalogue=repository(connection),
            decoder=JsonDcsProjectionCodec(),
        )
        components = adapter.list_bound_components(
            resource_references=("resource-source",),
            as_of=AS_OF,
        )
        interactions = adapter.list_interactions_for_components(
            component_deployment_ids=(SOURCE,),
        )
        remote_bindings = adapter.list_resource_bindings_for_components(
            component_deployment_ids=(DESTINATION,),
            as_of=AS_OF,
        )

    assert components.availability is DependencyAvailability.AVAILABLE
    assert len(components.items) == 1
    assert components.items[0].component_deployment_id == SOURCE
    assert components.items[0].display_name == "Frontend"

    assert interactions.availability is DependencyAvailability.AVAILABLE
    assert len(interactions.items) == 1
    interaction = interactions.items[0]
    assert interaction.source_display_name == "Frontend"
    assert interaction.destination_display_name == "Orders API"
    assert interaction.dcs_display_name == "HTTPS Orders"
    assert interaction.access_summary == "tcp 443"

    assert remote_bindings.availability is DependencyAvailability.AVAILABLE
    assert tuple(
        (item.component_deployment_id, item.resource_reference)
        for item in remote_bindings.items
    ) == ((DESTINATION, "resource-destination"),)
