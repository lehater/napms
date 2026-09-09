import pytest

psycopg = pytest.importorskip("psycopg")

from napms.access_policy_realization.adapters.cisco_asa_semantics import (
    project_asa_permit_regions,
)
from napms.access_policy_realization.domain.rendering import (
    RenderStatus,
)
from napms.composition.access_policy_realization_postgres import (
    open_access_policy_realization_scope,
)
from tests.integration.postgres import (
    test_access_policy_realization_reconciliation as baseline,
)


pytestmark = pytest.mark.postgres


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
