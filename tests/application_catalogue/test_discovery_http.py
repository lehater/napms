from contextlib import contextmanager
from types import SimpleNamespace
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from napms.application_catalogue.adapters.http.discovery import create_catalogue_discovery_router
from napms.application_catalogue.application.participant_discovery import (
    ApplicationCatalogueParticipant,
    ApplicationCatalogueParticipantPage,
)
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_api import PublicApiError


APPLICATION_ID = UUID("00000000-0000-0000-0000-000000006001")
COMPONENT_ID = UUID("00000000-0000-0000-0000-000000006002")
DEPLOYMENT_ID = UUID("00000000-0000-0000-0000-000000006003")


class Recorder:
    def __init__(self):
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)
        return ApplicationCatalogueParticipantPage(
            items=(
                ApplicationCatalogueParticipant(
                    application_id=APPLICATION_ID,
                    application_display_name="Orders",
                    component_id=COMPONENT_ID,
                    component_display_name="Orders API",
                    component_deployment_id=DEPLOYMENT_ID,
                    deployment_display_name="prod",
                ),
            ),
            page=kwargs["page"],
            page_size=kwargs["page_size"],
            has_more=False,
        )


def client_for():
    sessions = InMemorySessionStore(new_session_id=lambda: "session-1")
    sessions.create(AuthenticatedActor(actor_id="actor-1", login="local-admin"))
    recorder = Recorder()
    scope = SimpleNamespace(
        applications=SimpleNamespace(list_participants=recorder)
    )

    @contextmanager
    def open_scope():
        yield scope

    app = FastAPI()

    @app.exception_handler(PublicApiError)
    async def public_api_error_handler(request: Request, exc: PublicApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    app.include_router(
        create_catalogue_discovery_router(
            sessions=sessions,
            open_scope=open_scope,
        )
    )
    return TestClient(app), recorder


def test_participant_discovery_uses_backend_projection_and_paging():
    client, recorder = client_for()

    response = client.get(
        "/api/v1/catalogues/application-participants",
        params={"page": 2, "pageSize": 25, "search": "orders"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    assert recorder.calls == [
        {"page": 2, "page_size": 25, "search": "orders"}
    ]
    assert response.json() == {
        "items": [
            {
                "applicationId": str(APPLICATION_ID),
                "applicationDisplayName": "Orders",
                "componentId": str(COMPONENT_ID),
                "componentDisplayName": "Orders API",
                "componentDeploymentId": str(DEPLOYMENT_ID),
                "deploymentDisplayName": "prod",
            }
        ],
        "page": 2,
        "pageSize": 25,
        "hasMore": False,
    }


def test_participant_discovery_requires_session():
    client, recorder = client_for()

    response = client.get("/api/v1/catalogues/application-participants")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AuthenticationRequired"
    assert recorder.calls == []
