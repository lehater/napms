from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from napms.resource_catalogue.application.curation_read import (
    ResourceCatalogueListItem,
    ResourceCatalogueWorkspacePage,
)
from napms.resource_catalogue.domain.model import Resource
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.catalogue_resource_workspace_http import (
    create_catalogue_resource_workspace_router,
)
from napms.runtime.http_api import PublicApiError


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


class Recorder:
    def __init__(self):
        self.calls = []

    def execute_workspace(self, **kwargs):
        self.calls.append(kwargs)
        return ResourceCatalogueWorkspacePage(
            items=(
                ResourceCatalogueListItem(
                    resource=Resource("res-orders", "prov:orders", "Orders DB"),
                    has_effective_realization=True,
                    has_effective_scope_affiliation=True,
                    has_effective_responsibility=True,
                    has_effective_contact=False,
                ),
            ),
            page=kwargs["page"],
            page_size=kwargs["page_size"],
            has_more=False,
            as_of=kwargs["as_of"],
            responsibility_scope=kwargs["responsibility_scope"],
        )


def _client_for():
    recorder = Recorder()
    scope = SimpleNamespace(
        resources=SimpleNamespace(list_resources=recorder),
    )

    @contextmanager
    def open_scope():
        yield scope

    sessions = InMemorySessionStore(new_session_id=lambda: "session-1")
    sessions.create(AuthenticatedActor(actor_id="actor-1", login="local-reader"))

    app = FastAPI()

    @app.exception_handler(PublicApiError)
    async def public_api_error_handler(request: Request, exc: PublicApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    app.include_router(
        create_catalogue_resource_workspace_router(
            sessions=sessions,
            open_scope=open_scope,
            clock=lambda: NOW,
        )
    )
    return TestClient(app), recorder


def test_resource_workspace_projects_scope_search_as_of_and_completeness():
    client, recorder = _client_for()

    response = client.get(
        "/api/v1/catalogues/resource-workspace",
        params={
            "page": 2,
            "pageSize": 25,
            "search": "orders",
            "responsibilityScope": "payments-team",
            "asOf": NOW.isoformat(),
        },
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 2
    assert payload["pageSize"] == 25
    assert payload["asOf"] == NOW.isoformat()
    assert payload["responsibilityScope"] == "payments-team"
    assert payload["items"][0]["resourceReference"] == "res-orders"
    assert payload["items"][0]["currentFacts"] == {
        "hasRealization": True,
        "hasScopeAffiliation": True,
        "hasResponsibility": True,
        "hasContact": False,
    }
    assert recorder.calls == [
        {
            "page": 2,
            "page_size": 25,
            "search": "orders",
            "include_retired": False,
            "responsibility_scope": "payments-team",
            "as_of": NOW,
        }
    ]


def test_resource_workspace_uses_server_clock_when_as_of_is_omitted():
    client, recorder = _client_for()

    response = client.get(
        "/api/v1/catalogues/resource-workspace",
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    assert recorder.calls[0]["as_of"] == NOW


def test_resource_workspace_requires_authenticated_session():
    client, recorder = _client_for()

    response = client.get("/api/v1/catalogues/resource-workspace")

    assert response.status_code == 401
    assert recorder.calls == []


def test_resource_workspace_rejects_naive_explicit_as_of():
    client, recorder = _client_for()

    response = client.get(
        "/api/v1/catalogues/resource-workspace",
        params={"asOf": "2026-09-10T12:00:00"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 422
    assert recorder.calls == []
