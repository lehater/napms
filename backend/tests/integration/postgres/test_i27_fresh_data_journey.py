import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.contexts.application_catalogue.application.binding_curation import (
    CreateDeploymentResourceBindingCommand,
)
from napms.contexts.application_catalogue.application.curation import (
    CreateApplicationCommand,
)
from napms.contexts.application_catalogue.application.dcs_curation import (
    CreateDcsRevisionCommand,
)
from napms.contexts.application_catalogue.application.deployment_curation import (
    CreateComponentDeploymentCommand,
)
from napms.contexts.application_catalogue.application.structure_curation import (
    CreateComponentCommand,
)
from napms.contexts.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)
from napms.platform.bootstrap.catalogue_curation import (
    open_catalogue_curation_scope,
)
from napms.platform.bootstrap.config import ApplicationConfig, PostgresConfig
from napms.platform.bootstrap.greenfield import (
    apply_greenfield_migrations,
    open_greenfield_scope,
)
from napms.contexts.connectivity_requirements.application.declare import (
    DeclarationOutcome,
    DeclareConnectivityRequirement,
    DeclareRequirement,
)
from napms.contexts.connectivity_requirements.domain.model import (
    RequiredSemanticInteraction,
    RequirementApplicability,
)
from napms.contexts.resource_catalogue.application.curation import CreateResourceCommand
from napms.contexts.resource_catalogue.application.realization_curation import (
    CreateResourceRealizationCommand,
)
from napms.contexts.resource_catalogue.application.responsibility_curation import (
    CreateResponsibilityCommand,
)
from napms.contexts.resource_catalogue.application.scope_affiliation_curation import (
    CreateScopeAffiliationCommand,
)
from napms.contexts.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibilityRole,
)
from napms.workflows.scoped_connectivity_inventory.application.model import (
    Direction,
    RequirementCurrent,
)
from napms.workflows.scoped_connectivity_inventory.application.read import (
    InventoryQueryOutcome,
)


pytestmark = pytest.mark.postgres

ACTOR = "i27-fresh-curator"
RESPONSIBILITY_SCOPE = "payments-team"
NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
VALID_FROM = NOW - timedelta(days=1)
VALID_TO = NOW + timedelta(days=1)
REQUIREMENT_ID = UUID("00000000-0000-0000-0000-000000027001")


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
def clean_i27_fresh_journey(postgres_dsn, config):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_connectivity_requirements.applicability_changes,
                napms_connectivity_requirements.justification_changes,
                napms_connectivity_requirements.lifecycle_transitions,
                napms_connectivity_requirements.connectivity_requirements,
                napms_connectivity_decision.connectivity_decisions,
                napms_access_policy.access_rule_effective_window_changes,
                napms_access_policy.access_rule_effective_windows,
                napms_access_policy.access_rule_state_transitions,
                napms_access_policy.access_rules,
                napms_application_catalogue.curation_command_receipts,
                napms_application_catalogue.deployment_resource_bindings,
                napms_application_catalogue.dcs_revisions,
                napms_application_catalogue.component_deployments,
                napms_application_catalogue.components,
                napms_application_catalogue.applications,
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


def grant_product_authority(postgres_dsn):
    rows = (
        (
            "authority:i27:resource-curation",
            "CurateResourceCatalogue",
            "resource-catalogue",
        ),
        (
            "authority:i27:application-curation",
            "CurateApplicationCatalogue",
            "application-catalogue",
        ),
        (
            "authority:i27:scoped-connectivity",
            "ReadScopedConnectivity",
            RESPONSIBILITY_SCOPE,
        ),
        (
            "authority:i27:declare-requirement",
            "DeclareConnectivityRequirement",
            RESPONSIBILITY_SCOPE,
        ),
    )
    with psycopg.connect(postgres_dsn) as connection:
        for reference, action, scope in rows:
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
                    reference,
                    ACTOR,
                    action,
                    scope,
                    VALID_FROM,
                    VALID_TO,
                    f"provenance:{reference}",
                ),
            )
        connection.commit()


