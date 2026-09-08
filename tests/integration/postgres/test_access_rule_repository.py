import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
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
    AuthorityAction,
    AuthorityCheck,
    ConnectivityDecision,
    DecisionOutcome,
    InteractionCheck,
    InteractionOutcome,
    RuleSemanticIdentityConflict,
    TernaryOutcome,
)
from napms.access_policy.application.select_effective_policy import (
    EffectivePolicySelectionOutcome,
    SelectAccessPolicyEffectiveDesiredPolicy,
    SelectEffectiveDesiredPolicy,
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
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    EffectiveWindow,
    OperationalState,
    ProposalProvenance,
    RuleSemanticIdentity,
)


pytestmark = pytest.mark.postgres
NOW = datetime(2026, 9, 8, tzinfo=timezone.utc)
MUTATION_TIME = datetime(2026, 9, 8, 19, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_schema(postgres_dsn):
    migrations = files("napms.access_policy.adapters.postgres").joinpath("migrations")
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        for migration in sorted(
            (path for path in migrations.iterdir() if path.name.endswith(".sql")),
            key=lambda path: path.name,
        ):
            connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_access_rules(postgres_dsn):
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


class PermittedAuthority:
    def __init__(self, reference="auth-1"):
        self.reference = reference
        self.calls = []

    def check(self, **kwargs):
        self.calls.append(kwargs)
        return AuthorityCheck(TernaryOutcome.PERMITTED, self.reference)


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

    def save(self, rule):
        self._delegate.save(rule)

    def commit(self):
        self._delegate.commit()


class SaveBarrierRepository:
    def __init__(self, delegate, barrier):
        self._delegate = delegate
        self._barrier = barrier

    def find_by_identity(self, identity):
        return self._delegate.find_by_identity(identity)

    def get_by_id(self, rule_id):
        return self._delegate.get_by_id(rule_id)

    def add(self, rule):
        self._delegate.add(rule)

    def save(self, rule):
        self._barrier.wait(timeout=10)
        self._delegate.save(rule)

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

    def save(self, rule):
        self._delegate.save(rule)

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

    def save(self, rule):
        self._delegate.save(rule)

    def commit(self):
        self._delegate.commit()
        raise AccessRuleCommitOutcomeUnknown()


def new_identity():
    return RuleSemanticIdentity(uuid4(), uuid4(), uuid4())


def new_rule(identity=None, rule_id=None, scope="scope-1"):
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
            authority_scope=scope,
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


def materialization_service(repository, rule_id):
    return MaterializeAllowedAccessRule(
        authority=PermittedAuthority(),
        catalogue=ExactCatalogue(),
        decisions=AllowedDecisions(),
        rules=repository,
        new_rule_id=lambda: rule_id,
    )


def state_command(rule_id, target=OperationalState.INACTIVE):
    return SetRuleOperationalState(
        rule_id=rule_id,
        target_state=target,
        actor_id="state-operator",
        effective_time=MUTATION_TIME,
    )


def state_service(repository, authority=None):
    return SetAccessRuleOperationalState(
        authority=authority or PermittedAuthority("state-auth-1"),
        rules=repository,
    )


def persist_rule(postgres_dsn, rule):
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        repository.add(rule)
        repository.commit()


def test_repository_round_trip_preserves_rule_and_provenance(postgres_dsn):
    rule = new_rule()
    persist_rule(postgres_dsn, rule)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        assert repository.find_by_identity(rule.semantic_identity) == rule
        assert repository.get_by_id(rule.rule_id) == rule


def test_unique_constraint_translates_to_semantic_identity_conflict(postgres_dsn):
    identity = new_identity()
    winner = new_rule(identity, UUID(int=1))
    duplicate = new_rule(identity, UUID(int=2))

    persist_rule(postgres_dsn, winner)

    with psycopg.connect(postgres_dsn) as second_connection:
        second = PostgresAccessRuleRepository(second_connection)
        with pytest.raises(RuleSemanticIdentityConflict):
            second.add(duplicate)

        assert second.find_by_identity(identity) == winner


def test_rule_id_collision_is_not_misclassified_as_semantic_identity_conflict(postgres_dsn):
    winner = new_rule(new_identity(), UUID(int=7))
    other_identity = new_identity()
    duplicate_rule_id = new_rule(other_identity, UUID(int=7))

    persist_rule(postgres_dsn, winner)

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
            return materialization_service(repository, rule_id).execute(command(identity))

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
            materialization_service(repository, UUID(int=21)).execute(command(identity))

    with psycopg.connect(postgres_dsn) as connection:
        assert PostgresAccessRuleRepository(connection).find_by_identity(identity) is None


def test_unknown_commit_acknowledgement_is_not_reported_as_success(postgres_dsn):
    identity = new_identity()

    with psycopg.connect(postgres_dsn) as connection:
        delegate = PostgresAccessRuleRepository(connection)
        repository = CommitThenUnknownRepository(delegate)
        with pytest.raises(AccessRuleCommitOutcomeUnknown):
            materialization_service(repository, UUID(int=31)).execute(command(identity))

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


def test_state_transition_round_trip_preserves_identity_governance_decision_and_audit(
    postgres_dsn,
):
    rule = new_rule(rule_id=UUID(int=41))
    persist_rule(postgres_dsn, rule)

    authority = PermittedAuthority("state-auth-1")
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        result = state_service(repository, authority).execute(state_command(rule.rule_id))

    assert result.outcome is OperationalStateMutationOutcome.UPDATED

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.operational_state is OperationalState.INACTIVE
    assert reloaded.rule_id == rule.rule_id
    assert reloaded.semantic_identity == rule.semantic_identity
    assert reloaded.decision == rule.decision
    assert reloaded.governance_scope == "scope-1"
    assert len(reloaded.operational_state_history) == 1
    audit = reloaded.operational_state_history[0]
    assert audit.from_state is OperationalState.ACTIVE
    assert audit.to_state is OperationalState.INACTIVE
    assert audit.actor_id == "state-operator"
    assert audit.effective_time == MUTATION_TIME
    assert audit.governance_scope == "scope-1"
    assert audit.authority_reference == "state-auth-1"
    assert authority.calls[0]["scope"] == "scope-1"


def test_second_state_transition_appends_audit_history(postgres_dsn):
    rule = new_rule(rule_id=UUID(int=42))
    persist_rule(postgres_dsn, rule)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        first = state_service(repository).execute(state_command(rule.rule_id))
        assert first.outcome is OperationalStateMutationOutcome.UPDATED

    second_time = datetime(2026, 9, 8, 20, 0, tzinfo=timezone.utc)
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        second = state_service(repository).execute(
            SetRuleOperationalState(
                rule_id=rule.rule_id,
                target_state=OperationalState.ACTIVE,
                actor_id="state-operator-2",
                effective_time=second_time,
            )
        )
        assert second.outcome is OperationalStateMutationOutcome.UPDATED

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.operational_state is OperationalState.ACTIVE
    assert len(reloaded.operational_state_history) == 2
    assert reloaded.operational_state_history[0].to_state is OperationalState.INACTIVE
    assert reloaded.operational_state_history[1].from_state is OperationalState.INACTIVE
    assert reloaded.operational_state_history[1].to_state is OperationalState.ACTIVE


def test_state_and_audit_rollback_together_on_failed_commit(postgres_dsn):
    rule = new_rule(rule_id=UUID(int=43))
    persist_rule(postgres_dsn, rule)

    with psycopg.connect(postgres_dsn) as connection:
        delegate = PostgresAccessRuleRepository(connection)
        repository = RollbackThenFailRepository(delegate, connection)
        with pytest.raises(AccessRulePersistenceError):
            state_service(repository).execute(state_command(rule.rule_id))

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.operational_state is OperationalState.ACTIVE
    assert reloaded.operational_state_history == ()


def test_unknown_state_commit_acknowledgement_is_not_reported_as_success(postgres_dsn):
    rule = new_rule(rule_id=UUID(int=44))
    persist_rule(postgres_dsn, rule)

    with psycopg.connect(postgres_dsn) as connection:
        delegate = PostgresAccessRuleRepository(connection)
        repository = CommitThenUnknownRepository(delegate)
        with pytest.raises(AccessRuleCommitOutcomeUnknown):
            state_service(repository).execute(state_command(rule.rule_id))

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.operational_state is OperationalState.INACTIVE
    assert len(reloaded.operational_state_history) == 1


def test_concurrent_same_target_state_mutation_has_one_accepted_transition(postgres_dsn):
    rule = new_rule(rule_id=UUID(int=45))
    persist_rule(postgres_dsn, rule)
    barrier = Barrier(2)

    def worker(actor_id):
        try:
            with psycopg.connect(postgres_dsn) as connection:
                repository = SaveBarrierRepository(
                    PostgresAccessRuleRepository(connection),
                    barrier,
                )
                return state_service(repository).execute(
                    SetRuleOperationalState(
                        rule_id=rule.rule_id,
                        target_state=OperationalState.INACTIVE,
                        actor_id=actor_id,
                        effective_time=MUTATION_TIME,
                    )
                )
        except AccessRulePersistenceError as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(worker, ("operator-a", "operator-b")))

    assert sum(
        isinstance(result, AccessRulePersistenceError) for result in results
    ) == 1
    successful = [
        result
        for result in results
        if not isinstance(result, AccessRulePersistenceError)
    ]
    assert len(successful) == 1
    assert successful[0].outcome is OperationalStateMutationOutcome.UPDATED

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.operational_state is OperationalState.INACTIVE
    assert len(reloaded.operational_state_history) == 1


