import hashlib
import os
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy.adapters.connectivity_decision import (
    ConnectivityDecisionConsumerAdapter,
)
from napms.access_policy.application.materialize_rule import (
    MaterializationOutcome,
    MaterializeAllowedAccessRule,
    SubmitAccessRuleProposal,
)
from napms.access_policy_realization.application.ports import (
    ConfiguredPolicySemantics,
    ManagedReconciliationScopeContract,
)
from napms.access_policy_realization.domain.realization import (
    ManagedReconciliationScope,
    ReconciliationStatus,
    RequiredSemanticChange,
)
from napms.access_policy_realization.domain.rendering import RenderStatus
from napms.composition.access_policy_realization_postgres import (
    open_access_policy_realization_scope,
)
from napms.composition.config import ApplicationConfig, PostgresConfig
from napms.composition.greenfield_postgres import open_greenfield_scope
from napms.composition.network_environment_operations_stub import (
    open_network_environment_operations_stub_scope,
)
from napms.composition.postgres_migrations import apply_greenfield_migrations
from napms.connectivity_decision.application.record import (
    RecordConnectivityDecision,
    RecordDecision,
    RecordDecisionOutcome,
)
from napms.connectivity_decision.application.select import (
    SelectEffectiveConnectivityDecision,
)
from napms.connectivity_decision.domain.model import (
    DecisionEvidenceReference,
    DecisionOutcome,
    DecisionSubject,
    DecisionValidity,
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
from napms.contexts.network_environment_operations.application.command import (
    ExecuteNetworkOperationCommand,
)
from napms.contexts.network_environment_operations.domain.model import (
    OperationOutcome,
)
from tests.integration.postgres import (
    test_access_policy_realization_reconciliation as realization,
)


pytestmark = pytest.mark.postgres

REQUIREMENT_ID = UUID(int=25001)
DECISION_ID = UUID(int=25002)
RULE_ID = UUID(int=25003)


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
def clean_product_completion_state(postgres_dsn, config):
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
        connection.execute("TRUNCATE TABLE napms_authority.authority_assignments")
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
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resources
            CASCADE
            """
        )
        connection.execute(
            "TRUNCATE TABLE napms_technical_access_evidence.evidence_sets CASCADE"
        )
        connection.execute(
            "TRUNCATE TABLE napms_network_enforcement_placement.knowledge_captures CASCADE"
        )


def seed_static_owner_facts(postgres_dsn):
    realization.seed_domain(postgres_dsn)
    with psycopg.connect(postgres_dsn) as connection:
        for reference, action in (
            ("authority-requirement-i25", "DeclareConnectivityRequirement"),
            ("authority-decision-i25", "DecideConnectivity"),
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
                    reference,
                    realization.ACTOR,
                    action,
                    realization.SCOPE,
                    realization.VALID_FROM,
                    realization.VALID_TO,
                    f"provenance:{reference}",
                ),
            )
        connection.commit()


def declare_requirement(config):
    interaction = RequiredSemanticInteraction(
        realization.SOURCE_COMPONENT,
        realization.DESTINATION_COMPONENT,
        realization.DCS,
    )
    with open_greenfield_scope(config) as scope:
        result = DeclareConnectivityRequirement(
            authority=scope.requirement_authority,
            catalogue=scope.requirement_catalogue,
            requirements=scope.connectivity_requirements,
            id_factory=lambda: REQUIREMENT_ID,
        ).execute(
            DeclareRequirement(
                governance_scope=realization.SCOPE,
                dependent_component_deployment_id=realization.SOURCE_COMPONENT,
                required_interaction=interaction,
                applicability=RequirementApplicability.ongoing(),
                justification="I25 full-chain acceptance connectivity need.",
                actor_id=realization.ACTOR,
                effective_time=realization.PROPOSAL_TIME,
            )
        )
    assert result.outcome is DeclarationOutcome.DECLARED
    assert result.requirement is not None
    return result.requirement


def record_allowed_decision(config, requirement):
    subject = DecisionSubject(
        realization.SOURCE_COMPONENT,
        realization.DESTINATION_COMPONENT,
        realization.DCS,
    )
    with open_greenfield_scope(config) as scope:
        result = RecordConnectivityDecision(
            authority=scope.decision_authority,
            catalogue=scope.decision_catalogue,
            decisions=scope.connectivity_decisions,
            id_factory=lambda: DECISION_ID,
        ).execute(
            RecordDecision(
                subject=subject,
                governance_scope=realization.SCOPE,
                outcome=DecisionOutcome.ALLOWED,
                validity=DecisionValidity(realization.PROPOSAL_TIME),
                reason_code="REQUIRED_CONNECTIVITY",
                reason_text="Accepted I25 full-chain connectivity need.",
                evidence_references=(
                    DecisionEvidenceReference(
                        "ConnectivityRequirement",
                        str(requirement.requirement_id),
                    ),
                ),
                actor_id=realization.ACTOR,
                effective_time=realization.PROPOSAL_TIME,
            )
        )
    assert result.outcome is RecordDecisionOutcome.RECORDED
    assert result.decision is not None
    return result.decision


def materialize_rule_from_real_decision(config):
    with open_greenfield_scope(config) as scope:
        result = MaterializeAllowedAccessRule(
            authority=scope.authority,
            catalogue=scope.proposal_catalogue,
            decisions=ConnectivityDecisionConsumerAdapter(
                select_effective_decision=SelectEffectiveConnectivityDecision(
                    decisions=scope.connectivity_decisions
                )
            ),
            rules=scope.access_rules,
            new_rule_id=lambda: RULE_ID,
        ).execute(
            SubmitAccessRuleProposal(
                actor_id=realization.ACTOR,
                authority_scope=realization.SCOPE,
                effective_time=realization.PROPOSAL_TIME,
                source_component_deployment_id=realization.SOURCE_COMPONENT,
                destination_component_deployment_id=realization.DESTINATION_COMPONENT,
                dcs_contract_revision_id=realization.DCS,
            )
        )
    assert result.outcome is MaterializationOutcome.MATERIALIZED
    assert result.rule is not None
    return result.rule


def test_requirement_to_verified_operation_full_local_product_chain(config, postgres_dsn):
    seed_static_owner_facts(postgres_dsn)

    requirement = declare_requirement(config)
    decision = record_allowed_decision(config, requirement)
    rule = materialize_rule_from_real_decision(config)

    assert decision.evidence_references[0].reference == str(requirement.requirement_id)
    assert (
        decision.subject.source_component_deployment_id
        == requirement.required_interaction.source_component_deployment_id
    )
    assert (
        decision.subject.destination_component_deployment_id
        == requirement.required_interaction.destination_component_deployment_id
    )
    assert (
        decision.subject.dcs_contract_revision_id
        == requirement.required_interaction.dcs_contract_revision_id
    )
    assert rule.rule_id == RULE_ID
    assert rule.decision.decision_id == str(decision.decision_id)

    realization.record_placement(
        config,
        target=realization.TARGET_A,
        capture_reference="placement-i25-product-completion",
        valid_from=realization.VALID_FROM,
        valid_until=realization.VALID_TO,
    )
    configured_evidence_id = realization.record_evidence(
        config,
        capture_reference="configured-i25-empty",
        ports=(),
    )

    with open_access_policy_realization_scope(
        config,
        actor_id=realization.ACTOR,
    ) as scope:
        desired = scope.derive_desired.execute(
            governance_scope=realization.SCOPE,
            as_of=realization.AS_OF,
        )
        assert len(desired.intents) == 1
        assert desired.intents[0].rule_references == (f"access-rule:{RULE_ID}",)
        assert desired.regions_for(realization.TARGET_A)

        configured = scope.build_configured.execute(
            evidence_set_id=configured_evidence_id,
            contract=ManagedReconciliationScopeContract(
                managed_scope=ManagedReconciliationScope(
                    realization.SCOPE,
                    realization.TARGET_A,
                    "contract:i25-product-completion",
                ),
                evidence_source_namespace=realization.EVIDENCE_SOURCE.namespace,
                evidence_source_reference=realization.EVIDENCE_SOURCE.reference,
                evidence_source_scope_reference=realization.EVIDENCE_SCOPE.value,
                semantics=ConfiguredPolicySemantics.EFFECTIVE_PERMIT_SET,
                complete_for_managed_scope=True,
                provenance_reference="contract-provenance:i25-product-completion",
            ),
            as_of=realization.AS_OF,
        )
        reconciliation = scope.reconcile.execute(
            desired=desired,
            configured=configured,
        )
        assert reconciliation.status is ReconciliationStatus.DRIFT
        assert reconciliation.required_change is RequiredSemanticChange.ADD
        assert reconciliation.missing
        assert reconciliation.extra == ()

        rendered = scope.render.execute(desired)

    assert len(rendered) == 1
    artifact = rendered[0]
    assert artifact.status is RenderStatus.RENDERED
    assert artifact.content is not None
    assert artifact.target == realization.TARGET_A

    operation_scope = open_network_environment_operations_stub_scope(
        target=artifact.target
    )
    digest = hashlib.sha256(artifact.content.encode("utf-8")).hexdigest()
    operation = operation_scope.execute.execute(
        ExecuteNetworkOperationCommand(
            operation_id="op-i25-product-completion",
            target=operation_scope.target,
            renderer_name=artifact.renderer_name,
            renderer_contract_version=artifact.renderer_contract_version,
            artifact_content=artifact.content,
            artifact_digest=digest,
            actor_id=realization.ACTOR,
            authority_scope=realization.SCOPE,
            expected_pre_revision="1",
        )
    )

    assert operation.outcome is OperationOutcome.VERIFIED
    assert operation.post_state is not None
    assert operation.post_state.artifact_digest == digest
    assert operation.provenance_references
