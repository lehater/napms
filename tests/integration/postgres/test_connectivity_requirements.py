import os
from datetime import datetime, timedelta, timezone
from importlib.resources import files
from uuid import UUID

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.connectivity_requirements.adapters.postgres import (
    PostgresConnectivityRequirementRepository,
)
from napms.connectivity_requirements.application.ports import (
    ActiveRequirementSemanticConflict,
    RequirementAuthorityCheck,
    RequirementPersistenceError,
    RequirementVersionConflict,
    TernaryOutcome,
)
from napms.connectivity_requirements.application.set_applicability import (
    ApplicabilityMutationOutcome,
    SetConnectivityRequirementApplicability,
    SetRequirementApplicability,
)
from napms.connectivity_requirements.domain.model import (
    ConnectivityRequirement,
    RequiredSemanticInteraction,
    RequirementApplicability,
    RequirementDeclarationProvenance,
    RequirementLifecycleState,
    RequirementSemanticKey,
)


pytestmark = pytest.mark.postgres

NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=101)
DESTINATION = UUID(int=102)
DCS = UUID(int=103)
INTERACTION = RequiredSemanticInteraction(SOURCE, DESTINATION, DCS)


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session", autouse=True)
def migrated_connectivity_requirements(postgres_dsn):
    migrations = files(
        "napms.connectivity_requirements.adapters.postgres"
    ).joinpath("migrations")
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        for migration in sorted(
            (path for path in migrations.iterdir() if path.name.endswith(".sql")),
            key=lambda path: path.name,
        ):
            connection.execute(migration.read_text(encoding="utf-8"))


@pytest.fixture(autouse=True)
def clean_connectivity_requirements(postgres_dsn):
    with psycopg.connect(postgres_dsn, autocommit=True) as connection:
        connection.execute(
            """
            TRUNCATE TABLE
                napms_connectivity_requirements.applicability_changes,
                napms_connectivity_requirements.justification_changes,
                napms_connectivity_requirements.lifecycle_transitions,
                napms_connectivity_requirements.connectivity_requirements
            CASCADE
            """
        )


class PermittedAuthority:
    def __init__(self, reference="authority-1"):
        self.reference = reference
        self.calls = []

    def check(self, **kwargs):
        self.calls.append(kwargs)
        return RequirementAuthorityCheck(
            TernaryOutcome.PERMITTED,
            self.reference,
        )


class RollbackThenFailRepository:
    def __init__(self, delegate, connection):
        self.delegate = delegate
        self.connection = connection

    def __getattr__(self, name):
        return getattr(self.delegate, name)

    def save(self, requirement, *, expected_version):
        self.delegate.save(requirement, expected_version=expected_version)

    def commit(self):
        self.connection.rollback()
        raise RequirementPersistenceError("forced commit failure")


def requirement(
    requirement_id,
    *,
    scope="scope-a",
    dependent=SOURCE,
    interaction=INTERACTION,
    applicability=None,
    justification="Business dependency",
):
    key = RequirementSemanticKey(
        governance_scope=scope,
        dependent_component_deployment_id=dependent,
        required_interaction=interaction,
    )
    return ConnectivityRequirement.declared(
        requirement_id=requirement_id,
        semantic_key=key,
        applicability=applicability or RequirementApplicability.ongoing(),
        justification=justification,
        provenance=RequirementDeclarationProvenance(
            actor_id="actor-1",
            effective_time=NOW,
            governance_scope=scope,
            authority_reference="declare-authority",
            catalogue_reference="catalogue-1",
        ),
    )


def persist(postgres_dsn, value):
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityRequirementRepository(connection)
        repository.add(value)
        repository.commit()


def test_requirement_round_trip_preserves_identity_and_declaration_provenance(
    postgres_dsn,
):
    original = requirement(UUID(int=1))
    persist(postgres_dsn, original)

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresConnectivityRequirementRepository(connection).get_by_id(
            original.requirement_id
        )

    assert reloaded == original
    assert reloaded.semantic_key == original.semantic_key
    assert reloaded.version == 1


def test_active_semantic_uniqueness_is_enforced(postgres_dsn):
    first = requirement(UUID(int=2))
    second = requirement(UUID(int=3))
    persist(postgres_dsn, first)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityRequirementRepository(connection)
        with pytest.raises(ActiveRequirementSemanticConflict):
            repository.add(second)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityRequirementRepository(connection)
        resolved = repository.find_active_by_semantic_key(first.semantic_key)

    assert resolved.requirement_id == first.requirement_id


def test_retirement_releases_active_semantic_key_for_new_lifecycle(postgres_dsn):
    first = requirement(UUID(int=4))
    persist(postgres_dsn, first)

    retired = first.retired(
        actor_id="actor-2",
        effective_time=NOW + timedelta(minutes=1),
        authority_reference="retire-authority",
    )
    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityRequirementRepository(connection)
        repository.save(retired, expected_version=1)
        repository.commit()

    second = requirement(UUID(int=5))
    persist(postgres_dsn, second)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityRequirementRepository(connection)
        old = repository.get_by_id(first.requirement_id)
        active = repository.find_active_by_semantic_key(second.semantic_key)

    assert old.lifecycle_state is RequirementLifecycleState.RETIRED
    assert active.requirement_id == second.requirement_id


