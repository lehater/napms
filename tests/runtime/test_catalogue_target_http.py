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
from napms.application_catalogue.application.target_curation import (
    InteractionDefinitionMutationResult,
    TargetDependencyGroup,
    TargetDependencyKind,
    TargetMutationOutcome,
)
from napms.application_catalogue.application.target_ports import ActiveDependencyReference
from napms.application_catalogue.application.target_read import (
    ApplicationDefinitionSummary,
    DefinitionSummaryPage,
    DeploymentConnectivityPage,
    DeploymentConnectivityRow,
    TargetPage,
)
from napms.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)
from napms.application_catalogue.domain.model import Application
from napms.application_catalogue.domain.target_model import InteractionDefinition
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.catalogue_target_http import create_catalogue_target_router
from napms.runtime.http_api import PublicApiError


NOW = datetime(2026, 9, 11, 0, 0, tzinfo=timezone.utc)
APP = UUID("00000000-0000-0000-0000-000000009001")
SOURCE = UUID("00000000-0000-0000-0000-000000009002")
DESTINATION = UUID("00000000-0000-0000-0000-000000009003")
INTERACTION = UUID("00000000-0000-0000-0000-000000009004")
DEPLOYMENT = UUID("00000000-0000-0000-0000-000000009005")
DEPLOYMENT_INTERACTION = UUID("00000000-0000-0000-0000-000000009006")


def _traffic(port: int = 443):
    return (
        AuthoredDcsTrafficAlternative(
            protocol="tcp",
            source_ports=DcsPortConstraint.any(),
            destination_ports=DcsPortConstraint.ranged(DcsPortRange(port, port)),
            service_reference="https",
        ),
    )


class ExecuteRecorder:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, command):
        self.calls.append(command)
        return self.result


class ReadRecorder:
    def __init__(self):
        self.calls = []
        self.application = Application(
            APP,
            "CRM",
            "prov:app",
            description="Customer relationship management",
            domain="Sales",
            owner_reference="team:crm",
        )

    def list_definitions(self, **kwargs):
        self.calls.append(("list_definitions", kwargs))
        return DefinitionSummaryPage(
            items=(
                ApplicationDefinitionSummary(
                    application=self.application,
                    component_count=2,
                    interaction_count=4,
                    deployment_count=3,
                ),
            ),
            page=TargetPage(offset=kwargs["offset"], limit=kwargs["limit"], total=81),
        )

    def get_application_deployment(self, *, application_deployment_id):
        self.calls.append(
            ("get_application_deployment", {"application_deployment_id": application_deployment_id})
        )
        return SimpleNamespace(
            application_deployment_id=DEPLOYMENT,
            application_id=APP,
        )

    def list_deployment_connectivity(self, **kwargs):
        self.calls.append(("list_deployment_connectivity", kwargs))
        return DeploymentConnectivityPage(
            items=(
                DeploymentConnectivityRow(
                    deployment_interaction_id=DEPLOYMENT_INTERACTION,
                    interaction_definition_id=INTERACTION,
                    source_component_id=SOURCE,
                    source_component_name="Web",
                    source_resource_count=327,
                    destination_component_id=DESTINATION,
                    destination_component_name="API",
                    destination_resource_count=12,
                    traffic_alternatives=_traffic(),
                ),
            ),
            page=TargetPage(offset=kwargs["offset"], limit=kwargs["limit"], total=1),
            as_of=kwargs["as_of"],
        )


def _client(*, read=None, create_definition=None, update_traffic=None):
    sessions = InMemorySessionStore(new_session_id=lambda: "session-1")
    sessions.create(AuthenticatedActor(actor_id="actor-1", login="local-admin"))
    applications = SimpleNamespace(
        read=read or ReadRecorder(),
        create_definition=create_definition,
        update_interaction_traffic=update_traffic,
    )
    scope = SimpleNamespace(applications=applications)

    @contextmanager
    def open_scope():
        yield scope

    app = FastAPI()

    @app.exception_handler(PublicApiError)
    async def public_api_error_handler(request: Request, exc: PublicApiError):
        content = {"error": {"code": exc.code, "message": exc.message}}
        if exc.details is not None:
            content["error"]["details"] = exc.details
        return JSONResponse(status_code=exc.status_code, content=content)

    app.include_router(
        create_catalogue_target_router(
            sessions=sessions,
            open_scope=open_scope,
            clock=lambda: NOW,
        )
    )
    return TestClient(app), applications


def test_target_definition_list_requires_authentication():
    client, _ = _client()

    response = client.get("/api/v1/catalogues/application-definitions")

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AuthenticationRequired"


