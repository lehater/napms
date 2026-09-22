import os
from datetime import datetime, timezone
from uuid import UUID

import psycopg
import pytest

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
