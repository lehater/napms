from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.contexts.resource_catalogue.domain.model import (
    AddressKind,
    AddressRealization,
    Resource,
    ResponsibilityRole,
)


NOW = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)
RESOURCE = UUID(int=1)
ENDPOINT = UUID(int=2)
SITE_A = UUID(int=3)
SITE_B = UUID(int=4)
OWNER_A = UUID(int=5)
OWNER_B = UUID(int=6)


def resource() -> Resource:
    return Resource.register(
        resource_ref=RESOURCE,
        display_name="Payments API",
        authority_scope_ref="scope:payments",
    )


def test_resource_and_endpoint_identity_survive_address_changes() -> None:
    value = resource().add_endpoint(ENDPOINT)
    value = value.set_endpoint_address(
        ENDPOINT,
        AddressRealization.host("10.20.30.40"),
        effective_at=NOW,
        subject="alice",
    )
    value = value.set_endpoint_address(
        ENDPOINT,
        AddressRealization.prefix("10.20.40.0/24"),
        effective_at=NOW + timedelta(minutes=1),
        subject="bob",
    )

    endpoint = value.endpoints[0]
    assert value.resource_ref == RESOURCE
    assert value.authority_scope_ref == "scope:payments"
    assert endpoint.endpoint_ref == ENDPOINT
    assert endpoint.current_address is not None
    assert endpoint.current_address.address.kind is AddressKind.PREFIX
    assert endpoint.current_address.address.value == "10.20.40.0/24"
    assert endpoint.address_history[0].address.value == "10.20.30.40"
    assert endpoint.address_history[0].effective_to == NOW + timedelta(minutes=1)


def test_endpoint_may_exist_without_current_address_and_clear_preserves_history() -> None:
    value = resource().add_endpoint(ENDPOINT)
    assert value.endpoints[0].current_address is None

    value = value.set_endpoint_address(
        ENDPOINT,
        AddressRealization.host("2001:db8::10"),
        effective_at=NOW,
        subject="alice",
    )
    value = value.clear_endpoint_address(
        ENDPOINT,
        effective_at=NOW + timedelta(minutes=1),
        subject="bob",
    )

    endpoint = value.endpoints[0]
    assert endpoint.current_address is None
    assert endpoint.address_history[0].address.value == "2001:db8::10"
    assert endpoint.address_history[0].effective_to == NOW + timedelta(minutes=1)


def test_prefix_input_is_strict_and_not_silently_masked() -> None:
    with pytest.raises(ValueError):
        AddressRealization.prefix("10.20.30.7/24")


def test_site_and_responsibility_are_singular_current_facts_with_history() -> None:
    value = resource()
    value = value.set_site(SITE_A, effective_at=NOW, subject="alice")
    value = value.set_site(
        SITE_B,
        effective_at=NOW + timedelta(minutes=1),
        subject="bob",
    )
    value = value.set_responsibility(
        ResponsibilityRole.OWNER,
        OWNER_A,
        effective_at=NOW,
        subject="alice",
    )
    value = value.set_responsibility(
        ResponsibilityRole.OWNER,
        OWNER_B,
        effective_at=NOW + timedelta(minutes=1),
        subject="bob",
    )

    assert value.current_site is not None
    assert value.current_site.site_ref == SITE_B
    assert value.site_history[0].site_ref == SITE_A
    owners = [item for item in value.responsibilities if item.role is ResponsibilityRole.OWNER]
    assert [item.group_ref for item in owners] == [OWNER_B]
    assert value.responsibility_history[0].group_ref == OWNER_A


def test_endpoints_are_added_only_by_explicit_membership() -> None:
    first = UUID(int=20)
    second = UUID(int=21)
    value = resource().add_endpoint(first)
    assert [item.endpoint_ref for item in value.endpoints] == [first]

    value = value.add_endpoint(second)
    assert [item.endpoint_ref for item in value.endpoints] == [first, second]
