from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from napms.contexts.resource_catalogue.application._temporal_curation import (
    TemporalCurationOutcome,
)
from napms.contexts.resource_catalogue.presentation.http.curation import (
    create_resource_catalogue_curation_router,
)
from napms.contexts.resource_catalogue.application.responsibility_curation import (
    ResponsibilityMutationResult,
)
from napms.contexts.resource_catalogue.application.scope_affiliation_curation import (
    ScopeAffiliationMutationResult,
)
from napms.contexts.resource_catalogue.domain.model import ResourceScopeAffiliation
from napms.contexts.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibility,
    ResourceResponsibilityRole,
)
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore
from napms.runtime.http_api import PublicApiError


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
VALID_FROM = datetime(2026, 9, 10, 10, 0, tzinfo=timezone.utc)
RESOURCE = "resource:test:orders"


class Recorder:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, command=None, **kwargs):
        self.calls.append(command if command is not None else kwargs)
        return self.result


def _client(*, affiliation_outcome=TemporalCurationOutcome.CREATED):
    sessions = InMemorySessionStore(new_session_id=lambda: "session-1")
    sessions.create(AuthenticatedActor(actor_id="actor-1", login="local-admin"))

    affiliation = ResourceScopeAffiliation(
        affiliation_reference="affiliation-1",
        resource_reference=RESOURCE,
        responsibility_scope="payments-team",
        valid_from=VALID_FROM,
        valid_to=None,
        provenance_reference="prov:affiliation",
    )
    responsibility = ResourceResponsibility(
        assignment_reference="responsibility-1",
        resource_reference=RESOURCE,
        party_reference="team:orders",
        party_kind=ResponsiblePartyKind.TEAM,
        role=ResourceResponsibilityRole.TECHNICAL_OWNER,
        display_name="Orders Team",
        contact="orders@example.test",
        valid_from=VALID_FROM,
        valid_to=None,
        provenance_reference="prov:responsibility",
    )

    create_affiliation = Recorder(
        ScopeAffiliationMutationResult(
            affiliation_outcome,
            affiliation=affiliation if affiliation_outcome is TemporalCurationOutcome.CREATED else None,
            result_version=1 if affiliation_outcome is TemporalCurationOutcome.CREATED else None,
        )
    )
    create_responsibility = Recorder(
        ResponsibilityMutationResult(
            TemporalCurationOutcome.CREATED,
            responsibility=responsibility,
            result_version=1,
        )
    )
    resources = SimpleNamespace(
        create_scope_affiliation=create_affiliation,
        create_responsibility=create_responsibility,
    )
    scope = SimpleNamespace(applications=SimpleNamespace(), resources=resources)

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
        create_resource_catalogue_curation_router(
            sessions=sessions,
            open_scope=open_scope,
            clock=lambda: NOW,
        )
    )
    return TestClient(app), create_affiliation, create_responsibility


def test_scope_affiliation_treats_external_scope_as_business_data():
    client, recorder, _ = _client()

    response = client.post(
        f"/api/v1/catalogues/resources/{RESOURCE}/scope-affiliations",
        json={
            "responsibilityScope": "payments-team",
            "validFrom": VALID_FROM.isoformat(),
            "validTo": None,
        },
        headers={"Idempotency-Key": "affiliation-request-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 201
    assert response.json()["scopeAffiliation"]["responsibilityScope"] == "payments-team"
    command = recorder.calls[0]
    assert command.resource_reference == RESOURCE
    assert command.responsibility_scope == "payments-team"
    assert command.actor_id == "actor-1"
    assert command.effective_time == NOW
    assert command.idempotency_key == "affiliation-request-1"


def test_scope_affiliation_rejects_client_authority_scope_substitution():
    client, recorder, _ = _client()

    response = client.post(
        f"/api/v1/catalogues/resources/{RESOURCE}/scope-affiliations",
        json={
            "responsibilityScope": "payments-team",
            "validFrom": VALID_FROM.isoformat(),
            "validTo": None,
            "authorityScope": "payments-team",
        },
        headers={"Idempotency-Key": "affiliation-request-2"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 422
    assert recorder.calls == []


def test_resource_responsibility_treats_party_reference_as_external_correlation():
    client, _, recorder = _client()

    response = client.post(
        f"/api/v1/catalogues/resources/{RESOURCE}/responsibilities",
        json={
            "partyReference": "team:orders",
            "partyKind": "Team",
            "role": "TechnicalOwner",
            "displayName": "Orders Team",
            "contact": "orders@example.test",
            "validFrom": VALID_FROM.isoformat(),
            "validTo": None,
        },
        headers={"Idempotency-Key": "responsibility-request-1"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 201
    body = response.json()["responsibility"]
    assert body["partyReference"] == "team:orders"
    assert body["partyKind"] == "Team"
    assert body["role"] == "TechnicalOwner"
    command = recorder.calls[0]
    assert command.party_reference == "team:orders"
    assert command.party_kind is ResponsiblePartyKind.TEAM
    assert command.role is ResourceResponsibilityRole.TECHNICAL_OWNER
    assert command.actor_id == "actor-1"
    assert command.effective_time == NOW
    assert command.idempotency_key == "responsibility-request-1"


def test_resource_relation_authority_denial_maps_to_forbidden():
    client, recorder, _ = _client(
        affiliation_outcome=TemporalCurationOutcome.AUTHORITY_DENIED,
    )

    response = client.post(
        f"/api/v1/catalogues/resources/{RESOURCE}/scope-affiliations",
        json={
            "responsibilityScope": "payments-team",
            "validFrom": VALID_FROM.isoformat(),
            "validTo": None,
        },
        headers={"Idempotency-Key": "affiliation-request-denied"},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "CatalogueAuthorityDenied"
    assert len(recorder.calls) == 1
