import json
import logging
import re
import traceback
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable, ContextManager
from uuid import uuid4

from fastapi import Depends, FastAPI, Request, Response
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore, LocalPasswordAuthenticator
from napms.runtime.http_support import PublicApiError, SESSION_COOKIE_NAME, error_response

CORRELATION_HEADER = "X-Correlation-ID"
_CORRELATION_PATTERN = re.compile(r"^[A-Za-z0-9._:-]{1,128}$")
_LOGGER = logging.getLogger("napms.runtime.http")


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(slots=True)
class HttpApiDependencies:
    authenticator: LocalPasswordAuthenticator
    sessions: InMemorySessionStore
    open_scope: Callable[[], ContextManager[Any]]
    decisions: Any
    readiness: Callable[[], bool]
    clock: Callable[[], datetime] = _utc_now
    secure_cookie: bool = False


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    login: str = Field(min_length=1, max_length=256)
    password: str = Field(min_length=1, max_length=4096)


def configure_json_logging(*, level: int = logging.INFO) -> None:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    _LOGGER.handlers.clear()
    _LOGGER.addHandler(handler)
    _LOGGER.setLevel(level)
    _LOGGER.propagate = False


def _safe_correlation_id(raw: str | None) -> str:
    return raw if raw and _CORRELATION_PATTERN.fullmatch(raw) else str(uuid4())


def _correlation_id(request: Request) -> str:
    return getattr(request.state, "correlation_id", str(uuid4()))


def _set_outcome(request: Request, outcome: str) -> None:
    request.state.semantic_outcome = outcome


def _set_dependency(request: Request, dependency: str) -> None:
    request.state.dependency = dependency


def _error_response(request: Request, *, status_code: int, code: str, message: str, details: dict[str, Any] | None = None, dependency: str | None = None) -> JSONResponse:
    return error_response(request, status_code=status_code, code=code, message=message, details=details, dependency=dependency)


def _actor_dto(actor: AuthenticatedActor) -> dict[str, str]:
    return {"actorId": actor.actor_id, "login": actor.login}


