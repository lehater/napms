import os
from datetime import datetime, timedelta, timezone
from importlib.resources import files
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.contexts.application_catalogue.infrastructure.integrations.dcs_authoring import (
    JsonDcsAuthoringProjectionEncoder,
)
from napms.contexts.application_catalogue.infrastructure.persistence.postgres.target_retirement_query import (
    PostgresApplicationCatalogueRetirementDependencyQuery,
)
from napms.contexts.application_catalogue.application.target_lifecycle import RetirementDependencyKind
from napms.contexts.application_catalogue.application.target_retirement import RetirementSubjectKind
from napms.contexts.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)
from napms.contexts.application_catalogue.domain.target_model import DeploymentInteractionSide
from napms.contexts.application_catalogue.infrastructure.read_models.postgres.target import (
    PostgresApplicationCatalogueTargetReadModel,
)
from napms.contexts.resource_catalogue.application.read_resource_references import (
    ReadResourceReferences,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.resource_reference_query import (
    PostgresResourceReferenceQuery,
)


pytestmark = pytest.mark.postgres
NOW = datetime(2026, 9, 11, 0, 0, tzinfo=timezone.utc)
APP = UUID("00000000-0000-0000-0000-00000000a001")
SOURCE = UUID("00000000-0000-0000-0000-00000000a002")
DESTINATION = UUID("00000000-0000-0000-0000-00000000a003")
INTERACTION = UUID("00000000-0000-0000-0000-00000000a004")
AVAILABLE_INTERACTION = UUID("00000000-0000-0000-0000-00000000a005")
DEPLOYMENT = UUID("00000000-0000-0000-0000-00000000a006")
DEPLOYMENT_INTERACTION = UUID("00000000-0000-0000-0000-00000000a007")
SOURCE_COMPAT = UUID("00000000-0000-0000-0000-00000000a008")
DESTINATION_COMPAT = UUID("00000000-0000-0000-0000-00000000a009")
DCS = UUID("00000000-0000-0000-0000-00000000a00a")
LEGACY_DEPLOYMENT = UUID("00000000-0000-0000-0000-00000000a00b")


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_catalogues(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        for package in (
            "napms.contexts.application_catalogue.infrastructure.persistence.postgres",
            "napms.contexts.resource_catalogue.infrastructure.persistence.postgres",
        ):
            migrations = files(package).joinpath("migrations")
            for migration in sorted(
                (path for path in migrations.iterdir() if path.name.endswith(".sql")),
                key=lambda path: path.name,
            ):
                connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_catalogues(postgres_dsn):
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
                napms_application_catalogue.applications,
                napms_resource_catalogue.curation_command_receipts,
                napms_resource_catalogue.resource_responsibilities,
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resource_scope_affiliations,
                napms_resource_catalogue.resources
            CASCADE
            """
        )


def _executemany(connection, statement: str, rows) -> None:
    with connection.cursor() as cursor:
        cursor.executemany(statement, rows)


def _traffic_payload(port: int = 443) -> bytes:
    return JsonDcsAuthoringProjectionEncoder().encode(
        (
            AuthoredDcsTrafficAlternative(
                protocol="tcp",
                source_ports=DcsPortConstraint.any(),
                destination_ports=DcsPortConstraint.ranged(DcsPortRange(port, port)),
                service_reference="https",
            ),
        )
    )


def _seed(connection) -> None:
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.applications (
            application_id, display_name, provenance_reference, lifecycle_state,
            version, description, domain, owner_reference
        ) VALUES (%s, 'CRM', 'prov:app', 'Active', 1, 'CRM definition', 'Sales', 'team:crm')
        """,
        (APP,),
    )
    _executemany(
        connection,
        """
        INSERT INTO napms_application_catalogue.components (
            component_id, application_id, display_name, provenance_reference,
            lifecycle_state, version, component_type, description
        ) VALUES (%s, %s, %s, %s, 'Active', 1, %s, %s)
        """,
        (
            (SOURCE, APP, "Web", "prov:web", "Service", "Web tier"),
            (DESTINATION, APP, "API", "prov:api", "Service", "API tier"),
        ),
    )
    _executemany(
        connection,
        """
        INSERT INTO napms_application_catalogue.interaction_definitions (
            interaction_definition_id, application_id, source_component_id,
            destination_component_id, traffic_payload, provenance_reference,
            lifecycle_state, version
        ) VALUES (%s, %s, %s, %s, %s, %s, 'Active', 1)
        """,
        (
            (INTERACTION, APP, SOURCE, DESTINATION, _traffic_payload(), "prov:i1"),
            (
                AVAILABLE_INTERACTION,
                APP,
                DESTINATION,
                SOURCE,
                _traffic_payload(8443),
                "prov:i2",
            ),
        ),
    )
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.application_deployments (
            application_deployment_id, application_id, company_reference,
            environment, scope_reference, provenance_reference, lifecycle_state, version
        ) VALUES (%s, %s, 'company:a', 'Production', 'scope:moscow', 'prov:deployment', 'Active', 1)
        """,
        (DEPLOYMENT, APP),
    )
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.deployment_interactions (
            deployment_interaction_id, application_deployment_id,
            interaction_definition_id, provenance_reference, lifecycle_state, version
        ) VALUES (%s, %s, %s, 'prov:selection', 'Active', 1)
        """,
        (DEPLOYMENT_INTERACTION, DEPLOYMENT, INTERACTION),
    )
    _executemany(
        connection,
        """
        INSERT INTO napms_application_catalogue.component_deployments (
            component_deployment_id, provenance_reference, component_id,
            lifecycle_state, version
        ) VALUES (%s, %s, %s, 'Active', 1)
        """,
        (
            (SOURCE_COMPAT, "prov:source-compat", SOURCE),
            (DESTINATION_COMPAT, "prov:destination-compat", DESTINATION),
            (LEGACY_DEPLOYMENT, "prov:legacy", SOURCE),
        ),
    )
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.dcs_revisions (
            revision_id, source_component_deployment_id,
            destination_component_deployment_id, projection_payload, provenance_reference
        ) VALUES (%s, %s, %s, %s, 'prov:dcs')
        """,
        (DCS, SOURCE_COMPAT, DESTINATION_COMPAT, _traffic_payload()),
    )
    _executemany(
        connection,
        """
        INSERT INTO napms_application_catalogue.deployment_interaction_compatibility_sides (
            deployment_interaction_id, side, component_deployment_id
        ) VALUES (%s, %s, %s)
        """,
        (
            (DEPLOYMENT_INTERACTION, "Source", SOURCE_COMPAT),
            (DEPLOYMENT_INTERACTION, "Destination", DESTINATION_COMPAT),
        ),
    )
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.deployment_interaction_compatibility (
            deployment_interaction_id, current_dcs_revision_id, version
        ) VALUES (%s, %s, 1)
        """,
        (DEPLOYMENT_INTERACTION, DCS),
    )

    _executemany(
        connection,
        """
        INSERT INTO napms_resource_catalogue.resources (
            resource_reference, provenance_reference, display_name, lifecycle_state, version
        ) VALUES (%s, %s, %s, 'Active', 1)
        """,
        (
            ("resource:web-current", "prov:r1", "web-001"),
            ("resource:web-old", "prov:r2", "web-old"),
            ("resource:api-current", "prov:r3", "api-001"),
        ),
    )
    _executemany(
        connection,
        """
        INSERT INTO napms_resource_catalogue.resource_scope_affiliations (
            affiliation_reference, resource_reference, responsibility_scope,
            valid_from, valid_to, provenance_reference, version
        ) VALUES (%s, %s, %s, %s, %s, %s, 1)
        """,
        (
            ("scope:r1", "resource:web-current", "scope:moscow", NOW - timedelta(days=30), None, "prov:s1"),
            ("scope:r2", "resource:web-old", "scope:moscow", NOW - timedelta(days=30), NOW - timedelta(days=1), "prov:s2"),
            ("scope:r3", "resource:api-current", "scope:spb", NOW - timedelta(days=30), None, "prov:s3"),
        ),
    )
    _executemany(
        connection,
        """
        INSERT INTO napms_application_catalogue.deployment_resource_bindings (
            reference_id, component_deployment_id, resource_reference,
            valid_from, valid_to, provenance_reference, version
        ) VALUES (%s, %s, %s, %s, %s, %s, 1)
        """,
        (
            ("binding:web-current", SOURCE_COMPAT, "resource:web-current", NOW - timedelta(days=10), None, "prov:b1"),
            ("binding:web-old", SOURCE_COMPAT, "resource:web-old", NOW - timedelta(days=10), NOW - timedelta(days=1), "prov:b2"),
            ("binding:api-current", DESTINATION_COMPAT, "resource:api-current", NOW - timedelta(days=10), None, "prov:b3"),
        ),
    )
    connection.commit()


