import os
from uuid import UUID

import psycopg
import pytest

from napms.contexts.application_deployment.application.queries import (
    DeploymentCatalogueQuery,
    DeploymentSortField,
    SortDirection,
)
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


def test_deployment_catalogue_query_applies_search_filters_sort_and_paging() -> None:
    repository = PostgresComponentDeploymentRepository(DSN)
    values = (
        ComponentDeployment(UUID(int=101), UUID(int=201), UUID(int=301)),
        ComponentDeployment(UUID(int=102), UUID(int=202), UUID(int=302)),
        ComponentDeployment(UUID(int=103), UUID(int=201), UUID(int=303)),
    )
    for value in values:
        repository.add(value)

    first = repository.query_deployments(
        DeploymentCatalogueQuery(
            component_ref=UUID(int=201),
            sort_by=DeploymentSortField.RESOURCE_REF,
            sort_direction=SortDirection.DESC,
            page=1,
            page_size=1,
        )
    )
    assert first.total == 2
    assert [item.deployment_ref for item in first.items] == [UUID(int=103)]

    second = repository.query_deployments(
        DeploymentCatalogueQuery(
            component_ref=UUID(int=201),
            sort_by=DeploymentSortField.RESOURCE_REF,
            sort_direction=SortDirection.DESC,
            page=2,
            page_size=1,
        )
    )
    assert [item.deployment_ref for item in second.items] == [UUID(int=101)]

    filtered = repository.query_deployments(
        DeploymentCatalogueQuery(resource_ref=UUID(int=302))
    )
    assert filtered.total == 1
    assert [item.deployment_ref for item in filtered.items] == [UUID(int=102)]

    searched = repository.query_deployments(DeploymentCatalogueQuery(search="00000067"))
    assert searched.total == 1
    assert [item.deployment_ref for item in searched.items] == [UUID(int=103)]
