import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.contexts.access_policy.infrastructure.integrations.connectivity_decision import (
    ConnectivityDecisionConsumerAdapter,
)
from napms.contexts.access_policy.infrastructure.persistence.postgres import PostgresAccessRuleRepository
from napms.contexts.access_policy.application.materialize_rule import (
    MaterializationOutcome,
    MaterializeAllowedAccessRule,
    SubmitAccessRuleProposal,
)
from napms.contexts.access_policy.application.ports import (
    AuthorityCheck,
    InteractionCheck,
    InteractionOutcome,
    TernaryOutcome,
)
from napms.contexts.connectivity_decision.infrastructure.persistence.postgres import (
    PostgresConnectivityDecisionRepository,
)
from napms.contexts.connectivity_decision.application.select import (
    SelectEffectiveConnectivityDecision,
)
from napms.contexts.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionOutcome,
    DecisionProvenance,
    DecisionSubject,
    DecisionValidity,
)
from napms.platform.database.migrations import apply_postgres_migrations


pytestmark = pytest.mark.postgres

NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=6101)
DESTINATION = UUID(int=6102)
DCS = UUID(int=6103)
DECISION_ID = UUID(int=6104)
RULE_ID = UUID(int=6105)
SCOPE = "scope-i16b"
SUBJECT = DecisionSubject(SOURCE, DESTINATION, DCS)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_i16b(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        apply_postgres_migrations(connection)


@pytest.fixture(autouse=True)
def clean_i16b(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute("TRUNCATE TABLE napms_access_policy.access_rules CASCADE")
        connection.execute(
            "TRUNCATE TABLE napms_connectivity_decision.connectivity_decisions CASCADE"
        )


class PermittedProposalAuthority:
    def check(self, **_):
        return AuthorityCheck(TernaryOutcome.PERMITTED, "proposal-authority-i16b")


class ValidInteractionCatalogue:
    def resolve_directed_interaction(self, *, identity, **_):
        return InteractionCheck(
            InteractionOutcome.VALID,
            identity,
            "catalogue-i16b",
        )


def proposal():
    return SubmitAccessRuleProposal(
        actor_id="proposer-i16b",
        authority_scope=SCOPE,
        effective_time=NOW,
        source_component_deployment_id=SOURCE,
        destination_component_deployment_id=DESTINATION,
        dcs_contract_revision_id=DCS,
    )


def durable_decision(
    *,
    outcome=DecisionOutcome.ALLOWED,
    valid_from=NOW - timedelta(hours=1),
    valid_until=NOW + timedelta(hours=1),
):
    return ConnectivityDecision(
        decision_id=DECISION_ID,
        subject=SUBJECT,
        governance_scope=SCOPE,
        outcome=outcome,
        validity=DecisionValidity(valid_from, valid_until),
        reason_code="I16B_TEST",
        reason_text="Durable Decision consumed by Access Policy.",
        evidence_references=(),
        provenance=DecisionProvenance(
            actor_id="decider-i16b",
            decided_at=NOW - timedelta(hours=2),
            authority_reference="decision-authority-i16b",
        ),
    )


def persist_decision(connection, decision):
    repository = PostgresConnectivityDecisionRepository(connection)
    repository.add(decision)
    repository.commit()


def materialize(postgres_dsn):
    with (
        psycopg.connect(postgres_dsn) as decision_connection,
        psycopg.connect(postgres_dsn) as access_policy_connection,
    ):
        decision_repository = PostgresConnectivityDecisionRepository(decision_connection)
        rules = PostgresAccessRuleRepository(access_policy_connection)
        result = MaterializeAllowedAccessRule(
            authority=PermittedProposalAuthority(),
            catalogue=ValidInteractionCatalogue(),
            decisions=ConnectivityDecisionConsumerAdapter(
                select_effective_decision=SelectEffectiveConnectivityDecision(
                    decisions=decision_repository
                )
            ),
            rules=rules,
            new_rule_id=lambda: RULE_ID,
        ).execute(proposal())
        persisted = rules.find_by_identity(proposal().semantic_identity)
        return result, persisted


def test_durable_allowed_decision_materializes_access_rule(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        persist_decision(connection, durable_decision())

    result, persisted = materialize(postgres_dsn)

    assert result.outcome is MaterializationOutcome.MATERIALIZED
    assert result.rule == persisted
    assert result.rule.decision.decision_id == str(DECISION_ID)
    assert result.rule.governance_scope == SCOPE


def test_durable_not_allowed_decision_creates_no_access_rule(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        persist_decision(
            connection,
            durable_decision(outcome=DecisionOutcome.NOT_ALLOWED),
        )

    result, persisted = materialize(postgres_dsn)

    assert result.outcome is MaterializationOutcome.NOT_ALLOWED
    assert persisted is None


@pytest.mark.parametrize("decision", [None, durable_decision(valid_until=NOW)])
def test_missing_or_expired_decision_fails_closed(postgres_dsn, decision):
    if decision is not None:
        with psycopg.connect(postgres_dsn) as connection:
            persist_decision(connection, decision)

    result, persisted = materialize(postgres_dsn)

    assert result.outcome is MaterializationOutcome.DECISION_UNKNOWN
    assert persisted is None