WINDOW_START = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)
WINDOW_END = datetime(2026, 9, 10, 18, 0, tzinfo=timezone.utc)


def window_command(rule_id, window):
    return SetRuleEffectiveWindow(
        rule_id=rule_id,
        window=window,
        actor_id="window-operator",
        effective_time=MUTATION_TIME,
    )


def window_service(repository, authority=None):
    return SetAccessRuleEffectiveWindow(
        authority=authority or PermittedAuthority("window-auth-1"),
        rules=repository,
    )


def selection_service(repository, authority=None):
    return SelectAccessPolicyEffectiveDesiredPolicy(
        authority=authority or PermittedAuthority("read-auth-1"),
        rules=repository,
    )


def test_repository_lists_exact_governance_scope(postgres_dsn):
    scope_one = new_rule(rule_id=UUID(int=51), scope="scope-1")
    scope_two = new_rule(rule_id=UUID(int=52), scope="scope-2")
    persist_rule(postgres_dsn, scope_one)
    persist_rule(postgres_dsn, scope_two)

    with psycopg.connect(postgres_dsn) as connection:
        rules = PostgresAccessRuleRepository(connection).list_by_governance_scope(
            "scope-1"
        )

    assert rules == (scope_one,)


def test_repository_pages_rules_across_authorized_governance_scopes(postgres_dsn):
    scope_a = new_rule(rule_id=UUID(int=61), scope="scope-a")
    scope_b = new_rule(rule_id=UUID(int=62), scope="scope-b")
    scope_c = new_rule(rule_id=UUID(int=63), scope="scope-c")
    for rule in (scope_a, scope_b, scope_c):
        persist_rule(postgres_dsn, rule)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        first = repository.list_by_governance_scopes(
            ("scope-a", "scope-c"),
            offset=0,
            limit=1,
        )
        second = repository.list_by_governance_scopes(
            ("scope-a", "scope-c"),
            offset=1,
            limit=2,
        )

    assert first == (scope_a,)
    assert second == (scope_c,)


