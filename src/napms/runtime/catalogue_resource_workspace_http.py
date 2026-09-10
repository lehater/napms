from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Query, Request

from napms.resource_catalogue.application.ports import ResourceCataloguePersistenceError
from napms.runtime.auth import InMemorySessionStore
from napms.runtime.catalogue_curation_http import (
    _require_actor,
    _require_aware,
    _resource_dto,
    _resource_persistence_error,
)


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
        _require_actor(sessions, request)
        as_of = asOf or clock()
        _require_aware(as_of, "asOf")
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
            raise _resource_persistence_error() from exc

        return {
            "items": [
                {
                    **_resource_dto(item.resource),
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

    return router
