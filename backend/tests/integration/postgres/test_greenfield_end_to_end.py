import os
from datetime import datetime, timedelta, timezone
from uuid import UUID, uuid5

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy.application.materialize_rule import (
    MaterializationOutcome,
    MaterializeAllowedAccessRule,
    SubmitAccessRuleProposal,
)
from napms.access_policy.application.ports import (
    ConnectivityDecision,
    DecisionOutcome,
)
from napms.access_policy.application.read_rules import (
    AccessRuleDetailOutcome,
    GetAuthorizedAccessRule,
    ListAuthorizedAccessRules,
)
from napms.access_policy.application.proposal_options import (
    DiscoverProposalInteractions,
    DiscoverProposalScopes,
    ProposalInteractionDiscoveryOutcome,
)
from napms.access_policy.application.set_effective_window import (
    EffectiveWindowMutationOutcome,
    SetAccessRuleEffectiveWindow,
    SetRuleEffectiveWindow,
)
from napms.access_policy.application.set_operational_state import (
    OperationalStateMutationOutcome,
    SetAccessRuleOperationalState,
    SetRuleOperationalState,
)
from napms.access_policy.application.select_effective_policy import (
    EffectivePolicySelectionOutcome,
    SelectAccessPolicyEffectiveDesiredPolicy,
    SelectEffectiveDesiredPolicy,
)
from napms.access_policy.domain.model import (
    EffectiveWindow,
    OperationalState,
    RuleSemanticIdentity,
)
from napms.contexts.application_catalogue.infrastructure.integrations.dcs_json_codec import (
    JsonDcsProjectionCodec,
)
from napms.composition.config import ApplicationConfig, PostgresConfig
from napms.composition.greenfield_postgres import (
    apply_greenfield_migrations,
    open_greenfield_scope,
)
from napms.composition.postgres_migrations import MIGRATIONS
from napms.policy_export.application.export_snapshot import (
    AssembleExportSnapshot,
    SnapshotAssemblyOutcome,
    SnapshotFactSource,
    SnapshotFailureCategory,
)
from napms.policy_export.application.normalize_snapshot import NormalizeExportSnapshot
from napms.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortRange,
)


pytestmark = pytest.mark.postgres

ACTOR = "actor-1"
SCOPE = "scope-1"
TEST_APPLICATION = UUID("00000000-0000-0000-0000-000000001000")
TEST_COMPONENT_NAMESPACE = UUID("00000000-0000-0000-0000-000000001100")
SOURCE = UUID(int=1001)
DESTINATION = UUID(int=1002)
DCS = UUID(int=1003)
RULE_ID = UUID(int=1004)
PROPOSAL_TIME = datetime(2026, 9, 8, 10, 0, tzinfo=timezone.utc)
AS_OF = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
VALID_FROM = AS_OF - timedelta(days=1)
VALID_TO = AS_OF + timedelta(days=1)
IDENTITY = RuleSemanticIdentity(SOURCE, DESTINATION, DCS)


