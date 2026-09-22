import os
from datetime import datetime, timezone
from uuid import UUID

import psycopg
import pytest

from napms.contexts.business_connectivity.application.queries import (
    BusinessProcessCatalogueQuery,
    BusinessProcessSortField,
    SortDirection,
)
from napms.contexts.business_connectivity.domain.model import (
    BusinessProcess,
    ConnectivityNeed,
    NeedStatus,
)
from napms.contexts.business_connectivity.infrastructure.persistence.postgres.migration import (
    migrate,
)
from napms.contexts.business_connectivity.infrastructure.persistence.postgres.repository import (
    PostgresBusinessProcessRepository,
)


pytestmark = pytest.mark.postgres
DSN = os.environ["NAPMS_TEST_POSTGRES_DSN"]
NOW = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def fresh_schema() -> None:
    with psycopg.connect(DSN) as connection:
        connection.execute("DROP SCHEMA IF EXISTS business_connectivity CASCADE")
        migrate(connection)


def test_process_and_retired_need_round_trip_without_peer_foreign_keys() -> None:
    repository = PostgresBusinessProcessRepository(DSN)
    process = BusinessProcess.register(
        process_ref=UUID(int=1),
        name="Fulfillment",
        criticality_label="business-defined",
    )
    repository.add(process)

    need = ConnectivityNeed.declare(
        need_ref=UUID(int=2),
        interaction_ref=UUID(int=3),
        participant_component_ref=UUID(int=4),
        business_basis="fulfillment",
        created_by_subject="subject:alice",
    )
    process = process.add_need(need)
    repository.save_process(process, expected_version=1)
    process = process.retire_need(need.need_ref, retired_at=NOW)
    repository.save_process(process, expected_version=2)

    loaded = repository.get_process(process.process_ref)
    assert loaded == process
    assert loaded is not None
    assert loaded.needs[0].status is NeedStatus.RETIRED
    assert loaded.needs[0].interaction_ref == UUID(int=3)


def test_business_process_catalogue_query_applies_search_filters_sort_and_paging() -> None:
    repository = PostgresBusinessProcessRepository(DSN)
    alpha = BusinessProcess.register(
        process_ref=UUID(int=101),
        name="Alpha",
        criticality_label="HIGH",
    ).set_responsible_organization(
        external_reference="ORG-1",
        display_name="Operations",
    )
    beta = BusinessProcess.register(
        process_ref=UUID(int=102),
        name="Beta",
        criticality_label="LOW",
    ).set_responsible_organization(
        external_reference="ORG-2",
        display_name="Finance",
    )
    gamma = BusinessProcess.register(
        process_ref=UUID(int=103),
        name="Gamma",
        criticality_label="HIGH",
    ).set_responsible_organization(
        external_reference="ORG-1",
        display_name="Operations",
    )
    for process in (alpha, beta, gamma):
        repository.add(process)

    first = repository.query_processes(
        BusinessProcessCatalogueQuery(
            criticality_label="HIGH",
            organization_external_reference="ORG-1",
            sort_by=BusinessProcessSortField.NAME,
            sort_direction=SortDirection.DESC,
            page=1,
            page_size=1,
        )
    )
    assert first.total == 2
    assert [item.process_ref for item in first.items] == [UUID(int=103)]

    second = repository.query_processes(
        BusinessProcessCatalogueQuery(
            criticality_label="HIGH",
            organization_external_reference="ORG-1",
            sort_by=BusinessProcessSortField.NAME,
            sort_direction=SortDirection.DESC,
            page=2,
            page_size=1,
        )
    )
    assert [item.process_ref for item in second.items] == [UUID(int=101)]

    searched = repository.query_processes(BusinessProcessCatalogueQuery(search="Beta"))
    assert searched.total == 1
    assert [item.process_ref for item in searched.items] == [UUID(int=102)]

    by_criticality = repository.query_processes(
        BusinessProcessCatalogueQuery(
            sort_by=BusinessProcessSortField.CRITICALITY_LABEL,
            sort_direction=SortDirection.DESC,
        )
    )
    assert by_criticality.items[0].process_ref == UUID(int=102)
