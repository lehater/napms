import os
from datetime import datetime, timedelta, timezone
from importlib.resources import files
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy.adapters.postgres.application_catalogue_dependency_query import (
    PostgresAccessRuleDependencyQuery,
)
from napms.access_policy.domain.model import RuleSemanticIdentity
from napms.contexts.connectivity_decision.infrastructure.persistence.postgres.application_catalogue_dependency_query import (
    PostgresConnectivityDecisionDependencyQuery,
)
from napms.contexts.connectivity_decision.domain.model import DecisionSubject
from napms.contexts.connectivity_requirements.infrastructure.persistence.postgres.application_catalogue_dependency_query import (
    PostgresConnectivityRequirementDependencyQuery,
)
from napms.contexts.connectivity_requirements.domain.model import RequiredSemanticInteraction


pytestmark = pytest.mark.postgres
NOW = datetime(2026, 9, 11, 0, 0, tzinfo=timezone.utc)
SOURCE = UUID("00000000-0000-0000-0000-00000000b001")
DESTINATION = UUID("00000000-0000-0000-0000-00000000b002")
DCS = UUID("00000000-0000-0000-0000-00000000b003")
REQUIREMENT_CURRENT = UUID("00000000-0000-0000-0000-00000000b011")
REQUIREMENT_EXPIRED = UUID("00000000-0000-0000-0000-00000000b012")
DECISION_OLD = UUID("00000000-0000-0000-0000-00000000b021")
DECISION_CURRENT = UUID("00000000-0000-0000-0000-00000000b022")
RULE = UUID("00000000-0000-0000-0000-00000000b031")


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_dependencies(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        for package in (
            "napms.contexts.connectivity_requirements.infrastructure.persistence.postgres",
            "napms.contexts.connectivity_decision.infrastructure.persistence.postgres",
            "napms.access_policy.adapters.postgres",
        ):
            migrations = files(package).joinpath("migrations")
            for migration in sorted(
                (path for path in migrations.iterdir() if path.name.endswith(".sql")),
                key=lambda path: path.name,
            ):
                connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_dependencies(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_connectivity_requirements.connectivity_requirements,
                napms_connectivity_decision.connectivity_decisions,
                napms_access_policy.access_rules
            CASCADE
            """
        )


def _required_subject() -> RequiredSemanticInteraction:
    return RequiredSemanticInteraction(
        source_component_deployment_id=SOURCE,
        destination_component_deployment_id=DESTINATION,
        dcs_contract_revision_id=DCS,
    )


def _decision_subject() -> DecisionSubject:
    return DecisionSubject(
        source_component_deployment_id=SOURCE,
        destination_component_deployment_id=DESTINATION,
        dcs_contract_revision_id=DCS,
    )


def _rule_subject() -> RuleSemanticIdentity:
    return RuleSemanticIdentity(
        source_component_deployment_id=SOURCE,
        destination_component_deployment_id=DESTINATION,
        dcs_contract_revision_id=DCS,
    )


def test_requirement_dependency_query_uses_lifecycle_and_applicability(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        with connection.cursor() as cursor:
            cursor.executemany(
                """
                INSERT INTO napms_connectivity_requirements.connectivity_requirements (
                    requirement_id, governance_scope, dependent_component_deployment_id,
                    source_component_deployment_id, destination_component_deployment_id,
                    dcs_contract_revision_id, applicability_kind, applicability_start,
                    applicability_end, justification, lifecycle_state, declaration_actor_id,
                    declaration_effective_time, declaration_authority_reference,
                    declaration_catalogue_reference, version
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,
                          'test', 'Active', 'actor', %s, 'authority', 'catalogue', 1)
                """,
                (
                    (
                        REQUIREMENT_CURRENT,
                        "scope:current",
                        SOURCE,
                        SOURCE,
                        DESTINATION,
                        DCS,
                        "Ongoing",
                        None,
                        None,
                        NOW - timedelta(days=10),
                    ),
                    (
                        REQUIREMENT_EXPIRED,
                        "scope:expired",
                        SOURCE,
                        SOURCE,
                        DESTINATION,
                        DCS,
                        "AbsoluteWindow",
                        NOW - timedelta(days=10),
                        NOW - timedelta(days=1),
                        NOW - timedelta(days=10),
                    ),
                ),
            )
        connection.commit()

        total, references = PostgresConnectivityRequirementDependencyQuery(connection).page(
            subjects=(_required_subject(),),
            as_of=NOW,
            offset=0,
            limit=10,
        )

        assert total == 1
        assert references == (str(REQUIREMENT_CURRENT),)


def test_decision_dependency_query_returns_only_current_non_superseded_decision(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO napms_connectivity_decision.connectivity_decisions (
                decision_id, governance_scope, source_component_deployment_id,
                destination_component_deployment_id, dcs_contract_revision_id,
                outcome, valid_from, valid_until, reason_code, reason_text,
                evidence_references, deciding_actor_id, decided_at,
                authority_reference, supersedes_decision_id
            ) VALUES (%s, 'scope:a', %s, %s, %s, 'Allowed', %s, NULL,
                      'approved', 'old', '[]'::jsonb, 'actor', %s, 'authority', NULL)
            """,
            (DECISION_OLD, SOURCE, DESTINATION, DCS, NOW - timedelta(days=10), NOW - timedelta(days=10)),
        )
        connection.execute(
            """
            INSERT INTO napms_connectivity_decision.connectivity_decisions (
                decision_id, governance_scope, source_component_deployment_id,
                destination_component_deployment_id, dcs_contract_revision_id,
                outcome, valid_from, valid_until, reason_code, reason_text,
                evidence_references, deciding_actor_id, decided_at,
                authority_reference, supersedes_decision_id
            ) VALUES (%s, 'scope:a', %s, %s, %s, 'Allowed', %s, NULL,
                      'approved', 'current', '[]'::jsonb, 'actor', %s, 'authority', %s)
            """,
            (DECISION_CURRENT, SOURCE, DESTINATION, DCS, NOW - timedelta(days=1), NOW - timedelta(days=1), DECISION_OLD),
        )
        connection.commit()

        total, references = PostgresConnectivityDecisionDependencyQuery(connection).page(
            subjects=(_decision_subject(),),
            as_of=NOW,
            offset=0,
            limit=10,
        )

        assert total == 1
        assert references == (str(DECISION_CURRENT),)


def test_access_rule_dependency_query_respects_effective_window(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO napms_access_policy.access_rules (
                rule_id, source_component_deployment_id,
                destination_component_deployment_id, dcs_contract_revision_id,
                operational_state, decision_result, decision_id, proposal_actor_id,
                proposal_authority_scope, proposal_effective_time,
                authority_reference, catalogue_reference
            ) VALUES (%s, %s, %s, %s, 'Active', 'Allowed', 'decision:1',
                      'actor', 'scope:a', %s, 'authority', 'catalogue')
            """,
            (RULE, SOURCE, DESTINATION, DCS, NOW - timedelta(days=10)),
        )
        connection.execute(
            """
            INSERT INTO napms_access_policy.access_rule_effective_windows (
                rule_id, start_at, end_at
            ) VALUES (%s, %s, %s)
            """,
            (RULE, NOW - timedelta(days=1), NOW + timedelta(days=1)),
        )
        connection.commit()

        query = PostgresAccessRuleDependencyQuery(connection)
        total_now, refs_now = query.page(
            subjects=(_rule_subject(),),
            as_of=NOW,
            offset=0,
            limit=10,
        )
        total_later, refs_later = query.page(
            subjects=(_rule_subject(),),
            as_of=NOW + timedelta(days=2),
            offset=0,
            limit=10,
        )

        assert total_now == 1
        assert refs_now == (str(RULE),)
        assert total_later == 0
        assert refs_later == ()