def test_target_definition_list_is_server_bounded_and_reports_total():
    read = ReadRecorder()
    client, _ = _client(read=read)

    response = client.get(
        "/api/v1/catalogues/application-definitions",
        params={
            "page": 2,
            "pageSize": 25,
            "search": "crm",
            "domain": "Sales",
            "ownerReference": "team:crm",
            "sort": "-name",
        },
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["page"] == 2
    assert body["pageSize"] == 25
    assert body["total"] == 81
    assert body["items"][0]["componentCount"] == 2
    assert body["items"][0]["interactionCount"] == 4
    assert body["items"][0]["deploymentCount"] == 3
    call = read.calls[0][1]
    assert call == {
        "offset": 25,
        "limit": 25,
        "search": "crm",
        "domain": "Sales",
        "owner_reference": "team:crm",
        "sort": "-name",
    }


def test_target_connectivity_uses_explicit_as_of_and_hides_compatibility_ids():
    read = ReadRecorder()
    client, _ = _client(read=read)
    as_of = "2026-09-10T21:30:00+00:00"

    response = client.get(
        f"/api/v1/catalogues/application-deployments/{DEPLOYMENT}/connectivity",
        params={"asOf": as_of},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["asOf"] == as_of
    row = body["items"][0]
    assert row["deploymentInteractionId"] == str(DEPLOYMENT_INTERACTION)
    assert row["sourceComponent"]["resourceCount"] == 327
    assert row["destinationComponent"]["resourceCount"] == 12
    serialized = response.text
    assert "componentDeploymentId" not in serialized
    assert "dcsContractRevisionId" not in serialized
    call = next(value for name, value in read.calls if name == "list_deployment_connectivity")
    assert call["as_of"] == datetime(2026, 9, 10, 21, 30, tzinfo=timezone.utc)


def test_target_create_definition_uses_session_actor_clock_and_idempotency():
    application = Application(
        APP,
        "CRM",
        "prov:app",
        description="Customer relationship management",
        domain="Sales",
        owner_reference="team:crm",
    )
    recorder = ExecuteRecorder(
        CreateApplicationResult(CreateApplicationOutcome.CREATED, application)
    )
    client, _ = _client(create_definition=recorder)

    response = client.post(
        "/api/v1/catalogues/application-definitions",
        json={
            "displayName": "CRM",
            "description": "Customer relationship management",
            "domain": "Sales",
            "ownerReference": "team:crm",
        },
        headers={"Idempotency-Key": "definition-create-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    command = recorder.calls[0]
    assert command.actor_id == "actor-1"
    assert command.effective_time == NOW
    assert command.idempotency_key == "definition-create-1"
    assert command.description == "Customer relationship management"
    assert command.domain == "Sales"
    assert command.owner_reference == "team:crm"


def test_target_dependency_conflict_returns_exact_count_and_bounded_preview():
    interaction = InteractionDefinition(
        interaction_definition_id=INTERACTION,
        application_id=APP,
        source_component_id=SOURCE,
        destination_component_id=DESTINATION,
        traffic_alternatives=_traffic(443),
        provenance_reference="prov:interaction",
    )
    recorder = ExecuteRecorder(
        InteractionDefinitionMutationResult(
            outcome=TargetMutationOutcome.DEPENDENCY_BLOCKED,
            interaction_definition=interaction,
            dependencies=(
                TargetDependencyGroup(
                    kind=TargetDependencyKind.CONNECTIVITY_REQUIREMENTS,
                    references=(
                        ActiveDependencyReference("requirement:1", "Primary dependency"),
                        ActiveDependencyReference("requirement:2"),
                    ),
                    total=327,
                ),
            ),
        )
    )
    client, _ = _client(update_traffic=recorder)

    response = client.post(
        f"/api/v1/catalogues/interaction-definitions/{INTERACTION}/traffic",
        json={
            "trafficAlternatives": [
                {
                    "protocol": "tcp",
                    "sourcePorts": {"kind": "Any", "ranges": []},
                    "destinationPorts": {
                        "kind": "Ranges",
                        "ranges": [{"first": 8443, "last": 8443}],
                    },
                    "serviceReference": "https-alt",
                }
            ],
            "expectedVersion": 1,
        },
        headers={"Idempotency-Key": "traffic-edit-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 409
    dependencies = response.json()["error"]["details"]["dependencies"]
    assert dependencies == [
        {
            "kind": "ConnectivityRequirements",
            "count": 327,
            "preview": [
                {"reference": "requirement:1", "displayName": "Primary dependency"},
                {"reference": "requirement:2", "displayName": None},
            ],
        }
    ]
