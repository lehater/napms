import os

import pytest

psycopg = pytest.importorskip("psycopg")

from napms.contexts.access_policy_realization.infrastructure.rendering.cisco_asa_semantics import (
    project_asa_permit_regions,
)
from napms.contexts.access_policy_realization.domain.rendering import (
    RenderStatus,
)
from napms.platform.bootstrap.access_policy_realization import (
    open_access_policy_realization_scope,
)
from napms.platform.bootstrap.config import (
    ApplicationConfig,
    PostgresConfig,
)
from napms.platform.database.migrations import (
    apply_greenfield_migrations,
)
from tests.integration.postgres import (
    test_access_policy_realization_reconciliation as baseline,
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
        connection.execute(
            "TRUNCATE TABLE napms_authority.authority_assignments"
        )
        connection.execute(
            """
            TRUNCATE TABLE
                napms_application_catalogue.deployment_resource_bindings,
                napms_application_catalogue.dcs_revisions,
                napms_application_catalogue.component_deployments,
                napms_application_catalogue.components,
                napms_application_catalogue.applications
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
        connection.execute(
            "TRUNCATE TABLE napms_technical_access_evidence.evidence_sets"
        )
        connection.execute(
            "TRUNCATE TABLE "
            "napms_network_enforcement_placement.knowledge_captures"
        )


def _counts(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        return (
            connection.execute(
                "SELECT count(*) FROM napms_access_policy.access_rules"
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM "
                "napms_network_enforcement_placement.knowledge_captures"
            ).fetchone()[0],
            connection.execute(
                "SELECT count(*) FROM "
                "napms_technical_access_evidence.evidence_sets"
            ).fetchone()[0],
        )


def test_postgres_desired_policy_renders_to_equivalent_cisco_asa_acl(
    postgres_dsn,
    config,
):
    baseline.seed_domain(postgres_dsn)
    baseline.materialize_rule(config)
    baseline.record_placement(
        config,
        target=baseline.TARGET_A,
        capture_reference="placement-rendering",
        valid_from=baseline.VALID_FROM,
        valid_until=baseline.VALID_TO,
    )
    before = _counts(postgres_dsn)

    with open_access_policy_realization_scope(
        config,
        actor_id=baseline.ACTOR,
    ) as scope:
        desired = scope.derive_desired.execute(
            governance_scope=baseline.SCOPE,
            as_of=baseline.AS_OF,
        )
        rendered = scope.render.execute(desired)

    assert len(rendered) == 1
    artifact = rendered[0]
    assert artifact.status is RenderStatus.RENDERED
    assert artifact.target == baseline.TARGET_A
    assert artifact.renderer_name == "cisco-asa-extended-acl"
    assert artifact.renderer_contract_version == "1"
    assert artifact.content is not None
    assert "extended permit tcp" in artifact.content
    assert "eq 443" in artifact.content
    assert artifact.statements
    assert all(statement.rule_references for statement in artifact.statements)
    assert all(
        statement.interaction_references
        for statement in artifact.statements
    )
    assert all(
        statement.placement_provenance_references
        for statement in artifact.statements
    )

    projected = project_asa_permit_regions(artifact.content)
    assert set(projected) == set(
        desired.regions_for(baseline.TARGET_A)
    )
    assert _counts(postgres_dsn) == before
