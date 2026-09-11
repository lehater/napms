import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from importlib.resources import files
from threading import Barrier
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.connectivity_decision.adapters.postgres import (
    PostgresConnectivityDecisionRepository,
)
from napms.connectivity_decision.application.ports import (
    DecisionAuthorityCheck,
    DecisionCommitOutcomeUnknown,
    DecisionCurrentConflict,
    DecisionPersistenceError,
    DecisionSubjectCheck,
    SubjectOutcome,
    TernaryOutcome,
)
from napms.connectivity_decision.application.record import (
    RecordConnectivityDecision,
    RecordDecision,
    RecordDecisionOutcome,
)
from napms.connectivity_decision.application.select import (
    SelectEffectiveConnectivityDecision,
    SelectionOutcome,
)
from napms.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionEvidenceReference,
    DecisionOutcome,
    DecisionProvenance,
    DecisionSubject,
    DecisionValidity,
)


pytestmark = pytest.mark.postgres

NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=101)
DESTINATION = UUID(int=102)
DCS = UUID(int=103)
SUBJECT = DecisionSubject(SOURCE, DESTINATION, DCS)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_connectivity_decision(postgres_dsn):
    migrations = files(
        "napms.connectivity_decision.adapters.postgres"
    ).joinpath("migrations")
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        for migration in sorted(
            (path for path in migrations.iterdir() if path.name.endswith(".sql")),
            key=lambda path: path.name,
        ):
            connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_connectivity_decision(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            "TRUNCATE TABLE napms_connectivity_decision.connectivity_decisions CASCADE"
        )


class PermittedAuthority:
    def check(self, **kwargs):
        return DecisionAuthorityCheck(
            TernaryOutcome.PERMITTED,
            "decision-authority-1",
        )


class ValidCatalogue:
    def validate_decision_subject(self, *, subject, effective_time):
        return DecisionSubjectCheck(
            SubjectOutcome.VALID,
            subject,
            "catalogue-1",
        )


class BarrierRepository:
    def __init__(self, delegate, barrier):
        self.delegate = delegate
        self.barrier = barrier
        self.first_find = True

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def find_current(self, **kwargs):
        result = self.delegate.find_current(**kwargs)
        if self.first_find:
            self.first_find = False
            self.barrier.wait(timeout=10)
        return result


class RollbackCommitRepository:
    def __init__(self, delegate, connection):
        self.delegate = delegate
        self.connection = connection

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def commit(self):
        self.connection.rollback()
        raise DecisionPersistenceError("forced rollback")


def decision(
    decision_id,
    *,
    outcome=DecisionOutcome.ALLOWED,
    start=NOW,
    end=None,
    reason_code="BUSINESS_NEED",
    reason_text="Required application interaction",
    supersedes=None,
):
    return ConnectivityDecision(
        decision_id=decision_id,
        subject=SUBJECT,
        governance_scope="scope-a",
        outcome=outcome,
        validity=DecisionValidity(start, end),
        reason_code=reason_code,
        reason_text=reason_text,
        evidence_references=(
            DecisionEvidenceReference(
                "ConnectivityRequirement",
                "requirement-1",
            ),
        ),
        provenance=DecisionProvenance(
            actor_id="decider",
            decided_at=NOW,
            authority_reference="decision-authority-1",
        ),
        supersedes_decision_id=supersedes,
    )


def persist(postgres_dsn, value):
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityDecisionRepository(connection)
        repository.add(value)
        repository.commit()


def command(*, start=NOW):
    return RecordDecision(
        subject=SUBJECT,
        governance_scope="scope-a",
        outcome=DecisionOutcome.ALLOWED,
        validity=DecisionValidity(start),
        reason_code="BUSINESS_NEED",
        reason_text="Required application interaction",
        evidence_references=(
            DecisionEvidenceReference(
                "ConnectivityRequirement",
                "requirement-1",
            ),
        ),
        actor_id="decider",
        effective_time=NOW,
    )


def test_round_trip_preserves_identity_reason_evidence_and_provenance(postgres_dsn):
    original = decision(UUID(int=1))
    persist(postgres_dsn, original)

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresConnectivityDecisionRepository(connection).get_by_id(
            original.decision_id
        )

    assert reloaded == original
    assert reloaded.subject == SUBJECT
    assert reloaded.reason_code == "BUSINESS_NEED"
    assert reloaded.evidence_references[0].reference == "requirement-1"
    assert reloaded.provenance.authority_reference == "decision-authority-1"


def test_effective_selection_uses_half_open_validity(postgres_dsn):
    end = NOW + timedelta(hours=1)
    original = decision(UUID(int=2), end=end)
    persist(postgres_dsn, original)

    with psycopg.connect(postgres_dsn) as connection:
        selector = SelectEffectiveConnectivityDecision(
            decisions=PostgresConnectivityDecisionRepository(connection)
        )
        at_start = selector.execute(
            subject=SUBJECT,
            governance_scope="scope-a",
            as_of=NOW,
        )
        at_end = selector.execute(
            subject=SUBJECT,
            governance_scope="scope-a",
            as_of=end,
        )

    assert at_start.outcome is SelectionOutcome.FOUND
    assert at_start.decision == original
    assert at_end.outcome is SelectionOutcome.NOT_FOUND