def create_http_api(dependencies: HttpApiDependencies) -> FastAPI:
    from napms.contexts.access_policy.presentation.http.routes import create_access_policy_router
    from napms.contexts.access_policy.presentation.http.errors import register_access_policy_http_error_handlers
    from napms.contexts.application_catalogue.presentation.http.errors import register_application_catalogue_http_error_handlers
    from napms.contexts.authority_management.presentation.http.errors import register_authority_management_http_error_handlers
    from napms.contexts.connectivity_decision.presentation.http.routes import create_connectivity_decision_router
    from napms.contexts.connectivity_decision.presentation.http.errors import register_connectivity_decision_http_error_handlers
    from napms.contexts.connectivity_requirements.presentation.http.routes import create_connectivity_requirements_router
    from napms.contexts.connectivity_requirements.presentation.http.errors import register_connectivity_requirements_http_error_handlers
    from napms.workflows.policy_export.presentation.http.routes import create_policy_export_router
    from napms.workflows.policy_export.presentation.http.errors import register_policy_export_http_error_handlers
    from napms.workflows.requirement_policy_alignment.presentation.http.routes import create_requirement_policy_alignment_router
    from napms.workflows.scoped_connectivity_inventory.presentation.http.routes import create_scoped_connectivity_inventory_router

    app = FastAPI(title="NAPMS API", version="1")

    @app.middleware("http")
    async def runtime_boundary(request: Request, call_next):
        request.state.correlation_id = _safe_correlation_id(request.headers.get(CORRELATION_HEADER))
        request.state.operation = request.url.path
        request.state.semantic_outcome = "HttpCompleted"
        started = perf_counter()
        error: Exception | None = None
        try:
            response = await call_next(request)
        except Exception as exc:
            error = exc
            request.state.semantic_outcome = "InternalError"
            response = _error_response(request, status_code=500, code="InternalError", message="The operation could not be completed.")
        response.headers[CORRELATION_HEADER] = request.state.correlation_id
        event = {
            "event": "operation_completed", "operation": request.state.operation,
            "correlationId": request.state.correlation_id, "outcome": request.state.semantic_outcome,
            "httpStatus": response.status_code, "durationMs": round((perf_counter() - started) * 1000, 3),
        }
        actor_id = getattr(request.state, "actor_id", None)
        if actor_id:
            event["actorId"] = actor_id
        for state_name, event_name in (("rule_id", "ruleId"), ("requirement_id", "requirementId"), ("authority_reference", "authorityReference"), ("decision_reference", "decisionReference"), ("dependency", "dependency")):
            value = getattr(request.state, state_name, None)
            if value:
                event[event_name] = value
        if error is not None:
            event["exception"] = {"class": type(error).__name__, "stack": [frame.rstrip() for frame in traceback.format_list(traceback.extract_tb(error.__traceback__))]}
        level = logging.INFO
        if response.status_code >= 500:
            level = logging.ERROR if error is not None else logging.WARNING
        elif response.status_code >= 400:
            level = logging.WARNING
        _LOGGER.log(level, json.dumps(event, separators=(",", ":"), sort_keys=True))
        return response

    @app.exception_handler(StarletteHTTPException)
    async def starlette_http_error_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return _error_response(request, status_code=404, code="NotFound", message="The requested resource was not found.")
        if exc.status_code == 405:
            return _error_response(request, status_code=405, code="MethodNotAllowed", message="The requested method is not allowed.")
        return _error_response(request, status_code=exc.status_code, code="HttpError", message="The request could not be completed.")

    @app.exception_handler(PublicApiError)
    async def public_api_error_handler(request: Request, exc: PublicApiError):
        return _error_response(request, status_code=exc.status_code, code=exc.code, message=exc.message, details=exc.details, dependency=exc.dependency)

    @app.exception_handler(RequestValidationError)
    async def request_validation_error_handler(request: Request, exc: RequestValidationError):
        return _error_response(request, status_code=422, code="ValidationError", message="The request is invalid.")

    register_access_policy_http_error_handlers(app)
    register_connectivity_decision_http_error_handlers(app)
    register_connectivity_requirements_http_error_handlers(app)
    register_authority_management_http_error_handlers(app)
    register_policy_export_http_error_handlers(app)
    register_application_catalogue_http_error_handlers(app)

    def require_actor(request: Request) -> AuthenticatedActor:
        actor = dependencies.sessions.get(request.cookies.get(SESSION_COOKIE_NAME))
        if actor is None:
            raise PublicApiError(status_code=401, code="AuthenticationRequired", message="Authentication is required.")
        request.state.actor_id = actor.actor_id
        return actor

    @app.post("/api/v1/session", name="CreateSession")
    def create_session(payload: LoginRequest, request: Request):
        request.state.operation = "CreateSession"
        actor = dependencies.authenticator.authenticate(login=payload.login, password=payload.password)
        if actor is None:
            raise PublicApiError(status_code=401, code="AuthenticationFailed", message="Authentication failed.")
        session_id = dependencies.sessions.create(actor)
        request.state.actor_id = actor.actor_id
        _set_outcome(request, "Authenticated")
        response = JSONResponse(status_code=200, content={"actor": _actor_dto(actor)})
        response.set_cookie(key=SESSION_COOKIE_NAME, value=session_id, httponly=True, secure=dependencies.secure_cookie, samesite="strict", path="/")
        return response

    @app.get("/api/v1/session", name="GetSession")
    def get_session(request: Request, actor: AuthenticatedActor = Depends(require_actor)):
        request.state.operation = "GetSession"
        _set_outcome(request, "Authenticated")
        return {"actor": _actor_dto(actor)}

    @app.delete("/api/v1/session", status_code=204, name="DeleteSession")
    def delete_session(request: Request, actor: AuthenticatedActor = Depends(require_actor)):
        request.state.operation = "DeleteSession"
        dependencies.sessions.delete(request.cookies.get(SESSION_COOKIE_NAME))
        _set_outcome(request, "LoggedOut")
        response = Response(status_code=204)
        response.delete_cookie(key=SESSION_COOKIE_NAME, path="/", secure=dependencies.secure_cookie, httponly=True, samesite="strict")
        return response

    @app.get("/health/live", name="Liveness")
    def liveness(request: Request):
        request.state.operation = "Liveness"
        _set_outcome(request, "Alive")
        return {"status": "alive"}

    @app.get("/health/ready", name="Readiness")
    def readiness(request: Request):
        request.state.operation = "Readiness"
        try:
            ready = dependencies.readiness()
        except Exception:
            ready = False
        if not ready:
            _set_dependency(request, "PostgreSQL")
            _set_outcome(request, "NotReady")
            return JSONResponse(status_code=503, content={"status": "not-ready"})
        _set_outcome(request, "Ready")
        return {"status": "ready"}

    app.include_router(create_scoped_connectivity_inventory_router(sessions=dependencies.sessions, open_scope=dependencies.open_scope))
    app.include_router(create_requirement_policy_alignment_router(sessions=dependencies.sessions, open_scope=dependencies.open_scope))
    app.include_router(create_connectivity_requirements_router(sessions=dependencies.sessions, open_scope=dependencies.open_scope, clock=dependencies.clock))
    app.include_router(create_connectivity_decision_router(sessions=dependencies.sessions, open_scope=dependencies.open_scope, clock=dependencies.clock))
    app.include_router(create_access_policy_router(sessions=dependencies.sessions, open_scope=dependencies.open_scope, decisions=dependencies.decisions, clock=dependencies.clock))
    app.include_router(create_policy_export_router(sessions=dependencies.sessions, open_scope=dependencies.open_scope))
    return app
