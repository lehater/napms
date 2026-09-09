import json
import os
from datetime import datetime, timezone
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.composition.config import (
    ApplicationConfig,
    PostgresConfig,
)
from napms.composition.postgres_migrations import (
    apply_greenfield_migrations,
)
from napms.network_enforcement_placement.adapters.local_import import (
    LocalPlacementKnowledgeImportAdapter,
)
from napms.network_enforcement_placement.adapters.postgres import (
    PostgresPlacementKnowledgeRepository,
)
from napms.network_enforcement_placement.application.ports import (
    PlacementPersistenceError,
)
from napms.network_enforcement_placement.application.record import (
    RecordPlacementKnowledge,
    RecordPlacementKnowledgeOutcome,
)
from napms.network_enforcement_placement.application.select import (
    SelectEnforcement,
)
from napms.network_enforcement_placement.domain.model import (
    SelectionStatus,
)


pytestmark = pytest.mark.postgres

AS_OF = datetime(
    2026,
    9,
    9,
    12,
    tzinfo=timezone.utc,
)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get(
        "NAPMS_TEST_POSTGRES_DSN"
    )
    if not dsn:
        pytest.skip(
            "NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests"
        )
    return dsn


@pytest.fixture(scope="session")
def greenfield_config(postgres_dsn):
    config = ApplicationConfig(
        environment="local-dev",
        postgres=PostgresConfig(
            postgres_dsn
        ),
    )
    apply_greenfield_migrations(
        config
    )
    return config