class AllowedDecisionAdapter:
    def __init__(self, *, subject_override=None):
        self.subject_override = subject_override

    def obtain(self, *, subject, governance_scope, as_of):
        return ConnectivityDecision(
            outcome=DecisionOutcome.ALLOWED,
            subject=self.subject_override or subject,
            governance_scope=governance_scope,
            valid_from=as_of,
            decision_reference="decision-e2e-1",
        )


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
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
def clean_greenfield(postgres_dsn, greenfield_config):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_access_policy.access_rule_effective_window_changes,
                napms_access_policy.access_rule_effective_windows,
                napms_access_policy.access_rule_state_transitions,
                napms_access_policy.access_rules
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
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resources
            CASCADE
            """
        )


def dcs_payload():
    return JsonDcsProjectionCodec().encode(
        (
            DcsTrafficAlternative(
                protocol="tcp",
                source_ports=PortConstraint.any(),
                destination_ports=PortConstraint.ranged(PortRange(443, 443)),
                service_reference="https",
            ),
            DcsTrafficAlternative(
                protocol="udp",
                source_ports=PortConstraint.any(),
                destination_ports=PortConstraint.ranged(PortRange(53, 53)),
                service_reference="dns",
            ),
        )
    )


def seed_authority(
    connection,
    *,
    propose=True,
    read=True,
    read_rule=True,
    mutate_rule=True,
    mutate_window=True,
    overlap_propose=False,
):
    rows = []
    if propose:
        rows.append(
            (
                "authority-propose-1",
                ACTOR,
                "ProposeConnectivity",
                SCOPE,
                VALID_FROM,
                VALID_TO,
                "authority-provenance-propose-1",
            )
        )
        if overlap_propose:
            rows.append(
                (
                    "authority-propose-2",
                    ACTOR,
                    "ProposeConnectivity",
                    SCOPE,
                    VALID_FROM,
                    VALID_TO,
                    "authority-provenance-propose-2",
                )
            )
    if read:
        rows.append(
            (
                "authority-read-1",
                ACTOR,
                "ReadEffectiveDesiredPolicy",
                SCOPE,
                VALID_FROM,
                VALID_TO,
                "authority-provenance-read-1",
            )
        )
    if read_rule:
        rows.append(
            (
                "authority-read-rule-1",
                ACTOR,
                "ReadAccessRule",
                SCOPE,
                VALID_FROM,
                VALID_TO,
                "authority-provenance-read-rule-1",
            )
        )
    if mutate_rule:
        rows.append(
            (
                "authority-mutate-rule-1",
                ACTOR,
                "SetRuleOperationalState",
                SCOPE,
                VALID_FROM,
                VALID_TO,
                "authority-provenance-mutate-rule-1",
            )
        )
    if mutate_window:
        rows.append(
            (
                "authority-window-rule-1",
                ACTOR,
                "SetRuleEffectiveWindow",
                SCOPE,
                VALID_FROM,
                VALID_TO,
                "authority-provenance-window-rule-1",
            )
        )
    for row in rows:
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
            row,
        )


def _component_id_for(deployment_id):
    return uuid5(TEST_COMPONENT_NAMESPACE, str(deployment_id))


def seed_acc(
    connection,
    *,
    include_dcs=True,
    dcs_source=SOURCE,
    include_bindings=True,
):
    connection.execute(
        """
        INSERT INTO napms_application_catalogue.applications (
            application_id,
            display_name,
            provenance_reference
        )
        VALUES (%s, %s, %s)
        """,
        (TEST_APPLICATION, "Greenfield test application", "test:greenfield-application"),
    )

    deployments = [
        (SOURCE, "deployment-source-provenance"),
        (DESTINATION, "deployment-destination-provenance"),
    ]
    if dcs_source not in {SOURCE, DESTINATION}:
        deployments.append((dcs_source, "deployment-other-provenance"))

    for deployment, provenance in deployments:
        component_id = _component_id_for(deployment)
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
                TEST_APPLICATION,
                f"Component {deployment}",
                f"component-provenance:{deployment}",
            ),
        )
        connection.execute(
            """
            INSERT INTO napms_application_catalogue.component_deployments (
                component_deployment_id,
                component_id,
                provenance_reference
            )
            VALUES (%s, %s, %s)
            """,
            (deployment, component_id, provenance),
        )

    if include_dcs:
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
                dcs_source,
                DESTINATION,
                dcs_payload(),
                "dcs-provenance-1",
            ),
        )

    if include_bindings:
        for row in (
            (
                "binding-source",
                SOURCE,
                "resource-source",
                VALID_FROM,
                VALID_TO,
                "binding-source-provenance",
            ),
            (
                "binding-destination",
                DESTINATION,
                "resource-destination",
                VALID_FROM,
                VALID_TO,
                "binding-destination-provenance",
            ),
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
                row,
            )


def seed_rc(connection, *, source_valid_to=VALID_TO, include_destination=True):
    for resource in (
        "resource-source",
        "resource-destination",
    ):
        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resources (
                resource_reference,
                provenance_reference
            )
            VALUES (%s, %s)
            """,
            (resource, f"resource-provenance-{resource}"),
        )

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
            "rc-source-fact",
            "resource-source",
            VALID_FROM,
            source_valid_to,
            "rc-source-provenance",
        ),
    )
    for endpoint, address in (
        ("source-endpoint-a", "198.51.100.10"),
        ("source-endpoint-b", "198.51.100.11"),
    ):
        connection.execute(
            """
            INSERT INTO napms_resource_catalogue.resource_endpoints (
                fact_reference,
                endpoint_reference,
                technical_address
            )
            VALUES (%s, %s, %s)
            """,
            ("rc-source-fact", endpoint, address),
        )

    if include_destination:
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
                "rc-destination-fact",
                "resource-destination",
                VALID_FROM,
                VALID_TO,
                "rc-destination-provenance",
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
                "rc-destination-fact",
                "destination-endpoint",
                "203.0.113.20",
            ),
        )


