from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID, uuid4

from napms.contexts.authority_management.domain.model import Principal
from napms.contexts.resource_catalogue.application.ports import (
    ResourceCatalogueRepository,
    ResourceNotFound,
    ResourceVersionConflict,
)
from napms.contexts.resource_catalogue.domain.model import (
    AddressRealization,
    Resource,
    ResponsibilityRole,
)


@dataclass(frozen=True)
class MutationContext:
    principal: Principal
    effective_at: datetime


class ResourceCatalogueApplication:
    def __init__(
        self,
        *,
        resources: ResourceCatalogueRepository,
        new_ref: Callable[[], UUID] = uuid4,
    ) -> None:
        self._resources = resources
        self._new_ref = new_ref

    def list_resources(self) -> tuple[Resource, ...]:
        return self._resources.list()

    def get_resource(self, resource_ref: UUID) -> Resource | None:
        return self._resources.get(resource_ref)

    def register_resource(
        self,
        *,
        display_name: str,
        authority_scope_ref: str,
        context: MutationContext,
    ) -> Resource:
        self._admit(context)
        resource = Resource.register(
            resource_ref=self._new_ref(),
            display_name=display_name,
            authority_scope_ref=authority_scope_ref,
        )
        self._resources.add(resource)
        return resource

    def add_endpoint(
        self,
        *,
        resource_ref: UUID,
        expected_version: int,
        context: MutationContext,
    ) -> Resource:
        endpoint_ref = self._new_ref()
        return self._change(
            resource_ref=resource_ref,
            expected_version=expected_version,
            context=context,
            transform=lambda resource: resource.add_endpoint(endpoint_ref),
        )

    def set_endpoint_address(
        self,
        *,
        resource_ref: UUID,
        endpoint_ref: UUID,
        address: AddressRealization,
        expected_version: int,
        context: MutationContext,
    ) -> Resource:
        fact_ref = self._new_ref()
        return self._change(
            resource_ref=resource_ref,
            expected_version=expected_version,
            context=context,
            transform=lambda resource: resource.set_endpoint_address(
                endpoint_ref,
                address,
                fact_ref=fact_ref,
                effective_at=context.effective_at,
                subject=context.principal.subject,
            ),
        )

    def clear_endpoint_address(
        self,
        *,
        resource_ref: UUID,
        endpoint_ref: UUID,
        expected_version: int,
        context: MutationContext,
    ) -> Resource:
        return self._change(
            resource_ref=resource_ref,
            expected_version=expected_version,
            context=context,
            transform=lambda resource: resource.clear_endpoint_address(
                endpoint_ref,
                effective_at=context.effective_at,
            ),
        )

    def set_site(
        self,
        *,
        resource_ref: UUID,
        site_ref: UUID | None,
        expected_version: int,
        context: MutationContext,
    ) -> Resource:
        fact_ref = self._new_ref() if site_ref is not None else None
        return self._change(
            resource_ref=resource_ref,
            expected_version=expected_version,
            context=context,
            transform=lambda resource: resource.set_site(
                site_ref,
                fact_ref=fact_ref,
                effective_at=context.effective_at,
                subject=context.principal.subject,
            ),
        )

    def set_responsibility(
        self,
        *,
        resource_ref: UUID,
        role: ResponsibilityRole,
        group_ref: UUID | None,
        expected_version: int,
        context: MutationContext,
    ) -> Resource:
        fact_ref = self._new_ref() if group_ref is not None else None
        return self._change(
            resource_ref=resource_ref,
            expected_version=expected_version,
            context=context,
            transform=lambda resource: resource.set_responsibility(
                role,
                group_ref,
                fact_ref=fact_ref,
                effective_at=context.effective_at,
                subject=context.principal.subject,
            ),
        )

    @staticmethod
    def _admit(context: MutationContext) -> None:
        if "resource.write" not in context.principal.instance_permissions:
            raise PermissionError("resource.write is required")

    def _change(
        self,
        *,
        resource_ref: UUID,
        expected_version: int,
        context: MutationContext,
        transform: Callable[[Resource], Resource],
    ) -> Resource:
        self._admit(context)
        resource = self._resources.get(resource_ref)
        if resource is None:
            raise ResourceNotFound(str(resource_ref))
        if resource.version != expected_version:
            raise ResourceVersionConflict(str(resource_ref))
        updated = transform(resource)
        self._resources.save(updated, expected_version=expected_version)
        return updated