def test_supersession_preserves_history_and_changes_current_from_new_start(postgres_dsn):
    first = decision(UUID(int=3))
    persist(postgres_dsn, first)
    second_start = NOW + timedelta(hours=1)
    second = decision(
        UUID(int=4),
        outcome=DecisionOutcome.NOT_ALLOWED,
        start=second_start,
        reason_code="RISK",
        reason_text="Risk not accepted",
        supersedes=first.decision_id,
    )
    persist(postgres_dsn, second)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityDecisionRepository(connection)
        before = repository.find_current(
            subject=SUBJECT,
            governance_scope="scope-a",
            as_of=NOW,
        )
        after = repository.find_current(
            subject=SUBJECT,
            governance_scope="scope-a",
            as_of=second_start,
        )
        historical = repository.get_by_id(first.decision_id)

    assert before == (first,)
    assert after == (second,)
    assert historical == first


def test_independent_overlapping_current_decision_is_rejected(postgres_dsn):
    first = decision(UUID(int=5))
    persist(postgres_dsn, first)

    overlapping = decision(
        UUID(int=6),
        start=NOW + timedelta(minutes=5),
        reason_code="OTHER",
        reason_text="Independent overlapping decision",
    )
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityDecisionRepository(connection)
        with pytest.raises(DecisionCurrentConflict):
            repository.add(overlapping)


def test_future_scheduled_decision_prevents_earlier_long_overlap(postgres_dsn):
    future = decision(
        UUID(int=7),
        start=NOW + timedelta(hours=2),
    )
    persist(postgres_dsn, future)

    earlier_long = decision(
        UUID(int=8),
        start=NOW,
        end=NOW + timedelta(hours=3),
        reason_code="EARLIER",
        reason_text="Would overlap scheduled decision",
    )
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityDecisionRepository(connection)
        with pytest.raises(DecisionCurrentConflict):
            repository.add(earlier_long)


def test_database_rejects_mutation_of_historical_decision(postgres_dsn):
    original = decision(UUID(int=9))
    persist(postgres_dsn, original)

    with psycopg.connect(postgres_dsn) as connection:
        with pytest.raises(psycopg.Error):
            connection.execute(
                """
                UPDATE napms_connectivity_decision.connectivity_decisions
                SET reason_text = 'rewritten'
                WHERE decision_id = %s
                """,
                (original.decision_id,),
            )

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresConnectivityDecisionRepository(connection).get_by_id(
            original.decision_id
        )
    assert reloaded == original


def test_repository_pages_by_governance_scope(postgres_dsn):
    one = decision(UUID(int=10))
    persist(postgres_dsn, one)

    other = ConnectivityDecision(
        decision_id=UUID(int=11),
        subject=SUBJECT,
        governance_scope="scope-b",
        outcome=DecisionOutcome.ALLOWED,
        validity=DecisionValidity(NOW),
        reason_code="OTHER",
        reason_text="Other scope",
        evidence_references=(),
        provenance=DecisionProvenance(
            actor_id="decider",
            decided_at=NOW + timedelta(minutes=1),
            authority_reference="authority-b",
        ),
    )
    persist(postgres_dsn, other)

    with psycopg.connect(postgres_dsn) as connection:
        rows = PostgresConnectivityDecisionRepository(
            connection
        ).list_by_governance_scopes(
            ("scope-a",),
            offset=0,
            limit=10,
        )

    assert rows == (one,)


def test_concurrent_identical_record_resolves_one_authoritative_decision(postgres_dsn):
    barrier = Barrier(2)

    def worker(decision_id):
        with psycopg.connect(postgres_dsn) as connection:
            repository = BarrierRepository(
                PostgresConnectivityDecisionRepository(connection),
                barrier,
            )
            return RecordConnectivityDecision(
                authority=PermittedAuthority(),
                catalogue=ValidCatalogue(),
                decisions=repository,
                id_factory=lambda: decision_id,
            ).execute(command())

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(
            executor.map(
                worker,
                (UUID(int=20), UUID(int=21)),
            )
        )

    assert {result.outcome for result in results} == {
        RecordDecisionOutcome.RECORDED,
        RecordDecisionOutcome.RESOLVED,
    }
    ids = {result.decision.decision_id for result in results}
    assert len(ids) == 1

    with psycopg.connect(postgres_dsn) as connection:
        rows = connection.execute(
            """
            SELECT count(*)
            FROM napms_connectivity_decision.connectivity_decisions
            """
        ).fetchone()
    assert rows[0] == 1


def test_rollback_does_not_leave_decision_or_report_success(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        delegate = PostgresConnectivityDecisionRepository(connection)
        repository = RollbackCommitRepository(delegate, connection)
        with pytest.raises(DecisionPersistenceError):
            RecordConnectivityDecision(
                authority=PermittedAuthority(),
                catalogue=ValidCatalogue(),
                decisions=repository,
                id_factory=lambda: UUID(int=30),
            ).execute(command())

    with psycopg.connect(postgres_dsn) as connection:
        found = PostgresConnectivityDecisionRepository(connection).find_current(
            subject=SUBJECT,
            governance_scope="scope-a",
            as_of=NOW,
        )
    assert found == ()


def test_commit_failure_maps_to_unknown_outcome():
    class CommitFailureConnection:
        def commit(self):
            raise psycopg.OperationalError("lost commit acknowledgement")

    repository = PostgresConnectivityDecisionRepository(
        CommitFailureConnection()
    )

    with pytest.raises(DecisionCommitOutcomeUnknown):
        repository.commit()
