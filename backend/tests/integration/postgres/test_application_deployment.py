import os
from uuid import UUID

import psycopg
import pytest

from napms.contexts.application_deployment.domain.model import ComponentDeployment
from napms.contexts.application_deployment.infrastructure.persistence.postgres.migration import (
    migrate,
)
from napms.contexts.application_deployment.infrastructure.persistence.postgres.repository import (
    PostgresComponentDeploymentRepository,
)


pytestmark = pytest.mark.postgres
DSN = os.environ["NAPMS_TEST_POSTGRES_DSN"]


@pytest.fixture(autouse=True)
def fresh_schema() -> None:
    with psycopg.connect(DSN) as connection:
        connection.execute("DROP SCHEMA IF EXISTS application_deployment CASCADE")
        migrate(connection)


def test_deployment_round_trip_uses_opaque_cross_owner_refs() -> None:
    repository = PostgresComponentDeploymentRepository(DSN)
    deployment = ComponentDeployment(
        deployment_ref=UUID(int=1),
        component_ref=UUID(int=2),
        resource_ref=UUID(int=3),
    )

    repository.add(deployment)

    assert repository.resolve_deployment(deployment.deployment_ref) == deployment
