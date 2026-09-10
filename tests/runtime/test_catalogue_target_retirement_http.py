from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from napms.application_catalogue.application.target_curation import TargetMutationOutcome
from napms.application_catalogue.application.target_lifecycle import RetirementDependencyKind
from napms.application_catalogue.application.target_ports import ActiveDependencyReference
from napms.application_catalogue.application.target_retirement import (
    RetirementSubjectKind,
    TargetRetirementDependencyGroup,
    TargetRetirementMutationResult,
)
from napms.application_catalogue.domain.model import Application, CatalogueLifecycleState
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.catalogue_target_retirement_http import (
    create_catalogue_target_retirement_router,
)
from napms.runtime.http_api import PublicApiError


NOW = datetime(2026, 9, 11, 0, 0, tzinfo=timezone.utc)
APP = UUID("00000000-0000-0000-0000-000000009101")


class DependencyReader:
    def __init__(self):
        self.calls = []

    def summarize(self, **kwargs):
        self.calls.append(("summarize", kwargs))
        return (
            TargetRetirementDependencyGroup(
                kind=RetirementDependencyKind.COMPONENTS,
                total=327,
                references=(
                    ActiveDependencyReference("component:1", "Web"),
                    ActiveDependencyReference("component:2", "API"),
                ),
            ),
        )

    def page(self, **kwargs):
        self.calls.append(("page", kwargs))
        return TargetRetirementDependencyGroup(
            kind=kwargs["dependency_kind"],
            total=327,
            references=(ActiveDependencyReference("component:51", "Worker"),),
        )


class ExecuteRecorder:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, command):
        self.calls.append(command)
        return self.result


def _client(*, dependencies=None, retire_definition=None):
    sessions = InMemorySessionStore(new_session_id=lambda: "session-1")
    sessions.create(AuthenticatedActor(actor_id="actor-1", login="local-admin"))
    applications = SimpleNamespace(
        retirement_dependencies=dependencies or DependencyReader(),
        retire_definition=retire_definition,
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
        create_catalogue_target_retirement_router(
            sessions=sessions,
            open_scope=open_scope,
            clock=lambda: NOW,
        )
    )
    return TestClient(app), applications


def test_retirement_dependency_summary_is_exact_and_uses_server_time():
    dependencies = DependencyReader()
    client, _ = _client(dependencies=dependencies)

    response = client.get(
        f"/api/v1/catalogues/retirement-dependencies/application-definition/{APP}",
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "asOf": NOW.isoformat(),
        "dependencies": [
            {
                "kind": "Components",
                "count": 327,
                "preview": [
                    {"reference": "component:1", "displayName": "Web"},
                    {"reference": "component:2", "displayName": "API"},
                ],
            }
        ],
    }
    call = dependencies.calls[0][1]
    assert call["subject_kind"] is RetirementSubjectKind.APPLICATION_DEFINITION
    assert call["subject_id"] == APP
    assert call["as_of"] == NOW


def test_retirement_dependency_drilldown_is_server_paged():
    dependencies = DependencyReader()
    client, _ = _client(dependencies=dependencies)

    response = client.get(
        f"/api/v1/catalogues/retirement-dependencies/application-definition/{APP}/Components",
        params={"page": 2, "pageSize": 50},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    assert response.json()["total"] == 327
    assert response.json()["items"] == [
        {"reference": "component:51", "displayName": "Worker"}
    ]
    call = dependencies.calls[0][1]
    assert call["dependency_kind"] is RetirementDependencyKind.COMPONENTS
    assert call["offset"] == 50
    assert call["limit"] == 50


def test_retire_definition_returns_structured_blocker_counts():
    result = TargetRetirementMutationResult(
        outcome=TargetMutationOutcome.DEPENDENCY_BLOCKED,
        dependencies=(
            TargetRetirementDependencyGroup(
                kind=RetirementDependencyKind.APPLICATION_DEPLOYMENTS,
                total=18,
                references=(ActiveDependencyReference("deployment:1"),),
            ),
        ),
    )
    recorder = ExecuteRecorder(result)
    client, _ = _client(retire_definition=recorder)

    response = client.post(
        f"/api/v1/catalogues/application-definitions/{APP}/retire",
        json={"expectedVersion": 3},
        headers={"Idempotency-Key": "retire-definition-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["details"]["dependencies"] == [
        {
            "kind": "ApplicationDeployments",
            "count": 18,
            "preview": [{"reference": "deployment:1", "displayName": None}],
        }
    ]
    command = recorder.calls[0]
    assert command.application_id == APP
    assert command.expected_version == 3
    assert command.actor_id == "actor-1"
    assert command.effective_time == NOW
    assert command.idempotency_key == "retire-definition-1"


def test_retire_definition_returns_only_target_subject_identity():
    retired = Application(
        APP,
        "CRM",
        "prov:app",
        lifecycle_state=CatalogueLifecycleState.RETIRED,
        retirement_provenance_reference="prov:retire",
        version=4,
    )
    recorder = ExecuteRecorder(
        TargetRetirementMutationResult(
            outcome=TargetMutationOutcome.UPDATED,
            subject=retired,
        )
    )
    client, _ = _client(retire_definition=recorder)

    response = client.post(
        f"/api/v1/catalogues/application-definitions/{APP}/retire",
        json={"expectedVersion": 3},
        headers={"Idempotency-Key": "retire-definition-2"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    assert response.json() == {
        "outcome": "Updated",
        "subject": {
            "kind": "ApplicationDefinition",
            "reference": str(APP),
            "lifecycleState": "Retired",
            "version": 4,
        },
    }
    assert "componentDeploymentId" not in response.text
    assert "dcsContractRevisionId" not in response.text
