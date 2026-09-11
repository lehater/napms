from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from napms.contexts.application_catalogue.presentation.http.legacy_temporal import (
    create_application_catalogue_temporal_router,
)
from napms.contexts.application_catalogue.application.curation.bindings import (
    DeploymentBindingMutationResult,
)
from napms.contexts.application_catalogue.application.curation.structure import (
    CatalogueMutationOutcome,
)
from napms.contexts.application_catalogue.domain.model import DeploymentResourceBinding
from napms.platform.auth.local import AuthenticatedActor, InMemorySessionStore
from napms.platform.http.api import PublicApiError


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
START = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
DEPLOYMENT_ID = UUID("00000000-0000-0000-0000-000000006101")


class Recorder:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, command):
        self.calls.append(command)
        return self.result


def _client_for():
    ended_binding = DeploymentResourceBinding(
        reference_id="binding:orders",
        component_deployment_id=DEPLOYMENT_ID,
        resource_reference="resource:orders",
        valid_from=START,
        valid_to=NOW,
        provenance_reference="provenance:binding:create",
        end_provenance_reference="provenance:binding:end",
        version=5,
    )
    end_binding = Recorder(
        DeploymentBindingMutationResult(
            CatalogueMutationOutcome.UPDATED,
            binding=ended_binding,
            result_version=ended_binding.version,
        )
    )
    scope = SimpleNamespace(
        applications=SimpleNamespace(
            end_deployment_resource_binding=end_binding,
        )
    )

    @contextmanager
    def open_scope():
        yield scope

    sessions = InMemorySessionStore(new_session_id=lambda: "session-1")
    sessions.create(AuthenticatedActor(actor_id="actor-1", login="local-admin"))

    app = FastAPI()

    @app.exception_handler(PublicApiError)
    async def public_api_error_handler(request: Request, exc: PublicApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )

    app.include_router(
        create_application_catalogue_temporal_router(
            sessions=sessions,
            open_scope=open_scope,
            clock=lambda: NOW,
        )
    )
    return TestClient(app), end_binding


def test_end_binding_uses_relation_reference_version_and_server_context():
    client, recorder = _client_for()

    response = client.post(
        "/api/v1/catalogues/deployment-resource-bindings/binding:orders/end",
        json={
            "validTo": NOW.isoformat(),
            "expectedVersion": 4,
        },
        headers={"Idempotency-Key": "binding-end-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    assert response.json()["binding"]["version"] == 5
    command = recorder.calls[0]
    assert command.binding_reference == "binding:orders"
    assert command.expected_version == 4
    assert command.actor_id == "actor-1"
    assert command.effective_time == NOW
    assert command.idempotency_key == "binding-end-1"
