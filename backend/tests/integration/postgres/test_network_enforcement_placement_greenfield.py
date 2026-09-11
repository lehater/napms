import json
import os
from datetime import datetime, timezone
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.composition.config import ApplicationConfig, PostgresConfig
from napms.composition.network_enforcement_placement_postgres import (
    open_network_enforcement_placement_scope,
)
from napms.composition.postgres_migrations import apply_greenfield_migrations
from napms.network_enforcement_placement.adapters.local_import import (
    LocalPlacementKnowledgeImportAdapter,
)
from napms.network_enforcement_placement.domain.model import (
    InputProvenance,
    SelectionStatus,
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
def clean_nep(postgres_dsn, greenfield_config):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            "TRUNCATE TABLE napms_network_enforcement_placement.knowledge_captures"
        )


def capture_document(
    *,
    capture_reference: str,
    firewall_id: int,
    attachment_id: int,
    provider: str,
    valid_from: str,
    valid_until: str,
):
    return {
        "source_reference": "domain-attributable-lab-topology",
        "source_capture_reference": capture_reference,
        "validity": {
            "valid_from": valid_from,
            "valid_until": valid_until,
        },
        "relation": {
            "source_ip": "10.0.0.10",
            "destination_ip": "10.0.0.20",
        },
        "path": {
            "path_reference": f"path:{capture_reference}",
            "traversal_points": [
                {
                    "provider_realization": {
                        "namespace": "lab",
                        "reference": provider,
                    },
                    "path_attachment": {
                        "namespace": "lab",
                        "reference": "edge",
                    },
                    "provenance": [f"route:{capture_reference}"],
                }
            ],
            "provenance": [f"path:{capture_reference}"],
        },
        "no_forwarding_path": None,
        "logical_firewalls": [
            {
                "logical_firewall_id": str(UUID(int=firewall_id)),
                "validity": {
                    "valid_from": valid_from,
                    "valid_until": valid_until,
                },
                "provenance": [f"lf:{firewall_id}"],
            }
        ],
        "correspondences": [
            {
                "logical_firewall_id": str(UUID(int=firewall_id)),
                "provider_realization": {
                    "namespace": "lab",
                    "reference": provider,
                },
                "validity": {
                    "valid_from": valid_from,
                    "valid_until": valid_until,
                },
                "provenance": [f"corr:{capture_reference}"],
            }
        ],
        "attachments": [
            {
                "enforcement_attachment_id": str(UUID(int=attachment_id)),
                "logical_firewall_id": str(UUID(int=firewall_id)),
                "provider_realization": {
                    "namespace": "lab",
                    "reference": provider,
                },
                "path_attachment": {
                    "namespace": "lab",
                    "reference": "edge",
                },
                "validity": {
                    "valid_from": valid_from,
                    "valid_until": valid_until,
                },
                "provenance": [f"attachment:{attachment_id}"],
            }
        ],
        "complete_for_pair": True,
        "complete_for_attachments": True,
    }


def normalize(**kwargs):
    return LocalPlacementKnowledgeImportAdapter().normalize(
        json.dumps(capture_document(**kwargs))
    )


def counts(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        return {
            "access_rules": connection.execute(
                "SELECT count(*) FROM napms_access_policy.access_rules"
            ).fetchone()[0],
            "decisions": connection.execute(
                """
                SELECT count(*)
                FROM napms_connectivity_decision.connectivity_decisions
                """
            ).fetchone()[0],
            "tae": connection.execute(
                """
                SELECT count(*)
                FROM napms_technical_access_evidence.evidence_sets
                """
            ).fetchone()[0],
        }


def test_domain_attributable_relation_selects_without_peer_side_effects(
    postgres_dsn,
    greenfield_config,
):
    before = counts(postgres_dsn)
    command = normalize(
        capture_reference="capture-a",
        firewall_id=1,
        attachment_id=10,
        provider="device-a",
        valid_from="2026-09-09T10:00:00Z",
        valid_until="2026-09-09T13:00:00Z",
    )

    with open_network_enforcement_placement_scope(greenfield_config) as scope:
        scope.record_placement_knowledge.execute(command)
        result = scope.select_enforcement.execute(
            relation=command.relation,
            as_of=datetime(
                2026, 9, 9, 12, tzinfo=timezone.utc
            ),
            input_provenance=InputProvenance(
                (
                    "domain-interaction:1",
                    "resource:source:1",
                    "resource:destination:2",
                )
            ),
        )

    assert result.status is SelectionStatus.PLACED
    assert result.placements[0].logical_firewall_id == UUID(int=1)
    assert result.input_provenance.references == (
        "domain-interaction:1",
        "resource:destination:2",
        "resource:source:1",
    )
    assert counts(postgres_dsn) == before


def test_effective_time_switches_durable_placement_truthfully(
    greenfield_config,
):
    first = normalize(
        capture_reference="capture-a",
        firewall_id=1,
        attachment_id=10,
        provider="device-a",
        valid_from="2026-09-09T10:00:00Z",
        valid_until="2026-09-09T13:00:00Z",
    )
    second = normalize(
        capture_reference="capture-b",
        firewall_id=2,
        attachment_id=20,
        provider="device-b",
        valid_from="2026-09-09T13:00:00Z",
        valid_until="2026-09-09T16:00:00Z",
    )

    with open_network_enforcement_placement_scope(greenfield_config) as scope:
        scope.record_placement_knowledge.execute(first)
        scope.record_placement_knowledge.execute(second)

        before = scope.select_enforcement.execute(
            relation=first.relation,
            as_of=datetime(
                2026, 9, 9, 12, tzinfo=timezone.utc
            ),
        )
        after = scope.select_enforcement.execute(
            relation=first.relation,
            as_of=datetime(
                2026, 9, 9, 14, tzinfo=timezone.utc
            ),
        )

    assert before.status is SelectionStatus.PLACED
    assert after.status is SelectionStatus.PLACED
    assert before.placements[0].logical_firewall_id == UUID(int=1)
    assert after.placements[0].logical_firewall_id == UUID(int=2)