@pytest.fixture(autouse=True)
def clean_nep(
    postgres_dsn,
    greenfield_config,
):
    with psycopg.connect(
        postgres_dsn,
        autocommit=True,
    ) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_network_enforcement_placement.knowledge_captures
            """
        )


def document(
    *,
    capture_reference="capture-1",
    valid_from="2026-09-09T10:00:00Z",
    valid_until="2026-09-10T10:00:00Z",
):
    return {
        "source_reference": "lab-topology",
        "source_capture_reference": (
            capture_reference
        ),
        "validity": {
            "valid_from": valid_from,
            "valid_until": valid_until,
        },
        "relation": {
            "source_ip": "10.0.0.1",
            "destination_ip": "10.0.0.2",
        },
        "path": {
            "path_reference": (
                "path-1"
            ),
            "traversal_points": [
                {
                    "provider_realization": {
                        "namespace": "lab",
                        "reference": "device-a",
                    },
                    "path_attachment": {
                        "namespace": "lab",
                        "reference": "edge-a",
                    },
                    "provenance": ["route:1"],
                }
            ],
            "provenance": ["path:1"],
        },
        "no_forwarding_path": None,
        "logical_firewalls": [
            {
                "logical_firewall_id": str(
                    UUID(int=1)
                ),
                "validity": {
                    "valid_from": "2026-01-01T00:00:00Z",
                    "valid_until": None,
                },
                "provenance": ["lf:1"],
            }
        ],
        "correspondences": [
            {
                "logical_firewall_id": str(
                    UUID(int=1)
                ),
                "provider_realization": {
                    "namespace": "lab",
                    "reference": "device-a",
                },
                "validity": {
                    "valid_from": "2026-01-01T00:00:00Z",
                    "valid_until": None,
                },
                "provenance": ["corr:1"],
            }
        ],
        "attachments": [
            {
                "enforcement_attachment_id": str(
                    UUID(int=10)
                ),
                "logical_firewall_id": str(
                    UUID(int=1)
                ),
                "provider_realization": {
                    "namespace": "lab",
                    "reference": "device-a",
                },
                "path_attachment": {
                    "namespace": "lab",
                    "reference": "edge-a",
                },
                "validity": {
                    "valid_from": "2026-01-01T00:00:00Z",
                    "valid_until": None,
                },
                "provenance": [
                    "attachment:10"
                ],
            }
        ],
        "complete_for_pair": True,
        "complete_for_attachments": True,
    }


def normalize(**kwargs):
    return (
        LocalPlacementKnowledgeImportAdapter()
        .normalize(
            json.dumps(
                document(**kwargs)
            )
        )
    )


def test_import_round_trip_and_selects_durable_placement(
    postgres_dsn,
    greenfield_config,
):
    command = normalize()

    with psycopg.connect(
        postgres_dsn
    ) as connection:
        repository = (
            PostgresPlacementKnowledgeRepository(
                connection
            )
        )
        recorded = (
            RecordPlacementKnowledge(
                captures=repository,
                capture_id_factory=(
                    lambda: UUID(int=100)
                ),
                clock=lambda: AS_OF,
            ).execute(command)
        )

    assert (
        recorded.outcome
        is RecordPlacementKnowledgeOutcome.RECORDED
    )

    with psycopg.connect(
        postgres_dsn
    ) as connection:
        repository = (
            PostgresPlacementKnowledgeRepository(
                connection
            )
        )
        result = SelectEnforcement(
            placement_knowledge=repository
        ).execute(
            relation=command.relation,
            as_of=AS_OF,
        )
        retry = (
            RecordPlacementKnowledge(
                captures=repository
            ).execute(command)
        )

    assert (
        result.status
        is SelectionStatus.PLACED
    )
    assert [
        item.logical_firewall_id
        for item in result.placements
    ] == [UUID(int=1)]
    assert (
        retry.outcome
        is RecordPlacementKnowledgeOutcome.RESOLVED
    )
    assert (
        retry.capture.capture_id
        == UUID(int=100)
    )


def test_no_effective_capture_is_unknown(
    postgres_dsn,
    greenfield_config,
):
    command = normalize(
        valid_from="2026-09-10T10:00:00Z",
        valid_until="2026-09-11T10:00:00Z",
    )
    with psycopg.connect(
        postgres_dsn
    ) as connection:
        repository = (
            PostgresPlacementKnowledgeRepository(
                connection
            )
        )
        RecordPlacementKnowledge(
            captures=repository
        ).execute(command)
        result = SelectEnforcement(
            placement_knowledge=repository
        ).execute(
            relation=command.relation,
            as_of=AS_OF,
        )

    assert (
        result.status
        is SelectionStatus.UNKNOWN
    )
    assert {
        gap.reason
        for gap
        in result.knowledge_gaps
    } == {
        "NoEffectiveKnowledgeCapture"
    }


def test_overlapping_captures_fail_closed_instead_of_latest_wins(
    postgres_dsn,
    greenfield_config,
):
    first = normalize(
        capture_reference="capture-1"
    )
    second = normalize(
        capture_reference="capture-2"
    )

    with psycopg.connect(
        postgres_dsn
    ) as connection:
        repository = (
            PostgresPlacementKnowledgeRepository(
                connection
            )
        )
        RecordPlacementKnowledge(
            captures=repository
        ).execute(first)
        RecordPlacementKnowledge(
            captures=repository
        ).execute(second)
        result = SelectEnforcement(
            placement_knowledge=repository
        ).execute(
            relation=first.relation,
            as_of=AS_OF,
        )

    assert (
        result.status
        is SelectionStatus.UNKNOWN
    )
    assert {
        gap.reason
        for gap
        in result.knowledge_gaps
    } == {
        "MultipleEffectiveKnowledgeCaptures"
    }


def test_database_rejects_capture_mutation(
    postgres_dsn,
    greenfield_config,
):
    command = normalize()
    with psycopg.connect(
        postgres_dsn
    ) as connection:
        repository = (
            PostgresPlacementKnowledgeRepository(
                connection
            )
        )
        RecordPlacementKnowledge(
            captures=repository
        ).execute(command)

    with psycopg.connect(
        postgres_dsn
    ) as connection:
        with pytest.raises(
            psycopg.Error
        ):
            connection.execute(
                """
                UPDATE napms_network_enforcement_placement.knowledge_captures
                SET source_reference = 'rewritten'
                """
            )


def test_corrupt_persisted_completeness_fails_closed(
    postgres_dsn,
    greenfield_config,
):
    command = normalize()
    with psycopg.connect(
        postgres_dsn
    ) as connection:
        repository = (
            PostgresPlacementKnowledgeRepository(
                connection
            )
        )
        RecordPlacementKnowledge(
            captures=repository
        ).execute(command)

    with psycopg.connect(
        postgres_dsn,
        autocommit=True,
    ) as connection:
        connection.execute(
            """
            DROP TRIGGER trg_nep_capture_immutable
            ON napms_network_enforcement_placement.knowledge_captures
            """
        )
        connection.execute(
            """
            UPDATE napms_network_enforcement_placement.knowledge_captures
            SET payload = jsonb_set(
                payload,
                '{complete_for_pair}',
                '"true"'::jsonb
            )
            """
        )

    try:
        with psycopg.connect(
            postgres_dsn
        ) as connection:
            repository = (
                PostgresPlacementKnowledgeRepository(
                    connection
                )
            )
            with pytest.raises(
                PlacementPersistenceError
            ):
                repository.load_for(
                    relation=command.relation,
                    as_of=AS_OF,
                )
    finally:
        from importlib.resources import files

        migration = files(
            "napms.network_enforcement_placement.adapters.postgres"
        ).joinpath(
            "migrations/0001_knowledge_captures.sql"
        )
        with psycopg.connect(
            postgres_dsn,
            autocommit=True,
        ) as connection:
            connection.execute(
                migration.read_text(
                    encoding="utf-8"
                )
            )
