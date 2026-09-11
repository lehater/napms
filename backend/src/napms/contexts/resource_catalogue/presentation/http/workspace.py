from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable, Literal

from fastapi import APIRouter, Header, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from napms.contexts.resource_catalogue.presentation.http.curation import (
    realization_dto,
    resource_dto,
    resource_persistence_error,
    responsibility_dto,
    scope_affiliation_dto,
)
from napms.contexts.resource_catalogue.presentation.http.support import (
    mutation_response,
    require_aware,
    require_mutation_success,
)
from napms.contexts.resource_catalogue.application.curation import (
    RenameResourceCommand,
    RetireResourceCommand,
)
from napms.contexts.resource_catalogue.application.ports import ResourceCataloguePersistenceError
from napms.platform.auth.local import InMemorySessionStore
from napms.platform.http.support import PublicApiError, require_actor


ResourceWorkspaceDataState = Literal[
    "missing-address",
    "missing-scope",
    "missing-responsibility",
]
ResourceWorkspaceLifecycle = Literal["active", "retired", "all"]
ResourceWorkspaceSortBy = Literal["name", "reference", "lifecycle"]
ResourceWorkspaceSortDirection = Literal["asc", "desc"]


class RenameCatalogueResourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    display_name: str = Field(alias="displayName", min_length=1, max_length=256)
    expected_version: int = Field(alias="expectedVersion", ge=1)


class RetireCatalogueResourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    expected_version: int = Field(alias="expectedVersion", ge=1)


def create_catalogue_resource_workspace_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager],
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/api/v1/catalogues/resource-workspace",
        name="ListCatalogueResourceWorkspace",
    )
    def list_resource_workspace(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None, max_length=256),
        responsibilityScope: str | None = Query(None, max_length=512),
        dataState: ResourceWorkspaceDataState | None = Query(None),
        lifecycle: ResourceWorkspaceLifecycle = Query("active"),
        sortBy: ResourceWorkspaceSortBy = Query("name"),
        sortDirection: ResourceWorkspaceSortDirection = Query("asc"),
        asOf: datetime | None = Query(None),
        includeRetired: bool | None = Query(None),
    ):
        require_actor(sessions, request)
        as_of = asOf or clock()
        require_aware(as_of, "asOf")
        effective_lifecycle: ResourceWorkspaceLifecycle = lifecycle
        if includeRetired and lifecycle == "active":
            effective_lifecycle = "all"
        try:
            with open_scope() as scope:
                result = scope.resources.list_resources.execute_workspace(
                    page=page,
                    page_size=pageSize,
                    search=search,
                    lifecycle=effective_lifecycle,
                    responsibility_scope=responsibilityScope,
                    data_state=dataState,
                    sort_by=sortBy,
                    sort_direction=sortDirection,
                    as_of=as_of,
                )
        except ResourceCataloguePersistenceError as exc:
            raise resource_persistence_error() from exc

        return {
            "items": [
                {
                    **resource_dto(item.resource),
                    "currentFacts": {
                        "hasRealization": item.has_effective_realization,
                        "hasScopeAffiliation": item.has_effective_scope_affiliation,
                        "hasResponsibility": item.has_effective_responsibility,
                        "hasContact": item.has_effective_contact,
                    },
                    "currentAddresses": list(item.current_addresses),
                    "currentScopes": list(item.current_scopes),
                    "technicalOwners": list(item.technical_owners),
                }
                for item in result.items
            ],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
            "total": result.total,
            "counts": {
                "all": result.counts.all,
                "active": result.counts.active,
                "retired": result.counts.retired,
                "missingAddress": result.counts.missing_address,
                "missingScope": result.counts.missing_scope,
                "missingResponsibility": result.counts.missing_responsibility,
            },
            "asOf": result.as_of.isoformat(),
            "responsibilityScope": result.responsibility_scope,
            "dataState": result.data_state,
            "lifecycle": result.lifecycle,
            "sortBy": result.sort_by,
            "sortDirection": result.sort_direction,
        }

    @router.get(
        "/api/v1/catalogues/resource-history/{resource_reference:path}",
        name="ReadCatalogueResourceHistory",
    )
    def read_resource_history(
        resource_reference: str,
        request: Request,
    ):
        require_actor(sessions, request)
        read_at = clock()
        require_aware(read_at, "clock")
        try:
            with open_scope() as scope:
                result = scope.resources.read_resource.execute_history(
                    resource_reference=resource_reference,
                )
        except ResourceCataloguePersistenceError as exc:
            raise resource_persistence_error() from exc
        if result is None:
            raise PublicApiError(
                status_code=404,
                code="CatalogueResourceNotFound",
                message="The catalogue Resource was not found.",
            )
        return {
            "resource": resource_dto(result.resource),
            "asOf": read_at.isoformat(),
            "realizations": [realization_dto(item) for item in result.realizations],
            "scopeAffiliations": [
                scope_affiliation_dto(item) for item in result.scope_affiliations
            ],
            "responsibilities": [
                responsibility_dto(item) for item in result.responsibilities
            ],
        }

    @router.post(
        "/api/v1/catalogues/resources/{resource_reference:path}/rename",
        name="RenameCatalogueResource",
    )
    def rename_resource(
        resource_reference: str,
        payload: RenameCatalogueResourceRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=256,
        ),
    ):
        actor_id = require_actor(sessions, request)
        try:
            with open_scope() as scope:
                result = scope.resources.rename_resource.execute(
                    RenameResourceCommand(
                        resource_reference=resource_reference,
                        display_name=payload.display_name,
                        expected_version=payload.expected_version,
                        actor_id=actor_id,
                        effective_time=clock(),
                        idempotency_key=idempotency_key,
                    )
                )
        except ResourceCataloguePersistenceError as exc:
            raise resource_persistence_error() from exc
        require_mutation_success(result.outcome)
        return mutation_response(
            result.outcome,
            {"resource": resource_dto(result.resource)},
        )

    @router.post(
        "/api/v1/catalogues/resources/{resource_reference:path}/retire",
        name="RetireCatalogueResource",
    )
    def retire_resource(
        resource_reference: str,
        payload: RetireCatalogueResourceRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=256,
        ),
    ):
        actor_id = require_actor(sessions, request)
        try:
            with open_scope() as scope:
                result = scope.resources.retire_resource.execute(
                    RetireResourceCommand(
                        resource_reference=resource_reference,
                        expected_version=payload.expected_version,
                        actor_id=actor_id,
                        effective_time=clock(),
                        idempotency_key=idempotency_key,
                    )
                )
        except ResourceCataloguePersistenceError as exc:
            raise resource_persistence_error() from exc
        require_mutation_success(result.outcome)
        return mutation_response(
            result.outcome,
            {"resource": resource_dto(result.resource)},
        )

    return router
