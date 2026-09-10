import os

import psycopg
import pytest

from napms.composition.config import ApplicationConfig, PostgresConfig
from napms.composition.network_operator_view_postgres import (
    open_network_operator_view_scope,
)
from napms.composition.postgres_migrations import apply_greenfield_migrations
from napms.network_operator_view.application import Availability, ReadOutcome
from tests.integration.postgres import test_product_completion_acceptance as acceptance
from tests.integration.postgres import test_access_policy_realization_reconciliation as realization

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


def grant_operator_view(postgres_dsn):
    with psycopg.connect(postgres_dsn) as connection:
        connection.execute(
            """
            INSERT INTO napms_authority.authority_assignments (
                reference_id, actor_id, action, scope, valid_from, valid_to,
                provenance_reference
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                "authority-operator-view-i25",
                realization.ACTOR,
                "ReadNetworkOperatorRealization",
                realization.SCOPE,
                realization.VALID_FROM,
                realization.VALID_TO,
                "provenance:authority-operator-view-i25",
            ),
        )
        connection.commit()


def test_postgres_operator_view_keeps_unselected_runtime_inputs_not_available(
    config,
    postgres_dsn,
):
    acceptance.clean_product_completion_state(postgres_dsn, config)
    acceptance.seed_static_owner_facts(postgres_dsn)
    grant_operator_view(postgres_dsn)
    requirement = acceptance.declare_requirement(config)
    acceptance.record_allowed_decision(config, requirement)
    acceptance.materialize_rule_from_real_decision(config)
    realization.record_placement(
        config,
        target=realization.TARGET_A,
        capture_reference="placement-i25-operator-view",
        valid_from=realization.VALID_FROM,
        valid_until=realization.VALID_TO,
    )

    with open_network_operator_view_scope(
        config,
        actor_id=realization.ACTOR,
    ) as scope:
        result = scope.read.execute(
            actor_id=realization.ACTOR,
            scope=realization.SCOPE,
            as_of=realization.AS_OF,
        )

    assert result.outcome is ReadOutcome.AVAILABLE
    assert result.view is not None
    assert result.view.authority_reference == "authority-operator-view-i25"
    assert result.view.desired.availability is Availability.AVAILABLE
    assert result.view.rendering.availability is Availability.AVAILABLE
    assert result.view.reconciliation.availability is Availability.NOT_AVAILABLE
    assert result.view.operation.availability is Availability.NOT_AVAILABLE
