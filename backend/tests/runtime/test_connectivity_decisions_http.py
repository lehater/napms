from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from napms.access_policy.application.ports import (
    ConnectivityDecision as AccessPolicyConnectivityDecision,
    DecisionOutcome as AccessPolicyDecisionOutcome,
)
from napms.application_catalogue.application.describe_interactions import (
    DirectedInteractionDescription,
)
from napms.contexts.connectivity_decision.application.ports import (
    DecisionAuthorityCheck,
    DecisionInteractionPage,
    DecisionScopeOptions,
    DecisionSubjectCheck,
    SubjectOutcome,
    TernaryOutcome,
)
from napms.contexts.connectivity_decision.domain.model import DecisionSubject
from napms.runtime.auth import (
    InMemorySessionStore,
    LocalCredential,
    LocalPasswordAuthenticator,
    hash_local_password,
)
from napms.runtime.http_api import HttpApiDependencies, create_http_api


NOW = datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=201)
DESTINATION = UUID(int=202)
DCS = UUID(int=203)
SUBJECT = DecisionSubject(SOURCE, DESTINATION, DCS)


class FakeDecisionAuthority:
    def __init__(self, outcomes=None):
        self.outcomes = outcomes or {}
        self.calls = []

    def check(self, **kwargs):
        self.calls.append(kwargs)
        action = kwargs["action"].value
        outcome = self.outcomes.get(action, TernaryOutcome.PERMITTED)
        return DecisionAuthorityCheck(
            outcome=outcome,
            authority_reference=(
                f"{action}-authority"
                if outcome is TernaryOutcome.PERMITTED
                else None
            ),
        )


class FakeDecisionScopes:
    def list_effective_decision_scopes(self, **kwargs):
        return DecisionScopeOptions(
            permitted_scopes=("scope-a",),
            ambiguous_scopes=("scope-ambiguous",),
        )


class FakeDecisionReadScopes:
    def list_effective_decision_read_scopes(self, **kwargs):
        return DecisionScopeOptions(
            permitted_scopes=("scope-a",),
            ambiguous_scopes=(),
        )


class FakeDecisionCatalogue:
    def validate_decision_subject(self, **kwargs):
        return DecisionSubjectCheck(
            outcome=SubjectOutcome.VALID,
            subject=kwargs["subject"],
            provenance_reference="catalogue-decision-1",
        )


class FakeDecisionInteractions:
    def list_decision_subjects(self, *, page, page_size, search=None):
        return DecisionInteractionPage(
            subjects=(SUBJECT,),
            page=page,
            page_size=page_size,
            has_more=False,
        )


class MemoryDecisions:
    def __init__(self):
        self.by_id = {}
        self.pending = None

    def get_by_id(self, decision_id):
        return self.by_id.get(decision_id)

    def find_current(self, *, subject, governance_scope, as_of):
        values = [
            value
            for value in self.by_id.values()
            if value.subject == subject
            and value.governance_scope == governance_scope
            and value.is_effective_at(as_of)
            and not any(
                successor.supersedes_decision_id == value.decision_id
                for successor in self.by_id.values()
            )
        ]
        return tuple(values)

    def list_by_governance_scopes(self, scopes, *, offset, limit):
        values = [
            value
            for value in self.by_id.values()
            if value.governance_scope in scopes
        ]
        values.sort(key=lambda value: value.provenance.decided_at, reverse=True)
        return tuple(values[offset : offset + limit])

    def add(self, decision):
        self.pending = decision

    def commit(self):
        if self.pending is not None:
            self.by_id[self.pending.decision_id] = self.pending
            self.pending = None


class FakeDescriber:
    def execute(self, identities):
        return tuple(
            DirectedInteractionDescription(
                identity=identity,
                source_display_name="Demo Web Frontend",
                destination_display_name="Demo Orders API",
                dcs_display_name="HTTPS Orders API",
                dcs_projection_payload=None,
                dcs_provenance_reference="dcs-1",
            )
            for identity in identities
        )


class FakeDecoder:
    def decode(self, payload):
        raise AssertionError("decoder must not run without projection payload")


class FakeProposalDecisions:
    def obtain(self, *, subject, governance_scope, as_of):
        return AccessPolicyConnectivityDecision(
            outcome=AccessPolicyDecisionOutcome.UNKNOWN,
            subject=subject,
            governance_scope=governance_scope,
            valid_from=None,
        )


class Scope:
    def __init__(self, *, authority=None, decisions=None):
        self.decision_authority = authority or FakeDecisionAuthority()
        self.decision_scopes = FakeDecisionScopes()
        self.decision_read_scopes = FakeDecisionReadScopes()
        self.decision_catalogue = FakeDecisionCatalogue()
        self.decision_interaction_catalogue = FakeDecisionInteractions()
        self.connectivity_decisions = decisions or MemoryDecisions()
        self.catalogue_describer = FakeDescriber()
        self.dcs_decoder = FakeDecoder()


def build_client(*, authority=None, decisions=None):
    scope = Scope(authority=authority, decisions=decisions)
    credential = LocalCredential(
        login="alexey",
        actor_id="actor-1",
        password_hash=hash_local_password(
            "secret",
            salt=b"0123456789abcdef",
        ),
    )
    sessions = InMemorySessionStore(new_session_id=lambda: "opaque-session")

    @contextmanager
    def open_scope():
        yield scope

    app = create_http_api(
        HttpApiDependencies(
            authenticator=LocalPasswordAuthenticator(credential),
            sessions=sessions,
            open_scope=open_scope,
            decisions=FakeProposalDecisions(),
            readiness=lambda: True,
            clock=lambda: NOW,
        )
    )
    return TestClient(app), scope


