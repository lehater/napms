from contextlib import contextmanager
from datetime import datetime, timezone
from types import SimpleNamespace
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from napms.workflows.network_operator_view.presentation.http.routes import create_network_operator_view_router
from napms.workflows.network_operator_view.application.read import (
    Availability,
    NetworkOperatorRealizationView,
    ReadNetworkOperatorRealizationResult,
    ReadOutcome,
    Stage,
)
from napms.runtime.auth import AuthenticatedActor, InMemorySessionStore

NOW = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)


class Reader:
    def __init__(self, result):
        self.result = result

    def execute(self, **_):
        return self.result


def app_for(result):
    sessions = InMemorySessionStore(new_session_id=lambda: "session-1")
    sessions.create(AuthenticatedActor(actor_id="actor-1", login="operator"))

    @contextmanager
    def open_scope(_actor_id):
        yield SimpleNamespace(read=Reader(result))

    app = FastAPI()
    app.include_router(
        create_network_operator_view_router(sessions=sessions, open_scope=open_scope)
    )
    return TestClient(app)


def test_http_projection_keeps_missing_reconciliation_and_operation_explicit():
    target = SimpleNamespace(
        logical_firewall_id=UUID(int=1),
        enforcement_attachment_id=UUID(int=2),
    )
    desired = SimpleNamespace(
        status=SimpleNamespace(value="Derived"),
        intents=(
            SimpleNamespace(
                target=target,
                rule_references=("access-rule:1",),
                placement_provenance_references=("placement:1",),
            ),
        ),
    )
    rendered = SimpleNamespace(
        status=SimpleNamespace(value="Rendered"),
        target=target,
        renderer_name="cisco-asa-acl",
        renderer_contract_version="1",
        content="permit tcp host 10.0.0.1 host 10.0.0.2 eq 443",
        reason=None,
    )
    result = ReadNetworkOperatorRealizationResult(
        ReadOutcome.AVAILABLE,
        NetworkOperatorRealizationView(
            scope="scope-1",
            as_of=NOW,
            authority_reference="authority-1",
            desired=Stage(Availability.AVAILABLE, desired),
            reconciliation=Stage(
                Availability.NOT_AVAILABLE,
                reason="ConfiguredInputNotSelected",
            ),
            rendering=Stage(Availability.AVAILABLE, (rendered,)),
            operation=Stage(
                Availability.NOT_AVAILABLE,
                reason="OperationEvidenceNotSelected",
            ),
        ),
    )
    client = app_for(result)

    response = client.get(
        "/api/v1/network-operator-realization",
        params={"scope": "scope-1", "asOf": NOW.isoformat()},
        cookies={"napms_session": "session-1"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["desired"]["availability"] == "Available"
    assert body["desired"]["ruleReferences"] == ["access-rule:1"]
    assert body["reconciliation"] == {
        "availability": "NotAvailable",
        "status": None,
        "requiredChange": None,
        "reason": "ConfiguredInputNotSelected",
    }
    assert body["rendering"]["availability"] == "Available"
    assert body["operation"]["availability"] == "NotAvailable"
    assert body["operation"]["outcome"] is None


def test_http_requires_session():
    result = ReadNetworkOperatorRealizationResult(ReadOutcome.AUTHORITY_DENIED)
    client = app_for(result)

    response = client.get(
        "/api/v1/network-operator-realization",
        params={"scope": "scope-1", "asOf": NOW.isoformat()},
    )

    assert response.status_code == 401
