import hashlib
import os

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy_realization.domain.rendering import RenderStatus
from napms.composition.access_policy_realization_postgres import (
    open_access_policy_realization_scope,
)
from napms.composition.config import ApplicationConfig, PostgresConfig
from napms.composition.network_environment_operations_stub import (
    open_network_environment_operations_stub_scope,
)
from napms.composition.postgres_migrations import apply_greenfield_migrations
from napms.network_environment_operations.adapters import StubScenario
from napms.network_environment_operations.domain import (
    ExecuteNetworkOperationCommand,
    OperationOutcome,
)
from tests.integration.postgres import (
    test_access_policy_realization_reconciliation as baseline,
)


pytestmark = pytest.mark.postgres


@pytest.fixture(scope="session")
def postgres_dsn():
    dsn = os.environ.get("NAPMS_TEST_POSTGRES_DSN")
    if not dsn:
        pytest.skip("NAPMS_TEST_POSTGRES_DSN is required for PostgreSQL integration tests")
    return dsn


@pytest.fixture(scope="session")
def config(postgres_dsn):
    value = ApplicationConfig(
        environment="local-dev",
        postgres=PostgresConfig(postgres_dsn),
    )
    apply_greenfield_migrations(value)
    return value


@pytest.fixture(autouse=True)
def clean(postgres_dsn, config):
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
        connection.execute("TRUNCATE TABLE napms_authority.authority_assignments")
        connection.execute(
            """
            TRUNCATE TABLE
                napms_application_catalogue.deployment_resource_bindings,
                napms_application_catalogue.dcs_revisions,
                napms_application_catalogue.component_deployments
            CASCADE
            """
        )
        connection.execute(
            """
            TRUNCATE TABLE
                napms_resource_catalogue.resource_endpoints,
                napms_resource_catalogue.resource_realization_versions,
                napms_resource_catalogue.resources
            CASCADE
            """
        )
        connection.execute("TRUNCATE TABLE napms_technical_access_evidence.evidence_sets")
        connection.execute(
            "TRUNCATE TABLE napms_network_enforcement_placement.knowledge_captures"
        )


def _owner_counts(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        return (
            connection.execute(
                "SELECT count(*) FROM napms_access_policy.access_rules"
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM napms_network_enforcement_placement.knowledge_captures"
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM napms_technical_access_evidence.evidence_sets"
            ).fetchone()[0],
        )


def _derive_and_render(config):
    with open_access_policy_realization_scope(config, actor_id=baseline.ACTOR) as scope:
        desired = scope.derive_desired.execute(
            governance_scope=baseline.SCOPE,
            as_of=baseline.AS_OF,
        )
        rendered = scope.render.execute(desired)
    assert len(rendered) == 1
    artifact = rendered[0]
    assert artifact.status is RenderStatus.RENDERED
    assert artifact.content is not None
    return artifact


def _command(artifact, operation_target, operation_id="op-i22-success"):
    digest = hashlib.sha256(artifact.content.encode("utf-8")).hexdigest()
    return ExecuteNetworkOperationCommand(
        operation_id=operation_id,
        target=operation_target,
        renderer_name=artifact.renderer_name,
        renderer_contract_version=artifact.renderer_contract_version,
        artifact_content=artifact.content,
        artifact_digest=digest,
        actor_id=baseline.ACTOR,
        authority_scope=baseline.SCOPE,
        expected_pre_revision="1",
    )


def _seed(config, postgres_dsn):
    baseline.seed_domain(postgres_dsn)
    baseline.materialize_rule(config)
    baseline.record_placement(
        config,
        target=baseline.TARGET_A,
        capture_reference="placement-i22-stub",
        valid_from=baseline.VALID_FROM,
        valid_until=baseline.VALID_TO,
    )


def test_desired_rendered_stub_applied_and_verified_without_owner_mutation(
    config,
    postgres_dsn,
):
    _seed(config, postgres_dsn)
    before = _owner_counts(postgres_dsn)
    artifact = _derive_and_render(config)
    stub = open_network_environment_operations_stub_scope(target=artifact.target)

    result = stub.execute.execute(_command(artifact, stub.target))

    assert result.outcome is OperationOutcome.VERIFIED
    assert result.pre_state is not None
    assert result.post_state is not None
    assert result.post_state.artifact_digest == result.artifact_digest
    assert stub.target_stub.apply_calls == 1
    assert stub.target_stub.acquire_calls == 2
    assert _owner_counts(postgres_dsn) == before


def test_unknown_apply_is_not_reported_verified_or_blindly_retried(config, postgres_dsn):
    _seed(config, postgres_dsn)
    artifact = _derive_and_render(config)
    stub = open_network_environment_operations_stub_scope(
        target=artifact.target,
        scenario=StubScenario.UNKNOWN_APPLY,
    )
    command = _command(artifact, stub.target, operation_id="op-i22-unknown")

    first = stub.execute.execute(command)
    second = stub.execute.execute(command)

    assert first.outcome is OperationOutcome.UNKNOWN
    assert second is first
    assert stub.target_stub.apply_calls == 1


def test_concurrent_target_change_fails_without_verified_success(config, postgres_dsn):
    _seed(config, postgres_dsn)
    artifact = _derive_and_render(config)
    stub = open_network_environment_operations_stub_scope(
        target=artifact.target,
        scenario=StubScenario.CONCURRENT_CHANGE,
    )

    result = stub.execute.execute(
        _command(artifact, stub.target, operation_id="op-i22-concurrent")
    )

    assert result.outcome is OperationOutcome.PRECONDITION_FAILED
    assert result.apply_result is not None
    assert result.post_state is None
