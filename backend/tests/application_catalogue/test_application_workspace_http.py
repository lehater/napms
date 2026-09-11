from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from napms.contexts.application_catalogue.infrastructure.integrations.dcs_json_codec import JsonDcsProjectionCodec
from napms.contexts.application_catalogue.presentation.http.application_workspace import (
    create_catalogue_application_workspace_router,
)
from napms.contexts.application_catalogue.application.curation_detail import (
    ApplicationCatalogueTreeDetail,
    ComponentCatalogueDetail,
    ComponentDeploymentCatalogueDetail,
    DcsCatalogueSummary,
)
from napms.contexts.application_catalogue.application.deployment_curation import (
    ComponentDeploymentMutationResult,
)
from napms.contexts.application_catalogue.application.structure_curation import (
    ApplicationMutationResult,
    CatalogueMutationOutcome,
    ComponentMutationResult,
)
from napms.contexts.application_catalogue.domain.model import (
    Application,
    CatalogueLifecycleState,
    Component,
    ComponentDeployment,
)
from napms.workflows.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortRange,
)
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_api import PublicApiError


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
APP = UUID("00000000-0000-0000-0000-000000008001")
COMPONENT = UUID("00000000-0000-0000-0000-000000008002")
SOURCE = UUID("00000000-0000-0000-0000-000000008003")
DESTINATION = UUID("00000000-0000-0000-0000-000000008004")
DCS = UUID("00000000-0000-0000-0000-000000008005")


class Recorder:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, command=None, **kwargs):
        self.calls.append(command if command is not None else kwargs)
        return self.result


def _tree():
    payload = JsonDcsProjectionCodec().encode(
        (
            DcsTrafficAlternative(
                protocol="tcp",
                source_ports=PortConstraint.any(),
                destination_ports=PortConstraint.ranged(PortRange(443, 443)),
                service_reference="https",
            ),
        )
    )
    revision = DcsCatalogueSummary(
        revision_id=DCS,
        source_component_deployment_id=SOURCE,
        destination_component_deployment_id=DESTINATION,
        projection_payload=payload,
        display_name="HTTPS Orders API",
        provenance_reference="prov:dcs",
    )
    return ApplicationCatalogueTreeDetail(
        application=Application(APP, "Order Management", "prov:app"),
        components=(
            ComponentCatalogueDetail(
                component=Component(COMPONENT, APP, "Web UI", "prov:component"),
                deployments=(
                    ComponentDeploymentCatalogueDetail(
                        deployment=ComponentDeployment(
                            SOURCE,
                            COMPONENT,
                            "prov:source",
                            display_name="production",
                        ),
                        effective_resource_bindings=(),
                        dcs_revisions=(revision,),
                    ),
                ),
            ),
        ),
        as_of=NOW,
    )


