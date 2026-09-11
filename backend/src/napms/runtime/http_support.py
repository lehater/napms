from typing import Any
from uuid import uuid4

from fastapi import Request
from fastapi.responses import JSONResponse

from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore


SESSION_COOKIE_NAME = "napms_session"


class PublicApiError(Exception):
    def __init__(
        self,
        *,
        status_code: int,
        code: str,
        message: str,
        details: dict[str, Any] | None = None,
        dependency: str | None = None,
    ) -> None:
        super().__init__(code)
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details
        self.dependency = dependency


def error_response(
    request: Request,
    *,
    status_code: int,
    code: str,
    message: str,
    details: dict | None = None,
    dependency: str | None = None,
) -> JSONResponse:
    request.state.semantic_outcome = code
    if dependency is not None and not getattr(request.state, "dependency", None):
        request.state.dependency = dependency
    error = {
        "code": code,
        "message": message,
        "correlationId": getattr(request.state, "correlation_id", str(uuid4())),
    }
    if details is not None:
        error["details"] = details
    return JSONResponse(status_code=status_code, content={"error": error})


def authenticated_actor(
    sessions: InMemorySessionStore,
    request: Request,
) -> AuthenticatedActor:
    actor = sessions.get(request.cookies.get(SESSION_COOKIE_NAME))
    if actor is None:
        raise PublicApiError(
            status_code=401,
            code="AuthenticationRequired",
            message="Authentication is required.",
        )
    request.state.actor_id = actor.actor_id
    return actor


def require_actor(sessions: InMemorySessionStore, request: Request) -> str:
    return authenticated_actor(sessions, request).actor_id


def set_outcome(request: Request, outcome: str) -> None:
    request.state.semantic_outcome = outcome


def set_dependency(request: Request, dependency: str) -> None:
    request.state.dependency = dependency