def test_fresh_catalogue_curation_flows_into_connectivity_and_requirement(
    postgres_dsn,
    config,
):
    grant_product_authority(postgres_dsn)

    with open_catalogue_curation_scope(config) as curation:
        source_resource_result = curation.resources.create_resource.execute(
            CreateResourceCommand(
                display_name="Checkout Web resource",
                actor_id=ACTOR,
                effective_time=NOW,
                idempotency_key="resource-source",
            )
        )
        destination_resource_result = curation.resources.create_resource.execute(
            CreateResourceCommand(
                display_name="Orders API resource",
                actor_id=ACTOR,
                effective_time=NOW,
                idempotency_key="resource-destination",
            )
        )
        assert source_resource_result.outcome.value == "Created"
        assert destination_resource_result.outcome.value == "Created"
        source_resource = source_resource_result.resource
        destination_resource = destination_resource_result.resource
        assert source_resource is not None
        assert destination_resource is not None

        for key, resource_reference, address in (
            (
                "source",
                source_resource.resource_reference,
                "198.51.100.27",
            ),
            (
                "destination",
                destination_resource.resource_reference,
                "203.0.113.27",
            ),
        ):
            realization = curation.resources.create_realization.execute(
                CreateResourceRealizationCommand(
                    resource_reference=resource_reference,
                    technical_addresses=(address,),
                    valid_from=NOW,
                    valid_to=None,
                    actor_id=ACTOR,
                    effective_time=NOW,
                    idempotency_key=f"realization-{key}",
                )
            )
            assert realization.outcome.value == "Created"

        affiliation = curation.resources.create_scope_affiliation.execute(
            CreateScopeAffiliationCommand(
                resource_reference=source_resource.resource_reference,
                responsibility_scope=RESPONSIBILITY_SCOPE,
                valid_from=NOW,
                valid_to=None,
                actor_id=ACTOR,
                effective_time=NOW,
                idempotency_key="source-affiliation",
            )
        )
        assert affiliation.outcome.value == "Created"

        responsibility = curation.resources.create_responsibility.execute(
            CreateResponsibilityCommand(
                resource_reference=source_resource.resource_reference,
                party_reference="team:checkout",
                party_kind=ResponsiblePartyKind.TEAM,
                role=ResourceResponsibilityRole.TECHNICAL_OWNER,
                display_name="Checkout Team",
                contact="checkout@example.test",
                valid_from=NOW,
                valid_to=None,
                actor_id=ACTOR,
                effective_time=NOW,
                idempotency_key="source-responsibility",
            )
        )
        assert responsibility.outcome.value == "Created"

        application_result = curation.applications.create_application.execute(
            CreateApplicationCommand(
                display_name="Checkout",
                actor_id=ACTOR,
                effective_time=NOW,
                idempotency_key="application-checkout",
            )
        )
        assert application_result.outcome.value == "Created"
        application = application_result.application
        assert application is not None

        source_component_result = curation.applications.create_component.execute(
            CreateComponentCommand(
                application_id=application.application_id,
                display_name="Checkout Web",
                actor_id=ACTOR,
                effective_time=NOW,
                idempotency_key="component-checkout-web",
            )
        )
        destination_component_result = curation.applications.create_component.execute(
            CreateComponentCommand(
                application_id=application.application_id,
                display_name="Orders API",
                actor_id=ACTOR,
                effective_time=NOW,
                idempotency_key="component-orders-api",
            )
        )
        assert source_component_result.outcome.value == "Created"
        assert destination_component_result.outcome.value == "Created"
        source_component = source_component_result.component
        destination_component = destination_component_result.component
        assert source_component is not None
        assert destination_component is not None

        source_deployment_result = (
            curation.applications.create_component_deployment.execute(
                CreateComponentDeploymentCommand(
                    component_id=source_component.component_id,
                    display_name="Checkout Web / production",
                    actor_id=ACTOR,
                    effective_time=NOW,
                    idempotency_key="deployment-checkout-web",
                )
            )
        )
        destination_deployment_result = (
            curation.applications.create_component_deployment.execute(
                CreateComponentDeploymentCommand(
                    component_id=destination_component.component_id,
                    display_name="Orders API / production",
                    actor_id=ACTOR,
                    effective_time=NOW,
                    idempotency_key="deployment-orders-api",
                )
            )
        )
        assert source_deployment_result.outcome.value == "Created"
        assert destination_deployment_result.outcome.value == "Created"
        source_deployment = source_deployment_result.deployment
        destination_deployment = destination_deployment_result.deployment
        assert source_deployment is not None
        assert destination_deployment is not None

        for key, deployment, resource in (
            ("source", source_deployment, source_resource),
            ("destination", destination_deployment, destination_resource),
        ):
            binding = curation.applications.create_deployment_resource_binding.execute(
                CreateDeploymentResourceBindingCommand(
                    component_deployment_id=deployment.deployment_id,
                    resource_reference=resource.resource_reference,
                    valid_from=NOW,
                    valid_to=None,
                    actor_id=ACTOR,
                    effective_time=NOW,
                    idempotency_key=f"binding-{key}",
                )
            )
            assert binding.outcome.value == "Created"

        dcs_result = curation.applications.create_dcs_revision.execute(
            CreateDcsRevisionCommand(
                source_component_deployment_id=source_deployment.deployment_id,
                destination_component_deployment_id=destination_deployment.deployment_id,
                display_name="HTTPS Orders API",
                traffic_alternatives=(
                    AuthoredDcsTrafficAlternative(
                        protocol="tcp",
                        source_ports=DcsPortConstraint.any(),
                        destination_ports=DcsPortConstraint.ranged(
                            DcsPortRange(443, 443)
                        ),
                        service_reference="https",
                    ),
                ),
                actor_id=ACTOR,
                effective_time=NOW,
                idempotency_key="dcs-https-orders",
            )
        )
        assert dcs_result.outcome.value == "Created"
        dcs = dcs_result.revision
        assert dcs is not None

    with open_greenfield_scope(config) as product:
        before = product.scoped_connectivity_inventory.execute(
            actor_id=ACTOR,
            responsibility_scope=RESPONSIBILITY_SCOPE,
            as_of=NOW,
            page=1,
            page_size=50,
        )
        assert before.outcome is InventoryQueryOutcome.AVAILABLE
        assert before.page is not None
        assert len(before.page.items) == 1

        resource_item = before.page.items[0]
        assert resource_item.resource.resource_reference == source_resource.resource_reference
        assert tuple(
            endpoint.technical_address for endpoint in resource_item.resource.endpoints
        ) == ("198.51.100.27",)
        assert len(resource_item.components) == 1
        component_item = resource_item.components[0]
        assert component_item.component_deployment_id == source_deployment.deployment_id
        assert component_item.display_name == "Checkout Web / production"
        assert len(component_item.relationships) == 1

        relationship = component_item.relationships[0]
        assert relationship.direction is Direction.OUTGOING
        assert relationship.remote_component_deployment_id == (
            destination_deployment.deployment_id
        )
        assert relationship.dcs_display_name == "HTTPS Orders API"
        assert relationship.access_summary == "tcp 443"
        assert tuple(
            item.resource_reference for item in relationship.remote_resources
        ) == (destination_resource.resource_reference,)
        assert tuple(
            endpoint.technical_address
            for endpoint in relationship.remote_resources[0].endpoints
        ) == ("203.0.113.27",)
        assert relationship.requirement.current is RequirementCurrent.NONE

        interaction = RequiredSemanticInteraction(
            source_deployment.deployment_id,
            destination_deployment.deployment_id,
            dcs.revision_id,
        )
        declared = DeclareConnectivityRequirement(
            authority=product.requirement_authority,
            catalogue=product.requirement_catalogue,
            requirements=product.connectivity_requirements,
            id_factory=lambda: REQUIREMENT_ID,
        ).execute(
            DeclareRequirement(
                governance_scope=RESPONSIBILITY_SCOPE,
                dependent_component_deployment_id=source_deployment.deployment_id,
                required_interaction=interaction,
                applicability=RequirementApplicability.ongoing(),
                justification="Checkout requires Orders API over HTTPS.",
                actor_id=ACTOR,
                effective_time=NOW,
            )
        )
        assert declared.outcome is DeclarationOutcome.DECLARED
        assert declared.requirement is not None
        assert declared.requirement.requirement_id == REQUIREMENT_ID

    with open_greenfield_scope(config) as product:
        after = product.scoped_connectivity_inventory.execute(
            actor_id=ACTOR,
            responsibility_scope=RESPONSIBILITY_SCOPE,
            as_of=NOW,
            page=1,
            page_size=50,
        )

    assert after.outcome is InventoryQueryOutcome.AVAILABLE
    assert after.page is not None
    relationship = after.page.items[0].components[0].relationships[0]
    assert relationship.requirement.current is RequirementCurrent.REQUIRED
