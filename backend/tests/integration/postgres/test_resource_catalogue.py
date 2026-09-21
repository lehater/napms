import os
from datetime import datetime, timedelta, timezone
from uuid import UUID

import psycopg
import pytest

from napms.contexts.resource_catalogue.domain.model import (
    AddressRealization,
    Resource,
    ResponsibilityRole,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.migration import (
    migrate,
)
from napms.contexts.resource_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresResourceCatalogueRepository,
)


pytestmark = pytest.mark.postgres

DSN = os.environ["NAPMS_TEST_POSTGRES_DSN"]
NOW = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def fresh_schema() -> None:
    with psycopg.connect(DSN) as connection:
        connection.execute("DROP SCHEMA IF EXISTS resource_catalogue CASCADE")
        migrate(connection)


def test_fresh_database_migrates_and_round_trips_resource_history() -> None:
    repository = PostgresResourceCatalogueRepository(DSN)
    resource = Resource.register(
        resource_ref=UUID(int=1),
        display_name="Payments",
        authority_scope_ref="scope:payments",
    )
    repository.add(resource)

    site_a = UUID(int=2)
    site_b = UUID(int=3)
    owner_a = UUID(int=4)
    owner_b = UUID(int=5)
    with psycopg.connect(DSN) as connection:
        connection.execute(
            "INSERT INTO resource_catalogue.site(site_ref, name) VALUES (%s, %s), (%s, %s)",
            (site_a, "Site A", site_b, "Site B"),
        )
        connection.execute(
            """
            INSERT INTO resource_catalogue.responsibility_group(group_ref, display_name)
            VALUES (%s, %s), (%s, %s)
            """,
            (owner_a, "Owner A", owner_b, "Owner B"),
        )

    endpoint = UUID(int=10)
    resource = resource.add_endpoint(endpoint)
    resource = resource.set_endpoint_address(
        endpoint,
        AddressRealization.host("10.0.0.10"),
        fact_ref=UUID(int=20),
        effective_at=NOW,
        subject="subject:alice",
    )
    resource = resource.set_endpoint_address(
        endpoint,
        AddressRealization.prefix("10.0.1.0/24"),
        fact_ref=UUID(int=21),
        effective_at=NOW + timedelta(minutes=1),
        subject="subject:bob",
    )
    resource = resource.set_site(
        site_a,
        fact_ref=UUID(int=30),
        effective_at=NOW,
        subject="subject:alice",
    )
    resource = resource.set_site(
        site_b,
        fact_ref=UUID(int=31),
        effective_at=NOW + timedelta(minutes=1),
        subject="subject:bob",
    )
    resource = resource.set_responsibility(
        ResponsibilityRole.OWNER,
        owner_a,
        fact_ref=UUID(int=40),
        effective_at=NOW,
        subject="subject:alice",
    )
    resource = resource.set_responsibility(
        ResponsibilityRole.OWNER,
        owner_b,
        fact_ref=UUID(int=41),
        effective_at=NOW + timedelta(minutes=1),
        subject="subject:bob",
    )

    repository.save(resource, expected_version=1)
    loaded = repository.get(resource.resource_ref)

    assert loaded == resource
    assert loaded is not None
    assert loaded.authority_scope_ref == "scope:payments"
    assert loaded.endpoints[0].address_history[0].fact_ref == UUID(int=20)
    assert loaded.site_history[0].changed_by_subject == "subject:alice"
    assert loaded.responsibility_history[0].fact_ref == UUID(int=40)


def test_optimistic_version_rejects_stale_save() -> None:
    repository = PostgresResourceCatalogueRepository(DSN)
    resource = Resource.register(
        resource_ref=UUID(int=100),
        display_name="Orders",
        authority_scope_ref="scope:orders",
    )
    repository.add(resource)
    changed = resource.add_endpoint(UUID(int=101))
    repository.save(changed, expected_version=1)

    stale = resource.add_endpoint(UUID(int=102))
    from napms.contexts.resource_catalogue.application.ports import ResourceVersionConflict

    with pytest.raises(ResourceVersionConflict):
        repository.save(stale, expected_version=1)