def seed_greenfield(
    dsn,
    *,
    propose=True,
    read=True,
    read_rule=True,
    mutate_rule=True,
    mutate_window=True,
    overlap_propose=False,
    include_dcs=True,
    dcs_source=SOURCE,
    include_bindings=True,
    source_valid_to=VALID_TO,
    include_destination=True,
):
    with psycopg.connect(dsn) as connection:
        seed_authority(
            connection,
            propose=propose,
            read=read,
            read_rule=read_rule,
            mutate_rule=mutate_rule,
            mutate_window=mutate_window,
            overlap_propose=overlap_propose,
        )
        seed_acc(
            connection,
            include_dcs=include_dcs,
            dcs_source=dcs_source,
            include_bindings=include_bindings,
        )
        seed_rc(
            connection,
            source_valid_to=source_valid_to,
            include_destination=include_destination,
        )
        connection.commit()


def proposal():
    return SubmitAccessRuleProposal(
        actor_id=ACTOR,
        authority_scope=SCOPE,
        effective_time=PROPOSAL_TIME,
        source_component_deployment_id=SOURCE,
        destination_component_deployment_id=DESTINATION,
        dcs_contract_revision_id=DCS,
    )


def materialize(scope, *, decisions=None):
    return MaterializeAllowedAccessRule(
        authority=scope.authority,
        catalogue=scope.proposal_catalogue,
        decisions=decisions or AllowedDecisionAdapter(),
        rules=scope.access_rules,
        new_rule_id=lambda: RULE_ID,
    ).execute(proposal())


def select(scope):
    return SelectAccessPolicyEffectiveDesiredPolicy(
        authority=scope.authority,
        rules=scope.access_rules,
    ).execute(
        SelectEffectiveDesiredPolicy(
            scope=SCOPE,
            as_of=AS_OF,
            actor_id=ACTOR,
        )
    )


def snapshot(scope, selection):
    return AssembleExportSnapshot(
        application_catalogue=scope.application_projection,
        resource_catalogue=scope.resource_projection,
    ).execute(selection)


def test_tracked_greenfield_migrations_are_repeatable_and_journaled(
    postgres_dsn,
    greenfield_config,
):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute("DROP SCHEMA IF EXISTS napms_runtime CASCADE")

    first = apply_greenfield_migrations(greenfield_config)
    second = apply_greenfield_migrations(greenfield_config)

    assert first == tuple(item.migration_id for item in MIGRATIONS)
    assert second == ()

    with psycopg.connect(postgres_dsn) as connection:
        rows = connection.execute(
            """
            SELECT migration_id, checksum_sha256
            FROM napms_runtime.schema_migrations
            ORDER BY migration_id
            """
        ).fetchall()

    assert len(rows) == len(MIGRATIONS)
    assert {row[0] for row in rows} == {
        item.migration_id for item in MIGRATIONS
    }
    assert all(len(row[1]) == 64 for row in rows)