def test_effective_window_round_trip_preserves_identity_state_decision_and_audit(
    postgres_dsn,
):
    rule = new_rule(rule_id=UUID(int=53))
    persist_rule(postgres_dsn, rule)
    window = EffectiveWindow(WINDOW_START, WINDOW_END)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        result = window_service(repository).execute(
            window_command(rule.rule_id, window)
        )

    assert result.outcome is EffectiveWindowMutationOutcome.UPDATED

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.rule_id == rule.rule_id
    assert reloaded.semantic_identity == rule.semantic_identity
    assert reloaded.decision == rule.decision
    assert reloaded.operational_state is OperationalState.ACTIVE
    assert reloaded.governance_scope == "scope-1"
    assert reloaded.effective_window == window
    assert len(reloaded.effective_window_history) == 1
    audit = reloaded.effective_window_history[0]
    assert audit.previous_window is None
    assert audit.new_window == window
    assert audit.actor_id == "window-operator"
    assert audit.effective_time == MUTATION_TIME
    assert audit.governance_scope == "scope-1"
    assert audit.authority_reference == "window-auth-1"


def test_effective_window_remove_appends_history(postgres_dsn):
    rule = new_rule(rule_id=UUID(int=54))
    persist_rule(postgres_dsn, rule)
    window = EffectiveWindow(WINDOW_START, WINDOW_END)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        first = window_service(repository).execute(
            window_command(rule.rule_id, window)
        )
        assert first.outcome is EffectiveWindowMutationOutcome.UPDATED

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        second = window_service(repository).execute(
            SetRuleEffectiveWindow(
                rule_id=rule.rule_id,
                window=None,
                actor_id="window-remover",
                effective_time=MUTATION_TIME + timedelta(minutes=1),
            )
        )
        assert second.outcome is EffectiveWindowMutationOutcome.UPDATED

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.effective_window is None
    assert len(reloaded.effective_window_history) == 2
    assert reloaded.effective_window_history[0].new_window == window
    assert reloaded.effective_window_history[1].previous_window == window
    assert reloaded.effective_window_history[1].new_window is None


