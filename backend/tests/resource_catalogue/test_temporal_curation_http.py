from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from napms.contexts.resource_catalogue.presentation.http.temporal import (
    create_resource_catalogue_temporal_router,
)
from napms.contexts.resource_catalogue.application._temporal_curation import (
    TemporalCurationOutcome,
)
from napms.contexts.resource_catalogue.application.realization_curation import (
    RealizationMutationResult,
)
from napms.contexts.resource_catalogue.application.responsibility_curation import (
    ResponsibilityMutationResult,
)
from napms.contexts.resource_catalogue.application.scope_affiliation_curation import (
    ScopeAffiliationMutationResult,
)
from napms.contexts.resource_catalogue.domain.model import (
    EndpointAddress,
    ResourceRealizationVersion,
    ResourceScopeAffiliation,
)
from napms.contexts.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibility,
    ResourceResponsibilityRole,
)
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_api import PublicApiError


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
START = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)


class Recorder:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, command):
        self.calls.append(command)
        return self.result


def _client_for():
    replacement = ResourceRealizationVersion(
        fact_reference="realization:new",
        resource_reference="resource:orders",
        endpoint_realizations=(
            EndpointAddress("endpoint:new", "203.0.113.20"),
        ),
        valid_from=NOW,
        valid_to=None,
        provenance_reference="provenance:realization:new",
    )
    ended_affiliation = ResourceScopeAffiliation(
        affiliation_reference="affiliation:orders",
        resource_reference="resource:orders",
        responsibility_scope="payments-team",
        valid_from=START,
        valid_to=NOW,
        provenance_reference="provenance:affiliation:create",
        end_provenance_reference="provenance:affiliation:end",
        version=3,
    )
    ended_responsibility = ResourceResponsibility(
        assignment_reference="responsibility:orders",
        resource_reference="resource:orders",
        party_reference="team:orders",
        party_kind=ResponsiblePartyKind.TEAM,
        role=ResourceResponsibilityRole.TECHNICAL_OWNER,
        display_name="Orders Team",
        contact="orders@example.test",
        valid_from=START,
        valid_to=NOW,
        provenance_reference="provenance:responsibility:create",
        end_provenance_reference="provenance:responsibility:end",
        version=4,
    )
    replace_realization = Recorder(
        RealizationMutationResult(
            TemporalCurationOutcome.UPDATED,
            realization=replacement,
            replaced_fact_reference="realization:old",
            result_version=1,
        )
    )
    end_scope_affiliation = Recorder(
        ScopeAffiliationMutationResult(
            TemporalCurationOutcome.UPDATED,
            affiliation=ended_affiliation,
            result_version=ended_affiliation.version,
        )
    )
    end_responsibility = Recorder(
        ResponsibilityMutationResult(
            TemporalCurationOutcome.UPDATED,
            responsibility=ended_responsibility,
            result_version=ended_responsibility.version,
        )
    )
    resources = SimpleNamespace(
        replace_realization=replace_realization,
        end_scope_affiliation=end_scope_affiliation,
        end_responsibility=end_responsibility,
    )
    scope = SimpleNamespace(resources=resources)

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
        create_resource_catalogue_temporal_router(
            sessions=sessions,
            open_scope=open_scope,
            clock=lambda: NOW,
        )
    )
    return (
        TestClient(app),
        replace_realization,
        end_scope_affiliation,
        end_responsibility,
    )


def test_replace_realization_uses_selected_fact_version_and_server_context():
    client, recorder, _, _ = _client_for()

    response = client.post(
        "/api/v1/catalogues/resource-realizations/realization:old/replacement",
        json={
            "technicalAddresses": ["203.0.113.20"],
            "validFrom": NOW.isoformat(),
            "validTo": None,
            "expectedVersion": 2,
        },
        headers={"Idempotency-Key": "replace-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    assert response.json()["replacedFactReference"] == "realization:old"
    command = recorder.calls[0]
    assert command.current_fact_reference == "realization:old"
    assert command.technical_addresses == ("203.0.113.20",)
    assert command.expected_version == 2
    assert command.actor_id == "actor-1"
    assert command.effective_time == NOW
    assert command.idempotency_key == "replace-1"


def test_end_scope_affiliation_uses_relation_reference_version_and_server_context():
    client, _, recorder, _ = _client_for()

    response = client.post(
        "/api/v1/catalogues/resource-scope-affiliations/affiliation:orders/end",
        json={
            "validTo": NOW.isoformat(),
            "expectedVersion": 2,
        },
        headers={"Idempotency-Key": "affiliation-end-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    assert response.json()["scopeAffiliation"]["validTo"] == NOW.isoformat()
    command = recorder.calls[0]
    assert command.affiliation_reference == "affiliation:orders"
    assert command.expected_version == 2
    assert command.actor_id == "actor-1"
    assert command.effective_time == NOW
    assert command.idempotency_key == "affiliation-end-1"


def test_end_responsibility_uses_relation_reference_version_and_server_context():
    client, _, _, recorder = _client_for()

    response = client.post(
        "/api/v1/catalogues/resource-responsibilities/responsibility:orders/end",
        json={
            "validTo": NOW.isoformat(),
            "expectedVersion": 3,
        },
        headers={"Idempotency-Key": "responsibility-end-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    assert response.json()["responsibility"]["version"] == 4
    command = recorder.calls[0]
    assert command.assignment_reference == "responsibility:orders"
    assert command.expected_version == 3
    assert command.actor_id == "actor-1"
    assert command.effective_time == NOW
    assert command.idempotency_key == "responsibility-end-1"


def test_temporal_mutation_rejects_client_authority_scope_substitution():
    client, _, recorder, _ = _client_for()

    response = client.post(
        "/api/v1/catalogues/resource-scope-affiliations/affiliation:orders/end",
        json={
            "validTo": NOW.isoformat(),
            "expectedVersion": 2,
            "authorityScope": "attacker-controlled",
        },
        headers={"Idempotency-Key": "affiliation-end-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 422
    assert recorder.calls == []


def test_temporal_mutation_requires_authenticated_session():
    client, recorder, _, _ = _client_for()

    response = client.post(
        "/api/v1/catalogues/resource-realizations/realization:old/replacement",
        json={
            "technicalAddresses": ["203.0.113.20"],
            "validFrom": NOW.isoformat(),
            "validTo": None,
            "expectedVersion": 2,
        },
        headers={"Idempotency-Key": "replace-1"},
    )

    assert response.status_code == 401
    assert recorder.calls == []