def test_greenfield_access_rule_workspace_read_and_state_mutation(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(postgres_dsn)

    with open_greenfield_scope(greenfield_config) as scope:
        assert materialize(scope).outcome is MaterializationOutcome.MATERIALIZED

        page = ListAuthorizedAccessRules(
            read_authority=scope.rule_read_scope_discovery,
            rules=scope.access_rules,
        ).execute(
            actor_id=ACTOR,
            effective_time=AS_OF,
        )
        assert tuple(rule.rule_id for rule in page.rules) == (RULE_ID,)
        assert page.ambiguous_scopes == ()

        detail = GetAuthorizedAccessRule(
            authority=scope.authority,
            rules=scope.access_rules,
        ).execute(
            rule_id=RULE_ID,
            actor_id=ACTOR,
            effective_time=AS_OF,
        )
        assert detail.outcome is AccessRuleDetailOutcome.FOUND
        assert detail.state_mutation_admission.value == "Permitted"

        mutation = SetAccessRuleOperationalState(
            authority=scope.authority,
            rules=scope.access_rules,
        ).execute(
            SetRuleOperationalState(
                rule_id=RULE_ID,
                target_state=OperationalState.INACTIVE,
                actor_id=ACTOR,
                effective_time=AS_OF,
            )
        )
        assert mutation.outcome is OperationalStateMutationOutcome.UPDATED

    with open_greenfield_scope(greenfield_config) as scope:
        persisted = GetAuthorizedAccessRule(
            authority=scope.authority,
            rules=scope.access_rules,
        ).execute(
            rule_id=RULE_ID,
            actor_id=ACTOR,
            effective_time=AS_OF,
        )

    assert persisted.outcome is AccessRuleDetailOutcome.FOUND
    assert persisted.rule.operational_state is OperationalState.INACTIVE
    assert len(persisted.rule.operational_state_history) == 1
    transition = persisted.rule.operational_state_history[0]
    assert transition.actor_id == ACTOR
    assert transition.governance_scope == SCOPE
    assert transition.authority_reference == "authority-mutate-rule-1"


def test_greenfield_policy_operations_effective_window_to_normalized_export(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(postgres_dsn)
    window = EffectiveWindow(
        AS_OF - timedelta(hours=1),
        AS_OF + timedelta(hours=1),
    )

    with open_greenfield_scope(greenfield_config) as scope:
        assert materialize(scope).outcome is MaterializationOutcome.MATERIALIZED

        policy_scopes = scope.effective_policy_scope_discovery.list_effective_policy_read_scopes(
            actor_id=ACTOR,
            effective_time=AS_OF,
        )
        assert policy_scopes.permitted_scopes == (SCOPE,)
        assert policy_scopes.ambiguous_scopes == ()

        mutation = SetAccessRuleEffectiveWindow(
            authority=scope.authority,
            rules=scope.access_rules,
        ).execute(
            SetRuleEffectiveWindow(
                rule_id=RULE_ID,
                window=window,
                actor_id=ACTOR,
                effective_time=AS_OF,
            )
        )
        assert mutation.outcome is EffectiveWindowMutationOutcome.UPDATED

        selected = SelectAccessPolicyEffectiveDesiredPolicy(
            authority=scope.authority,
            rules=scope.access_rules,
        ).execute(
            SelectEffectiveDesiredPolicy(
                scope=SCOPE,
                as_of=AS_OF,
                actor_id=ACTOR,
            )
        )
        assert selected.outcome is EffectivePolicySelectionOutcome.SELECTED
        assert tuple(rule.rule_id for rule in selected.rules) == (RULE_ID,)

        outside = SelectAccessPolicyEffectiveDesiredPolicy(
            authority=scope.authority,
            rules=scope.access_rules,
        ).execute(
            SelectEffectiveDesiredPolicy(
                scope=SCOPE,
                as_of=AS_OF + timedelta(hours=2),
                actor_id=ACTOR,
            )
        )
        assert outside.outcome is EffectivePolicySelectionOutcome.SELECTED
        assert outside.rules == ()

        assembled = snapshot(scope, selected)
        assert assembled.outcome is SnapshotAssemblyOutcome.SUCCESS
        normalized = NormalizeExportSnapshot(
            decoder=scope.dcs_decoder
        ).execute(assembled.snapshot)

    assert len(normalized.rows) == 4
    assert all(row.rule_effective_window == window for row in normalized.rows)

    with open_greenfield_scope(greenfield_config) as scope:
        persisted = GetAuthorizedAccessRule(
            authority=scope.authority,
            rules=scope.access_rules,
        ).execute(
            rule_id=RULE_ID,
            actor_id=ACTOR,
            effective_time=AS_OF,
        )

    assert persisted.outcome is AccessRuleDetailOutcome.FOUND
    assert persisted.rule.effective_window == window
    assert persisted.effective_window_mutation_admission.value == "Permitted"
    assert len(persisted.rule.effective_window_history) == 1
    change = persisted.rule.effective_window_history[0]
    assert change.actor_id == ACTOR
    assert change.governance_scope == SCOPE
    assert change.authority_reference == "authority-window-rule-1"


def test_greenfield_postgres_end_to_end_produces_complete_normalized_export(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(postgres_dsn)

    with open_greenfield_scope(greenfield_config) as scope:
        proposal_scopes = DiscoverProposalScopes(
            authority=scope.proposal_scope_discovery
        ).execute(actor_id=ACTOR, effective_time=PROPOSAL_TIME)
        assert proposal_scopes.permitted_scopes == (SCOPE,)
        assert proposal_scopes.ambiguous_scopes == ()

        interactions = DiscoverProposalInteractions(
            authority=scope.authority,
            catalogue=scope.proposal_interaction_catalogue,
        ).execute(
            actor_id=ACTOR,
            scope=SCOPE,
            effective_time=PROPOSAL_TIME,
        )
        assert interactions.outcome is ProposalInteractionDiscoveryOutcome.AVAILABLE
        assert interactions.page is not None
        assert IDENTITY in interactions.page.identities

        materialized = materialize(scope)
        assert materialized.outcome is MaterializationOutcome.MATERIALIZED
        assert materialized.rule.rule_id == RULE_ID
        assert materialized.rule.proposal_provenance.authority_reference == (
            "authority-propose-1"
        )

        selection = select(scope)
        assert selection.outcome is EffectivePolicySelectionOutcome.SELECTED
        assert selection.authority_reference == "authority-read-1"
        assert tuple(rule.rule_id for rule in selection.rules) == (RULE_ID,)

        assembled = snapshot(scope, selection)
        assert assembled.outcome is SnapshotAssemblyOutcome.SUCCESS

        normalized = NormalizeExportSnapshot(
            decoder=scope.dcs_decoder
        ).execute(assembled.snapshot)

    assert normalized.scope == SCOPE
    assert normalized.as_of == AS_OF
    assert normalized.authority_reference == "authority-read-1"
    assert len(normalized.rows) == 4

    assert {
        (
            row.source_technical_address,
            row.destination_technical_address,
            row.protocol,
            row.destination_ports.ranges,
        )
        for row in normalized.rows
    } == {
        ("198.51.100.10", "203.0.113.20", "tcp", (PortRange(443, 443),)),
        ("198.51.100.11", "203.0.113.20", "tcp", (PortRange(443, 443),)),
        ("198.51.100.10", "203.0.113.20", "udp", (PortRange(53, 53),)),
        ("198.51.100.11", "203.0.113.20", "udp", (PortRange(53, 53),)),
    }
    assert all(row.rule_id == RULE_ID for row in normalized.rows)
    assert all(row.decision_reference == "decision-e2e-1" for row in normalized.rows)
    assert all(row.acc_fact_reference.startswith("acc-projection:") for row in normalized.rows)
    assert all(row.source_fact_reference == "rc-source-fact" for row in normalized.rows)
    assert all(
        row.destination_fact_reference == "rc-destination-fact"
        for row in normalized.rows
    )


def test_missing_proposal_authority_fails_before_rule_creation(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(postgres_dsn, propose=False)

    with open_greenfield_scope(greenfield_config) as scope:
        result = materialize(scope)
        assert result.outcome is MaterializationOutcome.AUTHORITY_DENIED
        assert scope.access_rules.find_by_identity(IDENTITY) is None


def test_ambiguous_proposal_authority_fails_closed_unknown(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(postgres_dsn, overlap_propose=True)

    with open_greenfield_scope(greenfield_config) as scope:
        result = materialize(scope)
        assert result.outcome is MaterializationOutcome.AUTHORITY_UNKNOWN
        assert scope.access_rules.find_by_identity(IDENTITY) is None


def test_missing_dcs_fails_closed_before_decision_and_rule(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(postgres_dsn, include_dcs=False)

    class DecisionMustNotBeCalled:
        def obtain(self, *, subject, governance_scope, as_of):
            raise AssertionError("decision must not be called without valid DCS")

    with open_greenfield_scope(greenfield_config) as scope:
        result = materialize(scope, decisions=DecisionMustNotBeCalled())
        assert result.outcome is MaterializationOutcome.INTERACTION_UNKNOWN
        assert scope.access_rules.find_by_identity(IDENTITY) is None


def test_dcs_subject_correlation_mismatch_is_rejected(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(postgres_dsn, dcs_source=UUID(int=1999))

    with open_greenfield_scope(greenfield_config) as scope:
        result = materialize(scope)
        assert result.outcome is MaterializationOutcome.INTERACTION_INVALID
        assert scope.access_rules.find_by_identity(IDENTITY) is None


def test_connectivity_decision_subject_mismatch_is_rejected(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(postgres_dsn)
    wrong = RuleSemanticIdentity(UUID(int=7), UUID(int=8), UUID(int=9))

    with open_greenfield_scope(greenfield_config) as scope:
        result = materialize(
            scope,
            decisions=AllowedDecisionAdapter(subject_override=wrong),
        )
        assert result.outcome is MaterializationOutcome.DECISION_SUBJECT_MISMATCH
        assert scope.access_rules.find_by_identity(IDENTITY) is None


def test_stale_resource_fact_prevents_successful_snapshot(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(
        postgres_dsn,
        source_valid_to=AS_OF,
    )

    with open_greenfield_scope(greenfield_config) as scope:
        assert materialize(scope).outcome is MaterializationOutcome.MATERIALIZED
        selection = select(scope)
        assembled = snapshot(scope, selection)

    assert assembled.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    assert assembled.snapshot is None
    assert any(
        diagnostic.source is SnapshotFactSource.RESOURCE_CATALOGUE
        and diagnostic.category is SnapshotFailureCategory.STALE
        and diagnostic.reference == "resource-source"
        for diagnostic in assembled.diagnostics
    )


def test_missing_resource_fact_prevents_successful_snapshot(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(
        postgres_dsn,
        include_destination=False,
    )

    with open_greenfield_scope(greenfield_config) as scope:
        assert materialize(scope).outcome is MaterializationOutcome.MATERIALIZED
        selection = select(scope)
        assembled = snapshot(scope, selection)

    assert assembled.outcome is SnapshotAssemblyOutcome.INCOMPLETE
    assert assembled.snapshot is None
    assert any(
        diagnostic.source is SnapshotFactSource.RESOURCE_CATALOGUE
        and diagnostic.category is SnapshotFailureCategory.MISSING
        and diagnostic.reference == "resource-destination"
        for diagnostic in assembled.diagnostics
    )


def test_denied_read_authority_returns_no_policy_data(
    postgres_dsn,
    greenfield_config,
):
    seed_greenfield(postgres_dsn, read=False)

    with open_greenfield_scope(greenfield_config) as scope:
        assert materialize(scope).outcome is MaterializationOutcome.MATERIALIZED
        selection = select(scope)
        assembled = snapshot(scope, selection)

    assert selection.outcome is EffectivePolicySelectionOutcome.AUTHORITY_DENIED
    assert selection.rules == ()
    assert assembled.outcome is SnapshotAssemblyOutcome.SELECTION_UNAVAILABLE
    assert assembled.snapshot is None
