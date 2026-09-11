from contextlib import AbstractContextManager
from typing import Callable

from fastapi import APIRouter, Query, Request

from napms.platform.auth.local import InMemorySessionStore
from napms.platform.http.support import PublicApiError, SESSION_COOKIE_NAME


def create_catalogue_discovery_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager],
) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/api/v1/catalogues/application-participants",
        name="ListCatalogueApplicationParticipants",
    )
    def list_application_participants(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None, max_length=256),
    ):
        actor = sessions.get(request.cookies.get(SESSION_COOKIE_NAME))
        if actor is None:
            raise PublicApiError(
                status_code=401,
                code="AuthenticationRequired",
                message="Authentication is required.",
            )
        request.state.actor_id = actor.actor_id

        with open_scope() as scope:
            result = scope.applications.list_participants.execute(
                page=page,
                page_size=pageSize,
                search=search,
            )
        return {
            "items": [
                {
                    "applicationId": str(item.application_id),
                    "applicationDisplayName": item.application_display_name,
                    "componentId": str(item.component_id),
                    "componentDisplayName": item.component_display_name,
                    "componentDeploymentId": str(item.component_deployment_id),
                    "deploymentDisplayName": item.deployment_display_name,
                }
                for item in result.items
            ],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
        }

    return router
