import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from importlib.resources import files
from threading import Barrier
from uuid import UUID, uuid4

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy.adapters.postgres import PostgresAccessRuleRepository
from napms.access_policy.application.materialize_rule import (
    MaterializationOutcome,
    MaterializeAllowedAccessRule,
    SubmitAccessRuleProposal,
)
from napms.access_policy.application.ports import (
    AccessRuleCommitOutcomeUnknown,
    AccessRulePersistenceError,
    AuthorityCheck,
    ConnectivityDecision,
    DecisionOutcome,
    InteractionCheck,
    InteractionOutcome,
    RuleSemanticIdentityConflict,
    TernaryOutcome,
)
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    ProposalProvenance,
    RuleSemanticIdentity,
)


pytestmark = pytest.mark.postgres
NOW = datetime(2026, 9, 8, tzinfo=timezone.utc)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_schema(postgres_dsn):
    migration = (
        files("napms.access_policy.adapters.postgres")
        .joinpath("migrations/0001_access_rules.sql")
        .read_text(encoding="utf-8")
    )
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(migration)


@pytest.fixture(autouse=True)
def clean_access_rules(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute("TRUNCATE TABLE napms_access_policy.access_rules")


class PermittedAuthority:
    def check(self, **_):
        return AuthorityCheck(TernaryOutcome.PERMITTED, "auth-1")


class ExactCatalogue:
    def resolve_directed_interaction(self, *, identity, **_):
        return InteractionCheck(InteractionOutcome.VALID, identity, "catalogue-1")


class AllowedDecisions:
    def obtain(self, *, subject):
        return ConnectivityDecision(DecisionOutcome.ALLOWED, subject, "decision-1")


class BarrierRepository:
    def __init__(self, delegate, barrier):
        self._delegate = delegate
        self._barrier = barrier

    def find_by_identity(self, identity):
        return self._delegate.find_by_identity(identity)

    def get_by_id(self, rule_id):
        return self._delegate.get_by_id(rule_id)

    def add(self, rule):
        self._barrier.wait(timeout=10)
        self._delegate.add(rule)

    def commit(self):
        self._delegate.commit()


class RollbackThenFailRepository:
    def __init__(self, delegate, connection):
        self._delegate = delegate
        self._connection = connection

    def find_by_identity(self, identity):
        return self._delegate.find_by_identity(identity)

    def get_by_id(self, rule_id):
        return self._delegate.get_by_id(rule_id)

    def add(self, rule):
        self._delegate.add(rule)

    def commit(self):
        self._connection.rollback()
        raise AccessRulePersistenceError()


class CommitThenUnknownRepository:
    def __init__(self, delegate):
        self._delegate = delegate

    def find_by_identity(self, identity):
        return self._delegate.find_by_identity(identity)

    def get_by_id(self, rule_id):
        return self._delegate.get_by_id(rule_id)

    def add(self, rule):
        self._delegate.add(rule)

    def commit(self):
        self._delegate.commit()
        raise AccessRuleCommitOutcomeUnknown()


def new_identity():
    return RuleSemanticIdentity(uuid4(), uuid4(), uuid4())


def new_rule(identity=None, rule_id=None):
    identity = identity or new_identity()
    return AccessRule.materialized_from_allowed_decision(
        rule_id=rule_id or uuid4(),
        semantic_identity=identity,
        decision=DecisionReference(
            subject=identity,
            result=ConnectivityDecisionResult.ALLOWED,
            decision_id="decision-1",
        ),
        proposal_provenance=ProposalProvenance(
            actor_id="actor-1",
            authority_scope="scope-1",
            effective_time=NOW,
            authority_reference="auth-1",
            catalogue_reference="catalogue-1",
        ),
    )


def command(identity):
    return SubmitAccessRuleProposal(
        actor_id="actor-1",
        authority_scope="scope-1",
        effective_time=NOW,
        source_component_deployment_id=identity.source_component_deployment_id,
        destination_component_deployment_id=identity.destination_component_deployment_id,
        dcs_contract_revision_id=identity.dcs_contract_revision_id,
    )


def use_case(repository, rule_id):
    return MaterializeAllowedAccessRule(
        authority=PermittedAuthority(),
        catalogue=ExactCatalogue(),
        decisions=AllowedDecisions(),
        rules=repository,
        new_rule_id=lambda: rule_id,
    )


def test_repository_round_trip_preserves_rule_and_provenance(postgres_dsn):
    rule = new_rule()
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        repository.add(rule)
        repository.commit()

        assert repository.find_by_identity(rule.semantic_identity) == rule
        assert repository.get_by_id(rule.rule_id) == rule


def test_unique_constraint_translates_to_semantic_identity_conflict(postgres_dsn):
    identity = new_identity()
    winner = new_rule(identity, UUID(int=1))
    duplicate = new_rule(identity, UUID(int=2))

    with psycopg.connect(postgres_dsn) as first_connection:
        first = PostgresAccessRuleRepository(first_connection)
        first.add(winner)
        first.commit()

    with psycopg.connect(postgres_dsn) as second_connection:
        second = PostgresAccessRuleRepository(second_connection)
        with pytest.raises(RuleSemanticIdentityConflict):
            second.add(duplicate)

        assert second.find_by_identity(identity) == winner


def test_rule_id_collision_is_not_misclassified_as_semantic_identity_conflict(postgres_dsn):
    winner = new_rule(new_identity(), UUID(int=7))
    other_identity = new_identity()
    duplicate_rule_id = new_rule(other_identity, UUID(int=7))

    with psycopg.connect(postgres_dsn) as first_connection:
        first = PostgresAccessRuleRepository(first_connection)
        first.add(winner)
        first.commit()

    with psycopg.connect(postgres_dsn) as second_connection:
        second = PostgresAccessRuleRepository(second_connection)
        with pytest.raises(AccessRulePersistenceError) as failure:
            second.add(duplicate_rule_id)

        assert not isinstance(failure.value, RuleSemanticIdentityConflict)
        assert second.find_by_identity(other_identity) is None


def test_concurrent_identical_materialization_resolves_one_authoritative_rule(postgres_dsn):
    identity = new_identity()
    barrier = Barrier(2)
    proposed_rule_ids = (UUID(int=11), UUID(int=12))

    def worker(rule_id):
        with psycopg.connect(postgres_dsn) as connection:
            repository = BarrierRepository(
                PostgresAccessRuleRepository(connection),
                barrier,
            )
            return use_case(repository, rule_id).execute(command(identity))

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(worker, proposed_rule_ids))

    assert {result.outcome for result in results} == {
        MaterializationOutcome.MATERIALIZED,
        MaterializationOutcome.RESOLVED,
    }
    assert {result.created for result in results} == {True, False}
    assert len({result.rule.rule_id for result in results}) == 1

    with psycopg.connect(postgres_dsn) as connection:
        authoritative = PostgresAccessRuleRepository(connection).find_by_identity(identity)
        assert authoritative is not None
        assert authoritative.rule_id == results[0].rule.rule_id == results[1].rule.rule_id


