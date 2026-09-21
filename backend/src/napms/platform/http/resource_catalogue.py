from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict

from napms.contexts.authority_management.domain.model import Principal
from napms.contexts.resource_catalogue.application.commands import (
    MutationContext,
    ResourceCatalogueApplication,
)
from napms.contexts.resource_catalogue.application.ports import (
    ResourceNotFound,
    ResourceVersionConflict,
)
from napms.contexts.resource_catalogue.domain.model import (
    AddressKind,
    AddressRealization,
    Resource,
    ResponsibilityRole,
)


class IdentityDependency(Protocol):
    def __call__(self) -> Principal: ...


class _Body(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class CreateResourceBody(_Body):
    display_name: str
    authority_scope_ref: str
    site_ref: UUID | None = None


class AddressBody(_Body):
    kind: AddressKind
    value: str


class SiteBody(_Body):
    site_ref: UUID | None


class ResponsibilityBody(_Body):
    organization_ref: UUID | None


def router(
    *,
    application: ResourceCatalogueApplication,
    identity: IdentityDependency,
) -> APIRouter:
    api = APIRouter(prefix="/v1")

    def version(value: str) -> int:
        try:
            return int(value.strip().strip('"'))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc

    def context(caller: Principal) -> MutationContext:
        return MutationContext(principal=caller, effective_at=datetime.now(timezone.utc))

    def mutate(call):
        try:
            return call()
        except PermissionError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from exc
        except ResourceVersionConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        except ResourceNotFound as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc

    @api.post("/resources", status_code=status.HTTP_201_CREATED)
    def create_resource(
        body: CreateResourceBody,
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        resource = mutate(
            lambda: application.register_resource(
                display_name=body.display_name,
                authority_scope_ref=body.authority_scope_ref,
                context=context(caller),
            )
        )
        if body.site_ref is not None:
            resource = mutate(
                lambda: application.set_site(
                    resource_ref=resource.resource_ref,
                    site_ref=body.site_ref,
                    expected_version=resource.version,
                    context=context(caller),
                )
            )
        return _view(resource)

    @api.get("/resources/{resource_ref}")
    def get_resource(
        resource_ref: UUID,
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        if "resource.read" not in caller.instance_permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        resource = application.get_resource(resource_ref)
        if resource is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
        return _view(resource)

    @api.post("/resources/{resource_ref}/endpoints", status_code=status.HTTP_201_CREATED)
    def add_endpoint(
        resource_ref: UUID,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        return _view(
            mutate(
                lambda: application.add_endpoint(
                    resource_ref=resource_ref,
                    expected_version=version(if_match),
                    context=context(caller),
                )
            )
        )

    @api.put("/resources/{resource_ref}/endpoints/{endpoint_ref}/address")
    def set_address(
        resource_ref: UUID,
        endpoint_ref: UUID,
        body: AddressBody,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        address = (
            AddressRealization.host(body.value)
            if body.kind is AddressKind.HOST
            else AddressRealization.prefix(body.value)
        )
        return _view(
            mutate(
                lambda: application.set_endpoint_address(
                    resource_ref=resource_ref,
                    endpoint_ref=endpoint_ref,
                    address=address,
                    expected_version=version(if_match),
                    context=context(caller),
                )
            )
        )

    @api.delete(
        "/resources/{resource_ref}/endpoints/{endpoint_ref}/address",
        status_code=status.HTTP_204_NO_CONTENT,
    )
    def clear_address(
        resource_ref: UUID,
        endpoint_ref: UUID,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> None:
        mutate(
            lambda: application.clear_endpoint_address(
                resource_ref=resource_ref,
                endpoint_ref=endpoint_ref,
                expected_version=version(if_match),
                context=context(caller),
            )
        )

    @api.put("/resources/{resource_ref}/site")
    def set_site(
        resource_ref: UUID,
        body: SiteBody,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        return _view(
            mutate(
                lambda: application.set_site(
                    resource_ref=resource_ref,
                    site_ref=body.site_ref,
                    expected_version=version(if_match),
                    context=context(caller),
                )
            )
        )

    @api.put("/resources/{resource_ref}/responsibilities/{role}")
    def set_responsibility(
        resource_ref: UUID,
        role: ResponsibilityRole,
        body: ResponsibilityBody,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        return _view(
            mutate(
                lambda: application.set_responsibility(
                    resource_ref=resource_ref,
                    role=role,
                    group_ref=body.organization_ref,
                    expected_version=version(if_match),
                    context=context(caller),
                )
            )
        )

    return api


def _view(resource: Resource) -> dict[str, object]:
    return {
        "resourceRef": str(resource.resource_ref),
        "displayName": resource.display_name,
        "authorityScopeRef": resource.authority_scope_ref,
        "version": resource.version,
        "current": {
            "siteRef": (
                None
                if resource.current_site is None
                else str(resource.current_site.site_ref)
            ),
            "endpoints": [
                {
                    "endpointRef": str(endpoint.endpoint_ref),
                    "address": (
                        None
                        if endpoint.current_address is None
                        else {
                            "kind": endpoint.current_address.address.kind.value,
                            "value": endpoint.current_address.address.value,
                        }
                    ),
                }
                for endpoint in resource.endpoints
            ],
            "responsibilities": [
                {
                    "role": fact.role.value,
                    "organizationRef": str(fact.group_ref),
                }
                for fact in resource.responsibilities
            ],
        },
        "history": {
            "sites": [_site_fact(item) for item in resource.site_history],
            "addresses": [
                {
                    "endpointRef": str(endpoint.endpoint_ref),
                    "facts": [_address_fact(item) for item in endpoint.address_history],
                }
                for endpoint in resource.endpoints
            ],
            "responsibilities": [
                _responsibility_fact(item) for item in resource.responsibility_history
            ],
        },
    }


def _site_fact(item) -> dict[str, object]:
    return {
        "factRef": str(item.fact_ref),
        "siteRef": str(item.site_ref),
        "effectiveFrom": item.effective_from.isoformat(),
        "effectiveTo": None if item.effective_to is None else item.effective_to.isoformat(),
        "changedBySubject": item.changed_by_subject,
    }


def _address_fact(item) -> dict[str, object]:
    return {
        "factRef": str(item.fact_ref),
        "kind": item.address.kind.value,
        "value": item.address.value,
        "effectiveFrom": item.effective_from.isoformat(),
        "effectiveTo": None if item.effective_to is None else item.effective_to.isoformat(),
        "changedBySubject": item.changed_by_subject,
    }


def _responsibility_fact(item) -> dict[str, object]:
    return {
        "factRef": str(item.fact_ref),
        "role": item.role.value,
        "organizationRef": str(item.group_ref),
        "effectiveFrom": item.effective_from.isoformat(),
        "effectiveTo": None if item.effective_to is None else item.effective_to.isoformat(),
        "changedBySubject": item.changed_by_subject,
    }
