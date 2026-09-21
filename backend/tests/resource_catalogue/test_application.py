from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.contexts.resource_catalogue.application.commands import (
    MutationContext,
    ResourceCatalogueApplication,
)
from napms.contexts.resource_catalogue.application.ports import (
    RESOURCE_CATALOGUE_AUTHORITY_SCOPE,
    RESOURCE_CATALOGUE_CURATION_ACTION,
    AuthorityDenied,
)
from napms.contexts.resource_catalogue.domain.model import Resource


NOW = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)


class MemoryResources:
    def __init__(self) -> None:
        self.values: dict[UUID, Resource] = {}
        self.save_count = 0

    def add(self, resource: Resource) -> None:
        self.values[resource.resource_ref] = resource

    def get(self, resource_ref: UUID) -> Resource | None:
        return self.values.get(resource_ref)

    def save(self, resource: Resource, *, expected_version: int) -> None:
        current = self.values[resource.resource_ref]
        assert current.version == expected_version
        self.values[resource.resource_ref] = resource
        self.save_count += 1


class Authority:
    def __init__(self, *, allowed: bool) -> None:
        self.allowed = allowed
        self.calls: list[tuple[str, str, str, datetime]] = []

    def require(
        self,
        *,
        principal: str,
        action: str,
        scope: str,
        evaluated_at: datetime,
    ) -> None:
        self.calls.append((principal, action, scope, evaluated_at))
        if not self.allowed:
            raise AuthorityDenied


class Refs:
    def __init__(self, *values: UUID) -> None:
        self._values = iter(values)

    def __call__(self) -> UUID:
        return next(self._values)


def test_register_resource_uses_server_owned_curation_action_and_scope() -> None:
    resources = MemoryResources()
    authority = Authority(allowed=True)
    app = ResourceCatalogueApplication(
        resources=resources,
        authority=authority,
        new_ref=Refs(UUID(int=100)),
    )

    value = app.register_resource(
        display_name="Orders",
        authority_scope_ref="scope:orders",
        context=MutationContext(principal="subject:alice", effective_at=NOW),
    )

    assert value.resource_ref == UUID(int=100)
    assert value.authority_scope_ref == "scope:orders"
    assert authority.calls == [
        (
            "subject:alice",
            RESOURCE_CATALOGUE_CURATION_ACTION,
            RESOURCE_CATALOGUE_AUTHORITY_SCOPE,
            NOW,
        )
    ]


def test_add_endpoint_uses_server_generated_stable_identity() -> None:
    resources = MemoryResources()
    initial = Resource.register(
        resource_ref=UUID(int=200),
        display_name="Billing",
        authority_scope_ref="scope:billing",
    )
    resources.add(initial)
    app = ResourceCatalogueApplication(
        resources=resources,
        authority=Authority(allowed=True),
        new_ref=Refs(UUID(int=201)),
    )

    updated = app.add_endpoint(
        resource_ref=initial.resource_ref,
        expected_version=initial.version,
        context=MutationContext(principal="subject:alice", effective_at=NOW),
    )

    assert updated.endpoints[0].endpoint_ref == UUID(int=201)


def test_denied_mutation_leaves_resource_truth_unchanged() -> None:
    resources = MemoryResources()
    initial = Resource.register(
        resource_ref=UUID(int=300),
        display_name="Billing",
        authority_scope_ref="scope:billing",
    )
    resources.add(initial)
    app = ResourceCatalogueApplication(
        resources=resources,
        authority=Authority(allowed=False),
        new_ref=Refs(UUID(int=301)),
    )

    with pytest.raises(AuthorityDenied):
        app.add_endpoint(
            resource_ref=initial.resource_ref,
            expected_version=initial.version,
            context=MutationContext(principal="subject:bob", effective_at=NOW),
        )

    assert resources.values[initial.resource_ref] == initial
    assert resources.save_count == 0
