from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Header, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from napms.resource_catalogue.adapters.http.curation import (
    resource_dto,
    resource_persistence_error,
)
from napms.resource_catalogue.application.curation import (
    RenameResourceCommand,
    RetireResourceCommand,
)
from napms.resource_catalogue.application.ports import ResourceCataloguePersistenceError
from napms.runtime.auth import InMemorySessionStore
from napms.runtime.http_support import (
    mutation_response,
    require_actor,
    require_aware,
    require_mutation_success,
)


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
        asOf: datetime | None = Query(None),
        includeRetired: bool = Query(False),
    ):
        require_actor(sessions, request)
        as_of = asOf or clock()
        require_aware(as_of, "asOf")
        try:
            with open_scope() as scope:
                result = scope.resources.list_resources.execute_workspace(
                    page=page,
                    page_size=pageSize,
                    search=search,
                    include_retired=includeRetired,
                    responsibility_scope=responsibilityScope,
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
                }
                for item in result.items
            ],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
            "asOf": result.as_of.isoformat(),
            "responsibilityScope": result.responsibility_scope,
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
