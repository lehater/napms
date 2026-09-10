from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from napms.application_catalogue.application.curation import (
    CreateApplicationOutcome,
    CreateApplicationResult,
)
from napms.application_catalogue.domain.model import Application
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.catalogue_curation_http import create_catalogue_curation_router
from napms.runtime.http_api import PublicApiError


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
APPLICATION_ID = UUID("00000000-0000-0000-0000-000000006001")


class Recorder:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, command=None, **kwargs):
        self.calls.append(command if command is not None else kwargs)
        return self.result


def client_for():
    sessions = InMemorySessionStore(new_session_id=lambda: "session-1")
    sessions.create(AuthenticatedActor(actor_id="actor-1", login="local-admin"))

    create_application = Recorder(
        CreateApplicationResult(
            CreateApplicationOutcome.CREATED,
            application=Application(
                application_id=APPLICATION_ID,
                display_name="Orders",
                provenance_reference="prov:application",
            ),
        )
    )
    applications = SimpleNamespace(
        create_application=create_application,
    )
    scope = SimpleNamespace(applications=applications, resources=SimpleNamespace())

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
        create_catalogue_curation_router(
            sessions=sessions,
            open_scope=open_scope,
            clock=lambda: NOW,
        )
    )
    return TestClient(app), create_application


def test_create_application_uses_authenticated_actor_server_time_and_idempotency_key():
    client, recorder = client_for()

    response = client.post(
        "/api/v1/catalogues/applications",
        json={"displayName": "Orders"},
        headers={"Idempotency-Key": "request-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 201
    assert response.json()["application"]["applicationId"] == str(APPLICATION_ID)
    command = recorder.calls[0]
    assert command.display_name == "Orders"
    assert command.actor_id == "actor-1"
    assert command.effective_time == NOW
    assert command.idempotency_key == "request-1"


def test_create_application_requires_authenticated_session():
    client, recorder = client_for()

    response = client.post(
        "/api/v1/catalogues/applications",
        json={"displayName": "Orders"},
        headers={"Idempotency-Key": "request-1"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AuthenticationRequired"
    assert recorder.calls == []


def test_create_application_requires_idempotency_key():
    client, recorder = client_for()

    response = client.post(
        "/api/v1/catalogues/applications",
        json={"displayName": "Orders"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 422
    assert recorder.calls == []


def test_catalogue_create_rejects_client_owned_actor_and_provenance_fields():
    client, recorder = client_for()

    response = client.post(
        "/api/v1/catalogues/applications",
        json={
            "displayName": "Orders",
            "actorId": "spoofed",
            "provenanceReference": "client-controlled",
        },
        headers={"Idempotency-Key": "request-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 422
    assert recorder.calls == []