def test_state_and_window_changes_can_interleave_without_losing_either_history(
    postgres_dsn,
):
    rule = new_rule(rule_id=UUID(int=55))
    persist_rule(postgres_dsn, rule)
    window = EffectiveWindow(WINDOW_START, WINDOW_END)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        assert (
            state_service(repository).execute(state_command(rule.rule_id)).outcome
            is OperationalStateMutationOutcome.UPDATED
        )

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        assert (
            window_service(repository).execute(
                window_command(rule.rule_id, window)
            ).outcome
            is EffectiveWindowMutationOutcome.UPDATED
        )

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        assert (
            state_service(repository).execute(
                SetRuleOperationalState(
                    rule_id=rule.rule_id,
                    target_state=OperationalState.ACTIVE,
                    actor_id="state-operator-2",
                    effective_time=MUTATION_TIME + timedelta(minutes=2),
                )
            ).outcome
            is OperationalStateMutationOutcome.UPDATED
        )

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.operational_state is OperationalState.ACTIVE
    assert reloaded.effective_window == window
    assert len(reloaded.operational_state_history) == 2
    assert len(reloaded.effective_window_history) == 1


def test_window_and_audit_rollback_together_on_failed_commit(postgres_dsn):
    rule = new_rule(rule_id=UUID(int=56))
    persist_rule(postgres_dsn, rule)
    window = EffectiveWindow(WINDOW_START, WINDOW_END)

    with psycopg.connect(postgres_dsn) as connection:
        delegate = PostgresAccessRuleRepository(connection)
        repository = RollbackThenFailRepository(delegate, connection)
        with pytest.raises(AccessRulePersistenceError):
            window_service(repository).execute(window_command(rule.rule_id, window))

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.effective_window is None
    assert reloaded.effective_window_history == ()


