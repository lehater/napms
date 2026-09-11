import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.contexts.access_policy.application.read_rules import (
    AccessRuleDetailOutcome,
    GetAuthorizedAccessRule,
)
from napms.contexts.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    OperationalState,
    ProposalProvenance,
    RuleSemanticIdentity,
)
from napms.composition.config import ApplicationConfig, PostgresConfig
from napms.composition.greenfield_postgres import (
    apply_greenfield_migrations,
    open_greenfield_scope,
)
from napms.contexts.connectivity_requirements.application.declare import (
    DeclarationOutcome,
    DeclareConnectivityRequirement,
    DeclareRequirement,
)
from napms.contexts.connectivity_requirements.application.retire import (
    RetireConnectivityRequirement,
    RetireRequirement,
    RetirementOutcome,
)
from napms.contexts.connectivity_requirements.domain.model import (
    RequiredSemanticInteraction,
    RequirementApplicability,
)
from napms.requirement_policy_alignment.application.align import (
    AlignConnectivityRequirementToPolicy,
    AlignmentQueryOutcome,
)
from napms.requirement_policy_alignment.application.model import AlignmentStatus


pytestmark = pytest.mark.postgres

ACTOR = "alignment-owner"
CR_SCOPE = "requirements-scope"
AP_SCOPE = "policy-scope"
APPLICATION = UUID(int=9290)
SOURCE_COMPONENT = UUID(int=9291)
DESTINATION_COMPONENT = UUID(int=9292)
SOURCE = UUID(int=9201)
DESTINATION = UUID(int=9202)
DCS = UUID(int=9203)
REQUIREMENT_ID = UUID(int=9204)
RULE_ID = UUID(int=9205)
NOW = datetime(2026, 9, 9, 10, 0, tzinfo=timezone.utc)
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


def seed(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        for action in (
            "DeclareConnectivityRequirement",
            "ReadConnectivityRequirement",
            "RetireConnectivityRequirement",
        ):
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
                    f"authority:{action}",
                    ACTOR,
                    action,
                    CR_SCOPE,
                    VALID_FROM,
                    VALID_TO,
                    f"provenance:{action}",
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
            (APPLICATION, "Alignment fixture", "fixture:alignment:application"),
        )
        for component_id, display_name in (
            (SOURCE_COMPONENT, "Source component"),
            (DESTINATION_COMPONENT, "Destination component"),
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
                    f"fixture:alignment:component:{component_id}",
                ),
            )

        for deployment, component_id in (
            (SOURCE, SOURCE_COMPONENT),
            (DESTINATION, DESTINATION_COMPONENT),
        ):
            connection.execute(
                """
                INSERT INTO napms_application_catalogue.component_deployments (
                    component_deployment_id,
                    component_id,
                    provenance_reference
                )
                VALUES (%s, %s, %s)
                """,
                (deployment, component_id, f"deployment:{deployment}"),
            )
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
            (
                DCS,
                SOURCE,
                DESTINATION,
                b'{"trafficAlternatives":[]}',
                "dcs-provenance",
            ),
        )
        connection.commit()


def align(scope):
    return AlignConnectivityRequirementToPolicy(
        requirements=scope.requirement_alignment,
        policy=scope.policy_alignment,
    ).execute(
        requirement_id=REQUIREMENT_ID,
        actor_id=ACTOR,
        as_of=NOW,
    )


def test_alignment_recomputes_across_cr_and_ap_without_rule_read_authority(
    postgres_dsn,
    greenfield_config,
):
    seed(postgres_dsn)

    with open_greenfield_scope(greenfield_config) as scope:
        declared = DeclareConnectivityRequirement(
            authority=scope.requirement_authority,
            catalogue=scope.requirement_catalogue,
            requirements=scope.connectivity_requirements,
            id_factory=lambda: REQUIREMENT_ID,
        ).execute(
            DeclareRequirement(
                governance_scope=CR_SCOPE,
                dependent_component_deployment_id=SOURCE,
                required_interaction=RequiredSemanticInteraction(
                    SOURCE,
                    DESTINATION,
                    DCS,
                ),
                applicability=RequirementApplicability.ongoing(),
                justification="Checkout requires Orders API.",
                actor_id=ACTOR,
                effective_time=NOW,
            )
        )
        assert declared.outcome is DeclarationOutcome.DECLARED

        uncovered = align(scope)
        assert uncovered.outcome is AlignmentQueryOutcome.ALIGNED
        assert uncovered.status is AlignmentStatus.UNCOVERED

        identity = RuleSemanticIdentity(SOURCE, DESTINATION, DCS)
        rule = AccessRule.materialized_from_allowed_decision(
            rule_id=RULE_ID,
            semantic_identity=identity,
            decision=DecisionReference(
                identity,
                ConnectivityDecisionResult.ALLOWED,
                "decision-alignment",
            ),
            proposal_provenance=ProposalProvenance(
                actor_id="policy-operator",
                authority_scope=AP_SCOPE,
                effective_time=NOW,
                authority_reference="proposal-authority",
                catalogue_reference="catalogue-provenance",
            ),
        )
        scope.access_rules.add(rule)
        scope.access_rules.commit()

        covered = align(scope)
        assert covered.status is AlignmentStatus.COVERED

        hidden_rule = GetAuthorizedAccessRule(
            authority=scope.authority,
            rules=scope.access_rules,
        ).execute(
            rule_id=RULE_ID,
            actor_id=ACTOR,
            effective_time=NOW,
        )
        assert hidden_rule.outcome in {
            AccessRuleDetailOutcome.AUTHORITY_DENIED,
            AccessRuleDetailOutcome.AUTHORITY_UNKNOWN,
        }
        assert hidden_rule.rule is None

        inactive = rule.with_operational_state(
            target_state=OperationalState.INACTIVE,
            actor_id="policy-operator",
            effective_time=NOW,
            authority_reference="state-authority",
        )
        scope.access_rules.save(inactive)
        scope.access_rules.commit()

        after_disable = align(scope)
        assert after_disable.status is AlignmentStatus.UNCOVERED

        retired = RetireConnectivityRequirement(
            authority=scope.requirement_authority,
            requirements=scope.connectivity_requirements,
        ).execute(
            RetireRequirement(
                requirement_id=REQUIREMENT_ID,
                actor_id=ACTOR,
                effective_time=NOW,
            )
        )
        assert retired.outcome is RetirementOutcome.RETIRED

        not_current = align(scope)
        assert not_current.status is AlignmentStatus.NOT_CURRENT

    with psycopg.connect(postgres_dsn) as connection:
        schemas = connection.execute(
            """
            SELECT schema_name
            FROM information_schema.schemata
            WHERE schema_name LIKE 'napms%alignment%'
            """
        ).fetchall()
    assert schemas == []
