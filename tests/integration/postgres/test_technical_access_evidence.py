import os
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from importlib.resources import files
from threading import Barrier
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.technical_access_evidence.adapters.postgres import (
    PostgresTechnicalAccessEvidenceRepository,
)
from napms.technical_access_evidence.application.ports import (
    EvidenceCaptureConflict,
    EvidenceCommitOutcomeUnknown,
    EvidencePersistenceError,
    EvidenceSetFilters,
)
from napms.technical_access_evidence.application.record import (
    RecordEvidenceOutcome,
    RecordEvidenceSet,
    RecordTechnicalAccessEvidenceSet,
)
from napms.technical_access_evidence.domain.model import (
    AddressConstraint,
    AddressRange,
    EvidenceAction,
    EvidenceKind,
    EvidenceSourceReference,
    EvidenceTime,
    PortConstraint,
    PortRange,
    ProtocolSelector,
    SourceCaptureReference,
    SourceScopeReference,
    TechnicalAccessEntry,
    TechnicalAccessEntryPayload,
    TechnicalAccessEvidenceSet,
    TechnicalAccessPredicate,
)


pytestmark = pytest.mark.postgres

NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = EvidenceSourceReference("controller", "fw-a")
SCOPE = SourceScopeReference("policy-package-a")
CAPTURE = SourceCaptureReference("capture-1")


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip(
            "NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests"
        )
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_tae(postgres_dsn):
    migrations = files(
        "napms.technical_access_evidence.adapters.postgres"
    ).joinpath("migrations")
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        for migration in sorted(
            (
                path
                for path in migrations.iterdir()
                if path.name.endswith(".sql")
            ),
            key=lambda path: path.name,
        ):
            connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_tae(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_technical_access_evidence.evidence_sets
            """
        )


def predicate(
    *,
    protocol=6,
    source_first="10.0.0.1",
    source_last="10.0.0.10",
    destination_first="2001:db8::1",
    destination_last="2001:db8::ffff",
    destination_port=443,
):
    return TechnicalAccessPredicate(
        source_addresses=AddressConstraint.ranged(
            AddressRange(source_first, source_last),
        ),
        destination_addresses=AddressConstraint.ranged(
            AddressRange(destination_first, destination_last),
        ),
        protocol=ProtocolSelector.ip_protocol(protocol),
        source_ports=PortConstraint.any(),
        destination_ports=PortConstraint.ranged(
            PortRange(destination_port, destination_port),
        ),
    )


def payload(
    *,
    reference="rule-1",
    position=10,
    destination_port=443,
):
    return TechnicalAccessEntryPayload(
        predicate=predicate(destination_port=destination_port),
        action=EvidenceAction.PERMIT,
        source_entry_reference=reference,
        source_position=position,
    )


def evidence_set(
    evidence_set_id=UUID(int=1),
    *,
    source=SOURCE,
    scope=SCOPE,
    capture=CAPTURE,
    kind=EvidenceKind.CONFIGURED,
    evidence_time=None,
    recorded_at=NOW,
    payloads=None,
):
    values = payloads if payloads is not None else (payload(),)
    return TechnicalAccessEvidenceSet(
        evidence_set_id=evidence_set_id,
        kind=kind,
        source=source,
        source_scope=scope,
        source_capture_reference=capture,
        evidence_time=(
            evidence_time
            if evidence_time is not None
            else EvidenceTime.instant(NOW - timedelta(minutes=5))
        ),
        recorded_at=recorded_at,
        entries=tuple(
            TechnicalAccessEntry(
                evidence_entry_id=UUID(int=100 + index),
                payload=value,
            )
            for index, value in enumerate(values)
        ),
    )


def persist(postgres_dsn, value):
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresTechnicalAccessEvidenceRepository(connection)
        repository.add(value)
        repository.commit()


def command_from(value):
    return RecordEvidenceSet(
        kind=value.kind,
        source=value.source,
        source_scope=value.source_scope,
        source_capture_reference=value.source_capture_reference,
        evidence_time=value.evidence_time,
        entries=tuple(entry.payload for entry in value.entries),
    )


def test_round_trip_preserves_full_source_qualified_evidence(postgres_dsn):
    duplicate = payload(reference=None, position=None)
    original = evidence_set(
        payloads=(
            duplicate,
            duplicate,
            payload(reference="rule-2", position=20, destination_port=8443),
        ),
    )
    persist(postgres_dsn, original)

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresTechnicalAccessEvidenceRepository(
            connection
        ).get_by_id(original.evidence_set_id)

    assert reloaded == original
    assert len(reloaded.entries) == 3
    assert reloaded.entries[0].payload == reloaded.entries[1].payload
    assert reloaded.entries[0].evidence_entry_id != reloaded.entries[1].evidence_entry_id
    assert (
        reloaded.entries[0].payload.predicate.destination_addresses.ranges[0].first
        == "2001:db8::1"
    )


def test_empty_unknown_time_capture_round_trips(postgres_dsn):
    original = evidence_set(
        kind=EvidenceKind.IMPORTED,
        evidence_time=EvidenceTime.unknown(),
        payloads=(),
    )
    persist(postgres_dsn, original)

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresTechnicalAccessEvidenceRepository(
            connection
        ).get_by_id(original.evidence_set_id)

    assert reloaded == original
    assert reloaded.entries == ()
    assert reloaded.evidence_time == EvidenceTime.unknown()


def test_window_time_and_list_filters_round_trip(postgres_dsn):
    first = evidence_set(
        UUID(int=1),
        recorded_at=NOW,
    )
    second = evidence_set(
        UUID(int=2),
        source=EvidenceSourceReference("flow", "sensor-a"),
        scope=SourceScopeReference("query-a"),
        capture=SourceCaptureReference("capture-2"),
        kind=EvidenceKind.TRAFFIC_DERIVED,
        evidence_time=EvidenceTime.window(
            NOW - timedelta(hours=1),
            NOW,
        ),
        recorded_at=NOW + timedelta(minutes=1),
        payloads=(),
    )
    persist(postgres_dsn, first)
    persist(postgres_dsn, second)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresTechnicalAccessEvidenceRepository(connection)
        rows = repository.list(
            filters=EvidenceSetFilters(
                source=second.source,
                source_scope=second.source_scope,
                kind=EvidenceKind.TRAFFIC_DERIVED,
                recorded_from=NOW,
                recorded_until=NOW + timedelta(hours=1),
            ),
            offset=0,
            limit=10,
        )

    assert rows == (second,)


def test_database_rejects_evidence_mutation(postgres_dsn):
    original = evidence_set()
    persist(postgres_dsn, original)

    with psycopg.connect(postgres_dsn) as connection:
        with pytest.raises(psycopg.Error):
            connection.execute(
                """
                UPDATE napms_technical_access_evidence.evidence_sets
                SET source_scope_reference = 'rewritten'
                WHERE evidence_set_id = %s
                """,
                (original.evidence_set_id,),
            )

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresTechnicalAccessEvidenceRepository(
            connection
        ).get_by_id(original.evidence_set_id)
    assert reloaded == original


def test_same_source_capture_is_unique(postgres_dsn):
    first = evidence_set(UUID(int=1))
    second = evidence_set(
        UUID(int=2),
        payloads=(payload(destination_port=8443),),
    )
    persist(postgres_dsn, first)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresTechnicalAccessEvidenceRepository(connection)
        with pytest.raises(EvidenceCaptureConflict):
            repository.add(second)


def test_generated_set_id_collision_is_persistence_failure(postgres_dsn):
    first = evidence_set(UUID(int=1))
    second = evidence_set(
        UUID(int=1),
        source=EvidenceSourceReference("controller", "fw-b"),
        capture=SourceCaptureReference("capture-2"),
    )
    persist(postgres_dsn, first)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresTechnicalAccessEvidenceRepository(connection)
        with pytest.raises(EvidencePersistenceError):
            repository.add(second)


class BarrierRepository:
    def __init__(self, delegate, barrier):
        self.delegate = delegate
        self.barrier = barrier
        self.first_find = True

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def find_by_capture(self, **kwargs):
        result = self.delegate.find_by_capture(**kwargs)
        if self.first_find:
            self.first_find = False
            self.barrier.wait(timeout=10)
        return result


def test_concurrent_identical_record_resolves_one_authoritative_set(postgres_dsn):
    barrier = Barrier(2)
    draft = evidence_set()

    def worker(set_id):
        with psycopg.connect(postgres_dsn) as connection:
            counter = iter(
                (
                    set_id,
                    UUID(int=1000 + set_id.int),
                )
            )
            repository = BarrierRepository(
                PostgresTechnicalAccessEvidenceRepository(connection),
                barrier,
            )
            return RecordTechnicalAccessEvidenceSet(
                evidence_sets=repository,
                set_id_factory=lambda: next(counter),
                entry_id_factory=lambda: next(counter),
                clock=lambda: NOW,
            ).execute(command_from(draft))

    with ThreadPoolExecutor(max_workers=2) as executor:
        results = tuple(
            executor.map(
                worker,
                (UUID(int=20), UUID(int=21)),
            )
        )

    assert {result.outcome for result in results} == {
        RecordEvidenceOutcome.RECORDED,
        RecordEvidenceOutcome.RESOLVED,
    }
    ids = {result.evidence_set.evidence_set_id for result in results}
    assert len(ids) == 1

    with psycopg.connect(postgres_dsn) as connection:
        count = connection.execute(
            """
            SELECT count(*)
            FROM napms_technical_access_evidence.evidence_sets
            """
        ).fetchone()[0]
    assert count == 1


def test_existing_capture_with_different_payload_is_application_conflict(postgres_dsn):
    original = evidence_set()
    persist(postgres_dsn, original)

    with psycopg.connect(postgres_dsn) as connection:
        result = RecordTechnicalAccessEvidenceSet(
            evidence_sets=PostgresTechnicalAccessEvidenceRepository(
                connection
            ),
            set_id_factory=lambda: UUID(int=2),
            entry_id_factory=lambda: UUID(int=200),
            clock=lambda: NOW + timedelta(minutes=5),
        ).execute(
            RecordEvidenceSet(
                kind=original.kind,
                source=original.source,
                source_scope=original.source_scope,
                source_capture_reference=original.source_capture_reference,
                evidence_time=original.evidence_time,
                entries=(payload(destination_port=8443),),
            )
        )

    assert result.outcome is RecordEvidenceOutcome.CAPTURE_CONFLICT
    assert result.evidence_set is None


def test_repository_maps_commit_failure_to_unknown_outcome():
    class CommitFailureConnection:
        def commit(self):
            raise psycopg.OperationalError("lost commit acknowledgement")

    repository = PostgresTechnicalAccessEvidenceRepository(
        CommitFailureConnection()
    )

    with pytest.raises(EvidenceCommitOutcomeUnknown):
        repository.commit()


def test_corrupt_persisted_json_fails_closed(postgres_dsn):
    original = evidence_set()
    persist(postgres_dsn, original)

    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            DROP TRIGGER trg_tae_evidence_set_immutable
            ON napms_technical_access_evidence.evidence_sets
            """
        )
        connection.execute(
            """
            UPDATE napms_technical_access_evidence.evidence_sets
            SET entries = '[{"broken": true}]'::jsonb
            WHERE evidence_set_id = %s
            """,
            (original.evidence_set_id,),
        )

    try:
        with psycopg.connect(postgres_dsn) as connection:
            with pytest.raises(EvidencePersistenceError):
                PostgresTechnicalAccessEvidenceRepository(
                    connection
                ).get_by_id(original.evidence_set_id)
    finally:
        migration = files(
            "napms.technical_access_evidence.adapters.postgres"
        ).joinpath("migrations/0001_evidence_sets.sql")
        with psycopg.connect(postgres_dsn, autocommit=True) as connection:
            connection.execute(migration.read_text(encoding="utf-8"))
