import os
from datetime import datetime, timezone
from importlib.resources import files
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.contexts.application_catalogue.infrastructure.integrations.dcs_authoring import (
    JsonDcsAuthoringProjectionEncoder,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres import (
    PostgresApplicationCatalogueRepository,
    PostgresTargetApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)
from napms.contexts.application_catalogue.domain.model import (
    Application,
    Component,
    ComponentDeployment,
    DcsRevision,
    DeploymentResourceBinding,
    DirectedInteractionIdentity,
)
from napms.contexts.application_catalogue.domain.target_model import (
    ApplicationDeployment,
    DeploymentInteraction,
    DeploymentInteractionCompatibility,
    InteractionDefinition,
)


pytestmark = pytest.mark.postgres
NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
APPLICATION_ID = UUID("00000000-0000-0000-0000-000000001001")
SOURCE_COMPONENT_ID = UUID("00000000-0000-0000-0000-000000001002")
DESTINATION_COMPONENT_ID = UUID("00000000-0000-0000-0000-000000001003")
INTERACTION_DEFINITION_ID = UUID("00000000-0000-0000-0000-000000001004")
APPLICATION_DEPLOYMENT_ID = UUID("00000000-0000-0000-0000-000000001005")
DEPLOYMENT_INTERACTION_ID = UUID("00000000-0000-0000-0000-000000001006")
SOURCE_COMPATIBILITY_ID = UUID("00000000-0000-0000-0000-000000001007")
DESTINATION_COMPATIBILITY_ID = UUID("00000000-0000-0000-0000-000000001008")
DCS_REVISION_ID = UUID("00000000-0000-0000-0000-000000001009")


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_catalogue(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        migrations = files("napms.contexts.application_catalogue.infrastructure.persistence.postgres").joinpath(
            "migrations"
        )
        for migration in sorted(
            (path for path in migrations.iterdir() if path.name.endswith(".sql")),
            key=lambda path: path.name,
        ):
            connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_catalogue(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_application_catalogue.deployment_interaction_compatibility_sides,
                napms_application_catalogue.deployment_interaction_compatibility,
                napms_application_catalogue.deployment_interactions,
                napms_application_catalogue.application_deployments,
                napms_application_catalogue.interaction_definitions,
                napms_application_catalogue.curation_command_receipts,
                napms_application_catalogue.deployment_resource_bindings,
                napms_application_catalogue.dcs_revisions,
                napms_application_catalogue.component_deployments,
                napms_application_catalogue.components,
                napms_application_catalogue.applications
            CASCADE
            """
        )


def test_target_compatibility_rows_are_consumable_by_existing_downstream_repository(
    postgres_dsn,
) -> None:
    traffic = (
        AuthoredDcsTrafficAlternative(
            protocol="tcp",
            source_ports=DcsPortConstraint.any(),
            destination_ports=DcsPortConstraint.ranged(DcsPortRange(443, 443)),
            service_reference="https",
        ),
    )
    encoder = JsonDcsAuthoringProjectionEncoder()
    source_binding = DeploymentResourceBinding(
        reference_id="binding:source",
        component_deployment_id=SOURCE_COMPATIBILITY_ID,
        resource_reference="resource:web",
        valid_from=NOW,
        valid_to=None,
        provenance_reference="prov:source-binding",
    )
    destination_binding = DeploymentResourceBinding(
        reference_id="binding:destination",
        component_deployment_id=DESTINATION_COMPATIBILITY_ID,
        resource_reference="resource:api",
        valid_from=NOW,
        valid_to=None,
        provenance_reference="prov:destination-binding",
    )

    with psycopg.connect(postgres_dsn) as connection:
        target = PostgresTargetApplicationCatalogueRepository(connection)
        target.add_application(
            Application(
                application_id=APPLICATION_ID,
                display_name="CRM",
                provenance_reference="prov:application",
                description="Customer Relationship Management",
                domain="Sales",
                owner_reference="CRM Team",
            )
        )
        target.add_component(
            Component(
                component_id=SOURCE_COMPONENT_ID,
                application_id=APPLICATION_ID,
                display_name="Web",
                provenance_reference="prov:web",
            )
        )
        target.add_component(
            Component(
                component_id=DESTINATION_COMPONENT_ID,
                application_id=APPLICATION_ID,
                display_name="API",
                provenance_reference="prov:api",
            )
        )
        target.add_interaction_definition(
            InteractionDefinition(
                interaction_definition_id=INTERACTION_DEFINITION_ID,
                application_id=APPLICATION_ID,
                source_component_id=SOURCE_COMPONENT_ID,
                destination_component_id=DESTINATION_COMPONENT_ID,
                traffic_alternatives=traffic,
                provenance_reference="prov:definition",
            )
        )
        target.add_application_deployment(
            ApplicationDeployment(
                application_deployment_id=APPLICATION_DEPLOYMENT_ID,
                application_id=APPLICATION_ID,
                company_reference="Company A",
                environment="Production",
                scope_reference="Moscow",
                provenance_reference="prov:deployment",
            )
        )
        target.add_deployment_interaction(
            DeploymentInteraction(
                deployment_interaction_id=DEPLOYMENT_INTERACTION_ID,
                application_deployment_id=APPLICATION_DEPLOYMENT_ID,
                interaction_definition_id=INTERACTION_DEFINITION_ID,
                provenance_reference="prov:selection",
            )
        )
        target.add_component_deployment(
            ComponentDeployment(
                deployment_id=SOURCE_COMPATIBILITY_ID,
                component_id=SOURCE_COMPONENT_ID,
                provenance_reference="prov:compat-source",
            )
        )
        target.add_component_deployment(
            ComponentDeployment(
                deployment_id=DESTINATION_COMPATIBILITY_ID,
                component_id=DESTINATION_COMPONENT_ID,
                provenance_reference="prov:compat-destination",
            )
        )
        target.add_dcs_revision(
            DcsRevision(
                revision_id=DCS_REVISION_ID,
                source_component_deployment_id=SOURCE_COMPATIBILITY_ID,
                destination_component_deployment_id=DESTINATION_COMPATIBILITY_ID,
                projection_payload=encoder.encode(traffic),
                provenance_reference="prov:dcs",
            )
        )
        target.add_compatibility_projection(
            DeploymentInteractionCompatibility(
                deployment_interaction_id=DEPLOYMENT_INTERACTION_ID,
                source_component_deployment_id=SOURCE_COMPATIBILITY_ID,
                destination_component_deployment_id=DESTINATION_COMPATIBILITY_ID,
                current_dcs_revision_id=DCS_REVISION_ID,
            )
        )
        target.add_binding(source_binding)
        target.add_binding(destination_binding)
        target.commit()

        compatibility = target.get_compatibility_projection(DEPLOYMENT_INTERACTION_ID)
        assert compatibility is not None
        subject = DirectedInteractionIdentity(
            source_component_deployment_id=compatibility.source_component_deployment_id,
            destination_component_deployment_id=compatibility.destination_component_deployment_id,
            dcs_contract_revision_id=compatibility.current_dcs_revision_id,
        )

        downstream = PostgresApplicationCatalogueRepository(connection)
        assert downstream.get_dcs_revision(subject.dcs_contract_revision_id) is not None
        deployments = downstream.get_component_deployments(
            (
                subject.source_component_deployment_id,
                subject.destination_component_deployment_id,
            )
        )
        assert {item.deployment_id for item in deployments} == {
            SOURCE_COMPATIBILITY_ID,
            DESTINATION_COMPATIBILITY_ID,
        }
        assert downstream.find_effective_bindings(
            component_deployment_id=subject.source_component_deployment_id,
            as_of=NOW,
        )[0].resource_reference == "resource:web"
        assert downstream.find_effective_bindings(
            component_deployment_id=subject.destination_component_deployment_id,
            as_of=NOW,
        )[0].resource_reference == "resource:api"