def login(client):
    response = client.post(
        "/api/v1/session",
        json={"login": "alexey", "password": "secret"},
    )
    assert response.status_code == 200


def decision_payload(**changes):
    values = {
        "authorityScope": "scope-a",
        "sourceComponentDeploymentId": str(SOURCE),
        "destinationComponentDeploymentId": str(DESTINATION),
        "dcsContractRevisionId": str(DCS),
        "outcome": "Allowed",
        "validFrom": (NOW - timedelta(minutes=5)).isoformat(),
        "validUntil": (NOW + timedelta(hours=1)).isoformat(),
        "reasonCode": "security-reviewed",
        "reasonText": "Connectivity reviewed for the demo.",
        "evidenceReferences": [
            {"kind": "Requirement", "reference": "requirement-1"}
        ],
    }
    values.update(changes)
    return values


def test_decision_scopes_and_interactions_are_authority_bound():
    client, scope = build_client()
    login(client)

    scopes = client.get("/api/v1/connectivity-decisions/scopes")
    assert scopes.status_code == 200
    assert scopes.json() == {
        "scopes": [{"scope": "scope-a"}],
        "ambiguousScopes": [{"scope": "scope-ambiguous"}],
    }

    interactions = client.get(
        "/api/v1/connectivity-decisions/interactions",
        params={"scope": "scope-a"},
    )
    assert interactions.status_code == 200
    item = interactions.json()["items"][0]
    assert item["sourceComponentDeploymentId"] == str(SOURCE)
    assert item["catalogue"]["sourceDisplayName"] == "Demo Web Frontend"
    assert scope.decision_authority.calls[-1]["action"].value == "DecideConnectivity"
    assert scope.decision_authority.calls[-1]["effective_time"] == NOW


def test_record_list_and_detail_preserve_final_decision_and_server_provenance():
    client, scope = build_client()
    login(client)

    response = client.post(
        "/api/v1/connectivity-decisions",
        json=decision_payload(),
    )
    assert response.status_code == 201
    body = response.json()
    assert body["outcome"] == "Recorded"
    decision = body["decision"]
    assert decision["outcome"] == "Allowed"
    assert decision["governanceScope"] == "scope-a"
    assert decision["reason"] == {
        "code": "security-reviewed",
        "text": "Connectivity reviewed for the demo.",
    }
    assert decision["provenance"]["actorId"] == "actor-1"
    assert decision["provenance"]["decidedAt"] == NOW.isoformat()
    assert decision["provenance"]["authorityReference"] == "DecideConnectivity-authority"
    assert decision["catalogue"]["destinationDisplayName"] == "Demo Orders API"

    decision_id = decision["decisionId"]
    listed = client.get("/api/v1/connectivity-decisions")
    assert listed.status_code == 200
    assert [item["decisionId"] for item in listed.json()["items"]] == [decision_id]

    detail = client.get(f"/api/v1/connectivity-decisions/{decision_id}")
    assert detail.status_code == 200
    assert detail.json()["decision"]["decisionId"] == decision_id
    assert detail.json()["readAuthorityReference"] == "ReadConnectivityDecision-authority"
    assert scope.decision_authority.calls[-1]["action"].value == "ReadConnectivityDecision"


def test_not_allowed_is_recorded_as_business_outcome_not_http_error():
    client, _ = build_client()
    login(client)

    response = client.post(
        "/api/v1/connectivity-decisions",
        json=decision_payload(outcome="NotAllowed"),
    )

    assert response.status_code == 201
    assert response.json()["decision"]["outcome"] == "NotAllowed"


def test_decide_and_read_authority_are_independent():
    authority = FakeDecisionAuthority(
        {"DecideConnectivity": TernaryOutcome.DENIED}
    )
    client, _ = build_client(authority=authority)
    login(client)

    denied = client.post(
        "/api/v1/connectivity-decisions",
        json=decision_payload(),
    )
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "AuthorityDenied"

    authority.outcomes = {"ReadConnectivityDecision": TernaryOutcome.DENIED}
    decisions = MemoryDecisions()
    client, scope = build_client(authority=authority, decisions=decisions)
    login(client)
    authority.outcomes = {}
    recorded = client.post(
        "/api/v1/connectivity-decisions",
        json=decision_payload(),
    )
    assert recorded.status_code == 201
    decision_id = recorded.json()["decision"]["decisionId"]
    authority.outcomes = {"ReadConnectivityDecision": TernaryOutcome.DENIED}

    hidden = client.get(f"/api/v1/connectivity-decisions/{decision_id}")
    assert hidden.status_code == 403
    assert hidden.json()["error"]["code"] == "AuthorityDenied"


def test_invalid_validity_is_rejected_before_recording():
    client, scope = build_client()
    login(client)

    response = client.post(
        "/api/v1/connectivity-decisions",
        json=decision_payload(
            validFrom=(NOW + timedelta(hours=1)).isoformat(),
            validUntil=NOW.isoformat(),
        ),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "InvalidDecisionValidity"
    assert scope.connectivity_decisions.by_id == {}
