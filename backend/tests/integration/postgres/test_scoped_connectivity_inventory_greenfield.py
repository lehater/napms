import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    ProposalProvenance,
    RuleSemanticIdentity,
)
from napms.application_catalogue.adapters.dcs_json_codec import JsonDcsProjectionCodec
from napms.composition.config import ApplicationConfig, PostgresConfig
from napms.composition.greenfield_postgres import (
    apply_greenfield_migrations,
    open_greenfield_scope,
)
from napms.connectivity_decision.adapters.postgres import (
    PostgresConnectivityDecisionRepository,
)
from napms.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionOutcome,
    DecisionProvenance,
    DecisionSubject,
    DecisionValidity,
)
from napms.connectivity_requirements.domain.model import (
    ConnectivityRequirement,
    RequiredSemanticInteraction,
    RequirementApplicability,
    RequirementDeclarationProvenance,
    RequirementSemanticKey,
)
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortRange,
)
from napms.scoped_connectivity_inventory.application.model import (
    CoverageSummary,
    DecisionSummaryState,
    Direction,
    EffectiveAtAsOf,
    PolicyOperationalState,
    RequirementCurrent,
    RuleExists,
)
from napms.scoped_connectivity_inventory.application.read import (
    InventoryQueryOutcome,
)


pytestmark = pytest.mark.postgres

ACTOR = "scoped-owner"
SCOPE = "payments-prod"
AP_SCOPE = "policy-scope"
APPLICATION = UUID(int=9700)
SOURCE_COMPONENT = UUID(int=9711)
DESTINATION_COMPONENT = UUID(int=9712)
SOURCE = UUID(int=9701)
DESTINATION = UUID(int=9702)
DCS = UUID(int=9703)
REQUIREMENT_ID = UUID(int=9704)
RULE_ID = UUID(int=9705)
DECISION_ID = UUID(int=9706)
LOCAL_RESOURCE = "resource-local"
REMOTE_RESOURCE = "resource-remote"
NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
VALID_FROM = NOW - timedelta(days=1)
VALID_TO = NOW + timedelta(days=1)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required")
    return dsn


@pytest.fixture(scope="session")
def greenfield_config(postgres_dsn):
    config = ApplicationConfig(
        environment="local-dev",
        postgres=PostgresConfig(postgres_dsn),
    )
    apply_greenfield_migrations(config)
    return config


@pytest.fixture(autouse=True)
def clean(postgres_dsn, greenfield_config):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_connectivity_requirements.applicability_changes,
                napms_connectivity_requirements.justification_changes,
                napms_connectivity_requirements.lifecycle_transitions,
                napms_connectivity_requirements.connectivity_requirements
            CASCADE
            """
        )
        connection.execute(
            "TRUNCATE TABLE napms_connectivity_decision.connectivity_decisions CASCADE"
        )
        connection.execute(
            """
            TRUNCATE TABLE
                napms_access_policy.access_rule_effective_window_changes,
                napms_access_policy.access_rule_effective_windows,
                napms_access_policy.access_rule_state_transitions,
                napms_access_policy.access_rules
            CASCADE
            """
        )
        connection.execute(
            "TRUNCATE TABLE napms_authority.authority_assignments"
        )
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
        connection.execute(
            """
            TRUNCATE TABLE
                napms_resource_catalogue.resource_scope_affiliations,
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resources
            CASCADE
            """
        )


def seed_catalogues_and_authority(postgres_dsn):
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
                "authority:scoped-read",
                ACTOR,
                "ReadScopedConnectivity",
                SCOPE,
                VALID_FROM,
                VALID_TO,
                "authority-provenance",
            ),
        )

        for resource_reference in (LOCAL_RESOURCE, REMOTE_RESOURCE):
            connection.execute(
                """
                INSERT INTO napms_resource_catalogue.resources (
                    resource_reference,
                    provenance_reference
                )
                VALUES (%s, %s)
                """,
                (
                    resource_reference,
                    f"resource-provenance:{resource_reference}",
                ),
            )

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
                "affiliation:local",
                LOCAL_RESOURCE,
                SCOPE,
                VALID_FROM,
                VALID_TO,
                "affiliation-provenance",
            ),
        )

        for resource_reference, address in (
            (LOCAL_RESOURCE, "10.10.10.10"),
            (REMOTE_RESOURCE, "10.20.20.20"),
        ):
            fact = f"fact:{resource_reference}"
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
                    resource_reference,
                    VALID_FROM,
                    VALID_TO,
                    f"realization-provenance:{resource_reference}",
                ),
            )
            connection.execute(
                """
                INSERT INTO napms_resource_catalogue.resource_endpoints (
                    fact_reference,
                    endpoint_reference,
                    technical_address
                )
                VALUES (%s, %s, %s)
                """,
                (
                    fact,
                    f"endpoint:{resource_reference}",
                    address,
                ),
            )

        connection.execute(
            """
            INSERT INTO napms_application_catalogue.applications (
                application_id,
                display_name,
                provenance_reference
            )
            VALUES (%s, %s, %s)
            """,
            (APPLICATION, "Payments", "application-provenance"),
        )

        for component_id, display_name in (
            (SOURCE_COMPONENT, "Checkout"),
            (DESTINATION_COMPONENT, "Orders"),
        ):
            connection.execute(
                """
                INSERT INTO napms_application_catalogue.components (
                    component_id,
                    application_id,
                    display_name,
                    provenance_reference
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    component_id,
                    APPLICATION,
                    display_name,
                    f"component-provenance:{component_id}",
                ),
            )

        for deployment, component_id, display_name in (
            (SOURCE, SOURCE_COMPONENT, "Checkout Frontend"),
            (DESTINATION, DESTINATION_COMPONENT, "Orders API"),
        ):
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
                (
                    deployment,
                    component_id,
                    f"deployment-provenance:{deployment}",
                    display_name,
                ),
            )

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
                DCS,
                SOURCE,
                DESTINATION,
                payload,
                "dcs-provenance",
                "HTTPS Orders",
            ),
        )

        for reference, deployment, resource in (
            ("binding:source", SOURCE, LOCAL_RESOURCE),
            ("binding:destination", DESTINATION, REMOTE_RESOURCE),
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
                    VALID_FROM,
                    VALID_TO,
                    f"binding-provenance:{reference}",
                ),
            )

        connection.commit()