def test_transaction_rollback_leaves_no_authoritative_rule(postgres_dsn):
    rule = new_rule()

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        repository.add(rule)
        connection.rollback()

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        assert repository.find_by_identity(rule.semantic_identity) is None


def test_failed_commit_is_not_reported_as_materialization_success(postgres_dsn):
    identity = new_identity()

    with psycopg.connect(postgres_dsn) as connection:
        delegate = PostgresAccessRuleRepository(connection)
        repository = RollbackThenFailRepository(delegate, connection)
        with pytest.raises(AccessRulePersistenceError):
            use_case(repository, UUID(int=21)).execute(command(identity))

    with psycopg.connect(postgres_dsn) as connection:
        assert PostgresAccessRuleRepository(connection).find_by_identity(identity) is None


def test_unknown_commit_acknowledgement_is_not_reported_as_success(postgres_dsn):
    identity = new_identity()

    with psycopg.connect(postgres_dsn) as connection:
        delegate = PostgresAccessRuleRepository(connection)
        repository = CommitThenUnknownRepository(delegate)
        with pytest.raises(AccessRuleCommitOutcomeUnknown):
            use_case(repository, UUID(int=31)).execute(command(identity))

    with psycopg.connect(postgres_dsn) as connection:
        authoritative = PostgresAccessRuleRepository(connection).find_by_identity(identity)
        assert authoritative is not None
        assert authoritative.rule_id == UUID(int=31)


def test_postgres_commit_failure_maps_to_unknown_outcome():
    class CommitFailureConnection:
        def commit(self):
            raise psycopg.OperationalError("lost commit acknowledgement")

    repository = PostgresAccessRuleRepository(CommitFailureConnection())
    with pytest.raises(AccessRuleCommitOutcomeUnknown):
        repository.commit()
