import os
from datetime import datetime, timedelta, timezone
from importlib.resources import files

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy.application.ports import AuthorityAction, TernaryOutcome
from napms.authority_management.adapters.access_policy import (
    AccessPolicyAuthorityAdapter,
    AccessPolicyProposalScopeAdapter,
)
from napms.authority_management.adapters.postgres import (
    PostgresAuthorityAssignmentRepository,
)
from napms.authority_management.adapters.scoped_connectivity_inventory import (
    AuthorityManagementScopedConnectivityAdapter,
)
from napms.authority_management.application.check_authority import CheckAuthority
from napms.authority_management.application.list_scopes import ListEffectiveAuthorityScopes
from napms.scoped_connectivity_inventory.application.ports import (
    DependencyAvailability,
    ScopeAdmissionOutcome,
)


pytestmark = pytest.mark.postgres
START = datetime(2026, 9, 8, 8, 0, tzinfo=timezone.utc)
END = datetime(2026, 9, 9, 8, 0, tzinfo=timezone.utc)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_authority(postgres_dsn):
    migrations = files("napms.authority_management.adapters.postgres").joinpath(
        "migrations"
    )
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        for migration in sorted(
            (path for path in migrations.iterdir() if path.name.endswith(".sql")),
            key=lambda path: path.name,
        ):
            connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_authority(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute("TRUNCATE TABLE napms_authority.authority_assignments")


def seed_assignment(
    connection,
    *,
    reference_id="auth-1",
    actor_id="actor-1",
    action=AuthorityAction.SET_RULE_OPERATIONAL_STATE.value,
    scope="scope-1",
    valid_from=START,
    valid_to=END,
    provenance_reference="authority-provenance-1",
):
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
        (
            reference_id,
            actor_id,
            action,
            scope,
            valid_from,
            valid_to,
            provenance_reference,
        ),
    )


def adapter(connection):
    repository = PostgresAuthorityAssignmentRepository(connection)
    return AccessPolicyAuthorityAdapter(
        checker=CheckAuthority(assignments=repository)
    )


@pytest.mark.parametrize(
    "effective_time,expected",
    [
        (START, TernaryOutcome.PERMITTED),
        (END - timedelta(microseconds=1), TernaryOutcome.PERMITTED),
        (END, TernaryOutcome.DENIED),
    ],
)
def test_postgres_authority_uses_half_open_effective_validity(
    postgres_dsn, effective_time, expected
):
    with psycopg.connect(postgres_dsn) as connection:
        seed_assignment(connection)
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        result = adapter(connection).check(
            actor_id="actor-1",
            action=AuthorityAction.SET_RULE_OPERATIONAL_STATE,
            scope="scope-1",
            effective_time=effective_time,
        )

    assert result.outcome is expected
    assert result.authority_reference == (
        "auth-1" if expected is TernaryOutcome.PERMITTED else None
    )


def test_postgres_authority_requires_exact_actor_action_and_scope(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_assignment(connection)
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        service = adapter(connection)
        assert (
            service.check(
                actor_id="other",
                action=AuthorityAction.SET_RULE_OPERATIONAL_STATE,
                scope="scope-1",
                effective_time=START,
            ).outcome
            is TernaryOutcome.DENIED
        )
        assert (
            service.check(
                actor_id="actor-1",
                action=AuthorityAction.SET_RULE_EFFECTIVE_WINDOW,
                scope="scope-1",
                effective_time=START,
            ).outcome
            is TernaryOutcome.DENIED
        )
        assert (
            service.check(
                actor_id="actor-1",
                action=AuthorityAction.SET_RULE_OPERATIONAL_STATE,
                scope="other",
                effective_time=START,
            ).outcome
            is TernaryOutcome.DENIED
        )


def test_overlapping_effective_assignments_fail_closed_unknown(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_assignment(connection, reference_id="auth-1")
        seed_assignment(connection, reference_id="auth-2")
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        result = adapter(connection).check(
            actor_id="actor-1",
            action=AuthorityAction.SET_RULE_OPERATIONAL_STATE,
            scope="scope-1",
            effective_time=START,
        )

    assert result.outcome is TernaryOutcome.UNKNOWN
    assert result.authority_reference is None


def test_database_rejects_invalid_validity_interval(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        with pytest.raises(psycopg.errors.CheckViolation):
            seed_assignment(
                connection,
                reference_id="invalid",
                valid_from=END,
                valid_to=START,
            )



def test_postgres_authority_discovers_only_unambiguous_proposal_scopes(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        seed_assignment(
            connection,
            reference_id="proposal-a",
            action=AuthorityAction.PROPOSE_CONNECTIVITY.value,
            scope="scope-a",
        )
        seed_assignment(
            connection,
            reference_id="proposal-b1",
            action=AuthorityAction.PROPOSE_CONNECTIVITY.value,
            scope="scope-b",
        )
        seed_assignment(
            connection,
            reference_id="proposal-b2",
            action=AuthorityAction.PROPOSE_CONNECTIVITY.value,
            scope="scope-b",
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAuthorityAssignmentRepository(connection)
        adapter = AccessPolicyProposalScopeAdapter(
            discovery=ListEffectiveAuthorityScopes(assignments=repository)
        )
        result = adapter.list_effective_proposal_scopes(
            actor_id="actor-1",
            effective_time=START,
        )

    assert result.permitted_scopes == ("scope-a",)
    assert result.ambiguous_scopes == ("scope-b",)



def test_scoped_connectivity_authority_discovers_and_checks_read_scope(
    postgres_dsn,
):
    with psycopg.connect(postgres_dsn) as connection:
        seed_assignment(
            connection,
            reference_id="scoped-a",
            action="ReadScopedConnectivity",
            scope="scope-a",
        )
        seed_assignment(
            connection,
            reference_id="scoped-b1",
            action="ReadScopedConnectivity",
            scope="scope-b",
        )
        seed_assignment(
            connection,
            reference_id="scoped-b2",
            action="ReadScopedConnectivity",
            scope="scope-b",
        )
        connection.commit()

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresAuthorityAssignmentRepository(connection)
        adapter = AuthorityManagementScopedConnectivityAdapter(
            checker=CheckAuthority(assignments=repository),
            scope_lister=ListEffectiveAuthorityScopes(assignments=repository),
        )
        discovered = adapter.discover_scopes(
            actor_id="actor-1",
            as_of=START,
        )
        permitted = adapter.check_scope(
            actor_id="actor-1",
            scope="scope-a",
            as_of=START,
        )
        ambiguous = adapter.check_scope(
            actor_id="actor-1",
            scope="scope-b",
            as_of=START,
        )

    assert discovered.availability is DependencyAvailability.AVAILABLE
    assert discovered.permitted_scopes == ("scope-a",)
    assert discovered.ambiguous_scopes == ("scope-b",)
    assert permitted.outcome is ScopeAdmissionOutcome.PERMITTED
    assert permitted.authority_reference == "scoped-a"
    assert ambiguous.outcome is ScopeAdmissionOutcome.AMBIGUOUS