def seed_decision(postgres_dsn, *, scope=SCOPE, outcome=DecisionOutcome.ALLOWED):
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityDecisionRepository(connection)
        repository.add(
            ConnectivityDecision(
                decision_id=DECISION_ID,
                subject=DecisionSubject(SOURCE, DESTINATION, DCS),
                governance_scope=scope,
                outcome=outcome,
                validity=DecisionValidity(VALID_FROM, VALID_TO),
                reason_code="SCOPED_TEST",
                reason_text="Protected Decision detail for scoped inventory test.",
                evidence_references=(),
                provenance=DecisionProvenance(
                    actor_id="decision-operator",
                    decided_at=NOW - timedelta(hours=1),
                    authority_reference="decision-authority",
                ),
            )
        )
        repository.commit()


def seed_requirement_and_rule(scope):
    interaction = RequiredSemanticInteraction(SOURCE, DESTINATION, DCS)
    requirement = ConnectivityRequirement.declared(
        requirement_id=REQUIREMENT_ID,
        semantic_key=RequirementSemanticKey(
            governance_scope=SCOPE,
            dependent_component_deployment_id=SOURCE,
            required_interaction=interaction,
        ),
        applicability=RequirementApplicability.ongoing(),
        justification="Checkout requires Orders API.",
        provenance=RequirementDeclarationProvenance(
            actor_id=ACTOR,
            effective_time=NOW,
            governance_scope=SCOPE,
            authority_reference="requirement-authority",
            catalogue_reference="dcs-provenance",
        ),
    )
    scope.connectivity_requirements.add(requirement)
    scope.connectivity_requirements.commit()

    identity = RuleSemanticIdentity(SOURCE, DESTINATION, DCS)
    rule = AccessRule.materialized_from_allowed_decision(
        rule_id=RULE_ID,
        semantic_identity=identity,
        decision=DecisionReference(
            subject=identity,
            result=ConnectivityDecisionResult.ALLOWED,
            decision_id="decision-existing-rule",
        ),
        proposal_provenance=ProposalProvenance(
            actor_id="policy-operator",
            authority_scope=AP_SCOPE,
            effective_time=NOW,
            authority_reference="proposal-authority",
            catalogue_reference="dcs-provenance",
        ),
    )
    scope.access_rules.add(rule)
    scope.access_rules.commit()


def test_greenfield_scoped_inventory_correlates_resource_component_need_and_policy(
    postgres_dsn,
    greenfield_config,
):
    seed_catalogues_and_authority(postgres_dsn)
    seed_decision(postgres_dsn)

    with open_greenfield_scope(greenfield_config) as scope:
        seed_requirement_and_rule(scope)
        result = scope.scoped_connectivity_inventory.execute(
            actor_id=ACTOR,
            responsibility_scope=SCOPE,
            as_of=NOW,
            page=1,
            page_size=50,
        )

    assert result.outcome is InventoryQueryOutcome.AVAILABLE
    assert result.page is not None
    assert result.page.partial is False
    assert len(result.page.items) == 1

    resource = result.page.items[0]
    assert resource.resource.resource_reference == LOCAL_RESOURCE
    assert len(resource.components) == 1

    component = resource.components[0]
    assert component.component_deployment_id == SOURCE
    assert component.display_name == "Checkout Frontend"
    assert len(component.relationships) == 1

    relationship = component.relationships[0]
    assert relationship.direction is Direction.OUTGOING
    assert relationship.remote_component_deployment_id == DESTINATION
    assert relationship.remote_component_display_name == "Orders API"
    assert relationship.dcs_display_name == "HTTPS Orders"
    assert relationship.access_summary == "tcp 443"
    assert tuple(
        item.resource_reference for item in relationship.remote_resources
    ) == (REMOTE_RESOURCE,)

    assert relationship.requirement.current is RequirementCurrent.REQUIRED
    assert relationship.requirement.coverage is CoverageSummary.COVERED

    assert relationship.decision.state is DecisionSummaryState.ALLOWED

    assert relationship.policy.rule_exists is RuleExists.YES
    assert (
        relationship.policy.operational_state
        is PolicyOperationalState.ACTIVE
    )
    assert relationship.policy.effective_at_as_of is EffectiveAtAsOf.YES


def test_greenfield_scoped_inventory_keeps_decision_scope_exact(
    postgres_dsn,
    greenfield_config,
):
    seed_catalogues_and_authority(postgres_dsn)
    seed_decision(postgres_dsn, scope="other-scope")

    with open_greenfield_scope(greenfield_config) as scope:
        result = scope.scoped_connectivity_inventory.execute(
            actor_id=ACTOR,
            responsibility_scope=SCOPE,
            as_of=NOW,
            page=1,
            page_size=50,
        )

    assert result.outcome is InventoryQueryOutcome.AVAILABLE
    assert result.page is not None
    assert result.page.partial is False
    relationship = result.page.items[0].components[0].relationships[0]
    assert (
        relationship.decision.state
        is DecisionSummaryState.NO_FINAL_DECISION
    )
