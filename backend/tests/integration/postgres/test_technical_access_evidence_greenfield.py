import json
import os

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.platform.bootstrap.config import ApplicationConfig, PostgresConfig
from napms.platform.bootstrap.greenfield import apply_greenfield_migrations
from napms.platform.bootstrap.technical_access_evidence import (
    open_technical_access_evidence_scope,
)
from napms.contexts.technical_access_evidence.presentation.imports.local_json import (
    LocalEvidenceImportAdapter,
    LocalEvidenceImportError,
)
from napms.contexts.technical_access_evidence.application.read import (
    EvidenceSetDetailOutcome,
)
from napms.contexts.technical_access_evidence.application.record import (
    RecordEvidenceOutcome,
)


pytestmark = pytest.mark.postgres


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip(
            "NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests"
        )
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
def clean_tae(postgres_dsn, greenfield_config):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            "TRUNCATE TABLE napms_technical_access_evidence.evidence_sets"
        )


def import_document(*, entries):
    return {
        "source_reference": "local-fixture-a",
        "source_scope_reference": "fixture-scope-a",
        "source_capture_reference": "fixture-capture-a",
        "evidence_time": {
            "kind": "Instant",
            "at": "2026-09-09T10:00:00Z",
        },
        "entries": entries,
    }


def imported_entry(*, reference, position):
    return {
        "source_addresses": {
            "kind": "Ranges",
            "ranges": [
                {"first": "198.51.100.10", "last": "198.51.100.10"},
            ],
        },
        "destination_addresses": {
            "kind": "Ranges",
            "ranges": [
                {"first": "203.0.113.20", "last": "203.0.113.20"},
            ],
        },
        "protocol": "tcp",
        "source_ports": {"kind": "Any"},
        "destination_ports": {
            "kind": "Ranges",
            "ranges": [{"first": 443, "last": 443}],
        },
        "action": "Permit",
        "source_entry_reference": reference,
        "source_position": position,
    }


def test_local_import_records_and_reads_back_durable_evidence(
    postgres_dsn,
    greenfield_config,
):
    raw = json.dumps(
        import_document(
            entries=[
                imported_entry(reference="rule-10", position=10),
                imported_entry(reference="rule-20", position=20),
            ]
        )
    )
    command = LocalEvidenceImportAdapter().normalize(raw)

    with psycopg.connect(postgres_dsn) as connection:
        access_rules_before = connection.execute(
            "SELECT count(*) FROM napms_access_policy.access_rules"
        ).fetchone()[0]
        decisions_before = connection.execute(
            """
            SELECT count(*)
            FROM napms_connectivity_decision.connectivity_decisions
            """
        ).fetchone()[0]

    with open_technical_access_evidence_scope(greenfield_config) as scope:
        recorded = scope.record_technical_access_evidence.execute(command)

    assert recorded.outcome is RecordEvidenceOutcome.RECORDED
    evidence_set_id = recorded.evidence_set.evidence_set_id

    with open_technical_access_evidence_scope(greenfield_config) as scope:
        detail = scope.get_technical_access_evidence.execute(evidence_set_id)
        retry = scope.record_technical_access_evidence.execute(command)

    assert detail.outcome is EvidenceSetDetailOutcome.FOUND
    assert detail.evidence_set.evidence_set_id == evidence_set_id
    assert detail.evidence_set.source.namespace == "local-import"
    assert detail.evidence_set.source.reference == "local-fixture-a"
    assert len(detail.evidence_set.entries) == 2

    assert retry.outcome is RecordEvidenceOutcome.RESOLVED
    assert retry.evidence_set.evidence_set_id == evidence_set_id
    assert retry.evidence_set.recorded_at == detail.evidence_set.recorded_at

    with psycopg.connect(postgres_dsn) as connection:
        access_rules_after = connection.execute(
            "SELECT count(*) FROM napms_access_policy.access_rules"
        ).fetchone()[0]
        decisions_after = connection.execute(
            """
            SELECT count(*)
            FROM napms_connectivity_decision.connectivity_decisions
            """
        ).fetchone()[0]
        evidence_count = connection.execute(
            """
            SELECT count(*)
            FROM napms_technical_access_evidence.evidence_sets
            """
        ).fetchone()[0]

    assert access_rules_after == access_rules_before
    assert decisions_after == decisions_before
    assert evidence_count == 1


def test_local_import_normalization_failure_has_no_persistence_side_effect(
    postgres_dsn,
    greenfield_config,
):
    invalid = imported_entry(reference="rule-bad", position=10)
    invalid["service_object"] = "unsupported-service-object"
    raw = json.dumps(import_document(entries=[invalid]))

    with pytest.raises(LocalEvidenceImportError):
        LocalEvidenceImportAdapter().normalize(raw)

    with psycopg.connect(postgres_dsn) as connection:
        evidence_count = connection.execute(
            """
            SELECT count(*)
            FROM napms_technical_access_evidence.evidence_sets
            """
        ).fetchone()[0]

    assert evidence_count == 0