def test_unknown_window_commit_acknowledgement_is_not_reported_as_success(
    postgres_dsn,
):
    rule = new_rule(rule_id=UUID(int=57))
    persist_rule(postgres_dsn, rule)
    window = EffectiveWindow(WINDOW_START, WINDOW_END)

    with psycopg.connect(postgres_dsn) as connection:
        delegate = PostgresAccessRuleRepository(connection)
        repository = CommitThenUnknownRepository(delegate)
        with pytest.raises(AccessRuleCommitOutcomeUnknown):
            window_service(repository).execute(window_command(rule.rule_id, window))

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.effective_window == window
    assert len(reloaded.effective_window_history) == 1


def test_concurrent_same_window_mutation_has_one_accepted_change(postgres_dsn):
    rule = new_rule(rule_id=UUID(int=58))
    persist_rule(postgres_dsn, rule)
    window = EffectiveWindow(WINDOW_START, WINDOW_END)
    barrier = Barrier(2)

    def worker(actor_id):
        try:
            with psycopg.connect(postgres_dsn) as connection:
                repository = SaveBarrierRepository(
                    PostgresAccessRuleRepository(connection),
                    barrier,
                )
                return window_service(repository).execute(
                    SetRuleEffectiveWindow(
                        rule_id=rule.rule_id,
                        window=window,
                        actor_id=actor_id,
                        effective_time=MUTATION_TIME,
                    )
                )
        except AccessRulePersistenceError as exc:
            return exc

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = list(executor.map(worker, ("window-a", "window-b")))

    assert sum(
        isinstance(result, AccessRulePersistenceError) for result in results
    ) == 1
    successful = [
        result
        for result in results
        if not isinstance(result, AccessRulePersistenceError)
    ]
    assert len(successful) == 1
    assert successful[0].outcome is EffectiveWindowMutationOutcome.UPDATED

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresAccessRuleRepository(connection).get_by_id(rule.rule_id)

    assert reloaded.effective_window == window
    assert len(reloaded.effective_window_history) == 1


def test_effective_policy_selection_uses_postgres_scope_read_and_core_as_of_logic(
    postgres_dsn,
):
    always = new_rule(rule_id=UUID(int=61), scope="scope-1")
    in_window = new_rule(rule_id=UUID(int=62), scope="scope-1")
    ended = new_rule(rule_id=UUID(int=63), scope="scope-1")
    suspended = new_rule(rule_id=UUID(int=64), scope="scope-1")
    other_scope = new_rule(rule_id=UUID(int=65), scope="scope-2")
    for rule in (always, in_window, ended, suspended, other_scope):
        persist_rule(postgres_dsn, rule)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        assert (
            window_service(repository).execute(
                window_command(
                    in_window.rule_id,
                    EffectiveWindow(WINDOW_START, WINDOW_END),
                )
            ).outcome
            is EffectiveWindowMutationOutcome.UPDATED
        )

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        assert (
            window_service(repository).execute(
                window_command(
                    ended.rule_id,
                    EffectiveWindow(
                        WINDOW_START - timedelta(hours=2),
                        WINDOW_START,
                    ),
                )
            ).outcome
            is EffectiveWindowMutationOutcome.UPDATED
        )

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        assert (
            state_service(repository).execute(
                state_command(suspended.rule_id)
            ).outcome
            is OperationalStateMutationOutcome.UPDATED
        )

    authority = PermittedAuthority("read-auth-1")
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAccessRuleRepository(connection)
        result = selection_service(repository, authority).execute(
            SelectEffectiveDesiredPolicy(
                scope="scope-1",
                as_of=WINDOW_START,
                actor_id="reader-1",
            )
        )

    assert result.outcome is EffectivePolicySelectionOutcome.SELECTED
    assert tuple(rule.rule_id for rule in result.rules) == (
        UUID(int=61),
        UUID(int=62),
    )
    assert result.authority_reference == "read-auth-1"
    assert authority.calls == [
        {
            "actor_id": "reader-1",
            "action": AuthorityAction.READ_EFFECTIVE_DESIRED_POLICY,
            "scope": "scope-1",
            "effective_time": WINDOW_START,
        }
    ]