def client_for():
    sessions = InMemorySessionStore(new_session_id=lambda: "session-1")
    sessions.create(AuthenticatedActor(actor_id="actor-1", login="local-admin"))

    updated_application = Application(
        APP,
        "Order Management 2",
        "prov:app",
        version=2,
    )
    retired_application = Application(
        APP,
        "Order Management",
        "prov:app",
        lifecycle_state=CatalogueLifecycleState.RETIRED,
        retirement_provenance_reference="prov:app:retire",
        version=2,
    )
    updated_component = Component(
        COMPONENT,
        APP,
        "Web Frontend",
        "prov:component",
        version=2,
    )
    retired_component = Component(
        COMPONENT,
        APP,
        "Web UI",
        "prov:component",
        lifecycle_state=CatalogueLifecycleState.RETIRED,
        retirement_provenance_reference="prov:component:retire",
        version=2,
    )
    updated_deployment = ComponentDeployment(
        SOURCE,
        COMPONENT,
        "prov:source",
        display_name="prod",
        version=2,
    )
    retired_deployment = ComponentDeployment(
        SOURCE,
        COMPONENT,
        "prov:source",
        display_name="production",
        lifecycle_state=CatalogueLifecycleState.RETIRED,
        retirement_provenance_reference="prov:deployment:retire",
        version=2,
    )

    recorders = {
        "read_application_tree": Recorder(_tree()),
        "rename_application": Recorder(
            ApplicationMutationResult(
                CatalogueMutationOutcome.UPDATED,
                application=updated_application,
                result_version=2,
            )
        ),
        "retire_application": Recorder(
            ApplicationMutationResult(
                CatalogueMutationOutcome.UPDATED,
                application=retired_application,
                result_version=2,
            )
        ),
        "rename_component": Recorder(
            ComponentMutationResult(
                CatalogueMutationOutcome.UPDATED,
                component=updated_component,
                result_version=2,
            )
        ),
        "retire_component": Recorder(
            ComponentMutationResult(
                CatalogueMutationOutcome.UPDATED,
                component=retired_component,
                result_version=2,
            )
        ),
        "rename_component_deployment": Recorder(
            ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.UPDATED,
                deployment=updated_deployment,
                result_version=2,
            )
        ),
        "retire_component_deployment": Recorder(
            ComponentDeploymentMutationResult(
                CatalogueMutationOutcome.UPDATED,
                deployment=retired_deployment,
                result_version=2,
            )
        ),
    }
    applications = SimpleNamespace(**recorders)
    scope = SimpleNamespace(applications=applications)

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
        create_catalogue_application_workspace_router(
            sessions=sessions,
            open_scope=open_scope,
            clock=lambda: NOW,
        )
    )
    return TestClient(app), recorders


def test_application_workspace_decodes_saved_dcs_traffic_semantics():
    client, recorders = client_for()

    response = client.get(
        f"/api/v1/catalogues/application-workspace/{APP}",
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    revision = response.json()["components"][0]["deployments"][0]["dcsRevisions"][0]
    assert revision["displayName"] == "HTTPS Orders API"
    assert revision["trafficAlternatives"] == [
        {
            "protocol": "tcp",
            "sourcePorts": {"kind": "Any"},
            "destinationPorts": {
                "kind": "Ranges",
                "ranges": [{"first": 443, "last": 443}],
            },
            "serviceReference": "https",
        }
    ]
    call = recorders["read_application_tree"].calls[0]
    assert call["application_id"] == APP
    assert call["as_of"] == NOW


def test_application_rename_uses_actor_server_time_version_and_idempotency():
    client, recorders = client_for()

    response = client.post(
        f"/api/v1/catalogues/applications/{APP}/rename",
        json={"displayName": "Order Management 2", "expectedVersion": 1},
        headers={"Idempotency-Key": "rename-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    assert response.json()["application"]["displayName"] == "Order Management 2"
    command = recorders["rename_application"].calls[0]
    assert command.application_id == APP
    assert command.display_name == "Order Management 2"
    assert command.expected_version == 1
    assert command.actor_id == "actor-1"
    assert command.effective_time == NOW
    assert command.idempotency_key == "rename-1"


def test_component_and_deployment_retirement_routes_preserve_expected_version():
    client, recorders = client_for()

    component_response = client.post(
        f"/api/v1/catalogues/components/{COMPONENT}/retire",
        json={"expectedVersion": 4},
        headers={"Idempotency-Key": "retire-component"},
        cookies={"napms_session": "session-1"},
    )
    deployment_response = client.post(
        f"/api/v1/catalogues/deployments/{SOURCE}/retire",
        json={"expectedVersion": 7},
        headers={"Idempotency-Key": "retire-deployment"},
        cookies={"napms_session": "session-1"},
    )

    assert component_response.status_code == 200
    assert deployment_response.status_code == 200
    assert recorders["retire_component"].calls[0].expected_version == 4
    assert recorders["retire_component_deployment"].calls[0].expected_version == 7


def test_workspace_requires_authenticated_session():
    client, recorders = client_for()

    response = client.get(f"/api/v1/catalogues/application-workspace/{APP}")

    assert response.status_code == 401
    assert recorders["read_application_tree"].calls == []
