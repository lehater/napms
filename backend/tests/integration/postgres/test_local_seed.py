import os

import psycopg
import pytest

from napms.contexts.access_policy.domain.model import PermissionDecision, RuleEffectState
from napms.contexts.access_policy.infrastructure.persistence.postgres.repository import (
    PostgresAccessPolicyRepository,
)
from napms.platform.bootstrap.local_seed import demo_ref, seed_local_demo
from napms.platform.database.migration import migrate


pytestmark = pytest.mark.postgres
DSN = os.environ["NAPMS_TEST_POSTGRES_DSN"]


@pytest.fixture(autouse=True)
def fresh_schemas() -> None:
    with psycopg.connect(DSN) as connection:
        for schema in (
            "access_policy",
            "business_connectivity",
            "application_deployment",
            "application_communication_catalogue",
            "resource_catalogue",
            "application_edge",
        ):
            connection.execute(f"DROP SCHEMA IF EXISTS {schema} CASCADE")
        migrate(connection)


def test_local_demo_seed_is_connected_and_idempotent() -> None:
    seed_local_demo(DSN)
    seed_local_demo(DSN)

    with psycopg.connect(DSN) as connection:
        counts = {
            "applications": connection.execute(
                "SELECT COUNT(*) FROM application_communication_catalogue.application"
            ).fetchone()[0],
            "components": connection.execute(
                "SELECT COUNT(*) FROM application_communication_catalogue.component"
            ).fetchone()[0],
            "interactions": connection.execute(
                "SELECT COUNT(*) FROM application_communication_catalogue.interaction"
            ).fetchone()[0],
            "revisions": connection.execute(
                "SELECT COUNT(*) FROM application_communication_catalogue.interaction_revision"
            ).fetchone()[0],
            "resources": connection.execute(
                "SELECT COUNT(*) FROM resource_catalogue.resource"
            ).fetchone()[0],
            "deployments": connection.execute(
                "SELECT COUNT(*) FROM application_deployment.component_deployment"
            ).fetchone()[0],
            "processes": connection.execute(
                "SELECT COUNT(*) FROM business_connectivity.business_process"
            ).fetchone()[0],
            "needs": connection.execute(
                "SELECT COUNT(*) FROM business_connectivity.connectivity_need"
            ).fetchone()[0],
            "requests": connection.execute(
                "SELECT COUNT(*) FROM access_policy.access_request"
            ).fetchone()[0],
            "rules": connection.execute(
                "SELECT COUNT(*) FROM access_policy.policy_rule"
            ).fetchone()[0],
        }
        decisions = connection.execute(
            """
            SELECT decision_result, COUNT(*)
            FROM access_policy.access_request
            GROUP BY decision_result
            """
        ).fetchall()

    assert counts == {
        "applications": 10,
        "components": 10,
        "interactions": 10,
        "revisions": 10,
        "resources": 10,
        "deployments": 10,
        "processes": 10,
        "needs": 10,
        "requests": 10,
        "rules": 6,
    }
    assert {decision: count for decision, count in decisions} == {
        None: 2,
        PermissionDecision.ALLOWED.value: 6,
        PermissionDecision.DENIED.value: 2,
    }

    policy = PostgresAccessPolicyRepository(DSN)
    allowed = policy.get_request(demo_ref("access-request", "customer-sign-in"))
    assert allowed is not None
    assert allowed.initial_need_ref == demo_ref("need", "customer-sign-in")
    assert allowed.decision_result is PermissionDecision.ALLOWED

    inactive_rule = policy.get_rule(demo_ref("policy-rule", "payment-reporting"))
    assert inactive_rule is not None
    assert inactive_rule.effect_state is RuleEffectState.INACTIVE

    pending = policy.get_request(
        demo_ref("access-request", "platform-monitoring")
    )
    assert pending is not None
    assert pending.decision_result is None