def test_mutations_round_trip_with_version_and_business_audit(postgres_dsn):
    original = requirement(UUID(int=6))
    persist(postgres_dsn, original)
    window = RequirementApplicability.absolute_window(
        start=NOW,
        end=NOW + timedelta(hours=2),
    )

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityRequirementRepository(connection)
        first = repository.get_by_id(original.requirement_id)
        changed_window = first.with_applicability(
            applicability=window,
            actor_id="actor-2",
            effective_time=NOW + timedelta(minutes=1),
            authority_reference="window-authority",
        )
        repository.save(changed_window, expected_version=first.version)
        repository.commit()

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityRequirementRepository(connection)
        second = repository.get_by_id(original.requirement_id)
        changed_reason = second.with_justification(
            justification="Updated dependency",
            actor_id="actor-3",
            effective_time=NOW + timedelta(minutes=2),
            authority_reference="reason-authority",
        )
        repository.save(changed_reason, expected_version=second.version)
        repository.commit()

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityRequirementRepository(connection)
        third = repository.get_by_id(original.requirement_id)
        retired = third.retired(
            actor_id="actor-4",
            effective_time=NOW + timedelta(minutes=3),
            authority_reference="retire-authority",
        )
        repository.save(retired, expected_version=third.version)
        repository.commit()

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresConnectivityRequirementRepository(connection).get_by_id(
            original.requirement_id
        )

    assert reloaded.version == 4
    assert reloaded.applicability == window
    assert reloaded.justification == "Updated dependency"
    assert reloaded.lifecycle_state is RequirementLifecycleState.RETIRED
    assert len(reloaded.applicability_history) == 1
    assert len(reloaded.justification_history) == 1
    assert len(reloaded.lifecycle_history) == 1
    assert reloaded.applicability_history[0].authority_reference == "window-authority"
    assert reloaded.justification_history[0].authority_reference == "reason-authority"
    assert reloaded.lifecycle_history[0].authority_reference == "retire-authority"


def test_stale_version_conflict_is_explicit(postgres_dsn):
    original = requirement(UUID(int=7))
    persist(postgres_dsn, original)

    connection_a = psycopg.connect(postgres_dsn)
    connection_b = psycopg.connect(postgres_dsn)
    try:
        repo_a = PostgresConnectivityRequirementRepository(connection_a)
        repo_b = PostgresConnectivityRequirementRepository(connection_b)
        loaded_a = repo_a.get_by_id(original.requirement_id)
        loaded_b = repo_b.get_by_id(original.requirement_id)

        updated_a = loaded_a.with_justification(
            justification="First writer",
            actor_id="actor-a",
            effective_time=NOW + timedelta(minutes=1),
            authority_reference="auth-a",
        )
        repo_a.save(updated_a, expected_version=loaded_a.version)
        repo_a.commit()

        updated_b = loaded_b.with_justification(
            justification="Second writer",
            actor_id="actor-b",
            effective_time=NOW + timedelta(minutes=2),
            authority_reference="auth-b",
        )
        with pytest.raises(RequirementVersionConflict):
            repo_b.save(updated_b, expected_version=loaded_b.version)
    finally:
        connection_a.close()
        connection_b.close()

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresConnectivityRequirementRepository(connection).get_by_id(
            original.requirement_id
        )

    assert reloaded.justification == "First writer"
    assert len(reloaded.justification_history) == 1


def test_state_and_audit_roll_back_together_on_failed_commit(postgres_dsn):
    original = requirement(UUID(int=8))
    persist(postgres_dsn, original)
    authority = PermittedAuthority("window-authority")
    window = RequirementApplicability.absolute_window(
        start=NOW,
        end=NOW + timedelta(hours=1),
    )

    with psycopg.connect(postgres_dsn) as connection:
        delegate = PostgresConnectivityRequirementRepository(connection)
        repository = RollbackThenFailRepository(delegate, connection)
        with pytest.raises(RequirementPersistenceError):
            SetConnectivityRequirementApplicability(
                authority=authority,
                requirements=repository,
            ).execute(
                SetRequirementApplicability(
                    requirement_id=original.requirement_id,
                    applicability=window,
                    actor_id="actor-2",
                    effective_time=NOW + timedelta(minutes=1),
                )
            )

    with psycopg.connect(postgres_dsn) as connection:
        reloaded = PostgresConnectivityRequirementRepository(connection).get_by_id(
            original.requirement_id
        )

    assert reloaded.applicability == RequirementApplicability.ongoing()
    assert reloaded.applicability_history == ()
    assert reloaded.version == 1


def test_repository_pages_across_authorized_governance_scopes(postgres_dsn):
    one = requirement(UUID(int=11), scope="scope-a")
    two = requirement(UUID(int=12), scope="scope-b")
    three = requirement(UUID(int=13), scope="scope-c")
    for value in (one, two, three):
        persist(postgres_dsn, value)

    with psycopg.connect(postgres_dsn) as connection:
        repository = PostgresConnectivityRequirementRepository(connection)
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

    assert first == (one,)
    assert second == (three,)


def test_postgres_commit_failure_maps_to_unknown_outcome():
    class CommitFailureConnection:
        def commit(self):
            raise psycopg.OperationalError("lost commit acknowledgement")

    repository = PostgresConnectivityRequirementRepository(
        CommitFailureConnection()
    )
    from napms.connectivity_requirements.application.ports import (
        RequirementCommitOutcomeUnknown,
    )

    with pytest.raises(RequirementCommitOutcomeUnknown):
        repository.commit()