def test_target_read_projection_is_bounded_temporal_and_scope_aware(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        _seed(connection)
        read = PostgresApplicationCatalogueTargetReadModel(
            connection,
            resources=ReadResourceReferences(
                query=PostgresResourceReferenceQuery(connection)
            ),
        )

        definitions = read.list_definitions(
            offset=0,
            limit=10,
            search="CRM",
            domain="Sales",
            owner_reference="team:crm",
            sort="name",
        )
        assert definitions.page.total == 1
        assert definitions.items[0].component_count == 2
        assert definitions.items[0].interaction_count == 2
        assert definitions.items[0].deployment_count == 1

        available = read.list_available_interactions_for_deployment(
            application_deployment_id=DEPLOYMENT,
            offset=0,
            limit=10,
            search=None,
            source_component_id=None,
            destination_component_id=None,
            protocol=None,
            sort="source",
        )
        assert available.page.total == 1
        assert available.items[0].interaction.interaction_definition_id == AVAILABLE_INTERACTION

        connectivity = read.list_deployment_connectivity(
            application_deployment_id=DEPLOYMENT,
            as_of=NOW,
            offset=0,
            limit=10,
            search=None,
            source_component_id=None,
            destination_component_id=None,
            protocol="tcp",
            sort="source",
        )
        assert connectivity.page.total == 1
        assert connectivity.items[0].source_resource_count == 1
        assert connectivity.items[0].destination_resource_count == 1
        assert connectivity.as_of == NOW

        resources = read.list_resource_set(
            deployment_interaction_id=DEPLOYMENT_INTERACTION,
            side=DeploymentInteractionSide.SOURCE,
            as_of=NOW,
            offset=0,
            limit=10,
            search="web",
            scope_reference="scope:moscow",
            sort="resource",
        )
        assert resources.page.total == 1
        member = resources.items[0]
        assert member.resource_reference == "resource:web-current"
        assert member.binding_reference == "binding:web-current"
        assert member.binding_version == 1
        assert member.scope_references == ("scope:moscow",)

        before_end = read.list_resource_set(
            deployment_interaction_id=DEPLOYMENT_INTERACTION,
            side=DeploymentInteractionSide.SOURCE,
            as_of=NOW - timedelta(days=2),
            offset=0,
            limit=10,
            search=None,
            scope_reference="scope:moscow",
            sort="resource",
        )
        assert before_end.page.total == 2


def test_local_retirement_query_keeps_target_compatibility_out_of_legacy_dependencies(
    postgres_dsn,
):
    with psycopg.connect(postgres_dsn) as connection:
        _seed(connection)
        query = PostgresApplicationCatalogueRetirementDependencyQuery(connection)

        legacy = query.page(
            subject_kind=RetirementSubjectKind.COMPONENT,
            subject_id=SOURCE,
            dependency_kind=RetirementDependencyKind.LEGACY_COMPONENT_DEPLOYMENTS,
            as_of=NOW,
            offset=0,
            limit=10,
        )
        assert legacy.total == 1
        assert [item.reference for item in legacy.references] == [str(LEGACY_DEPLOYMENT)]

        bindings = query.page(
            subject_kind=RetirementSubjectKind.DEPLOYMENT_INTERACTION,
            subject_id=DEPLOYMENT_INTERACTION,
            dependency_kind=RetirementDependencyKind.RESOURCE_BINDINGS,
            as_of=NOW,
            offset=0,
            limit=1,
        )
        assert bindings.total == 2
        assert len(bindings.references) == 1
