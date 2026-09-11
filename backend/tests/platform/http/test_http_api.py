from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from napms.contexts.access_policy.application.ports import (
    AuthorityCheck,
    ConnectivityDecision,
    DecisionOutcome,
    InteractionCheck,
    InteractionOutcome,
    ProposalInteractionPage,
    ProposalScopeOptions,
    TernaryOutcome,
)
from napms.contexts.application_catalogue.application.describe_interactions import (
    DirectedInteractionDescription,
)
from napms.contexts.application_catalogue.application.ports import CataloguePersistenceError
from napms.workflows.policy_export.application.ports import (
    ApplicationProjectionFact,
    ApplicationProjectionOutcome,
)
from napms.platform.auth.local import (
    InMemorySessionStore,
    LocalCredential,
    LocalPasswordAuthenticator,
    hash_local_password,
)
from napms.platform.http.api import HttpApiDependencies, create_http_api


NOW = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=1)
DESTINATION = UUID(int=2)
DCS = UUID(int=3)


class FakeAuthority:
    def __init__(self, outcome=TernaryOutcome.PERMITTED):
        self.outcome = outcome
        self.calls = []

    def check(self, **kwargs):
        self.calls.append(kwargs)
        return AuthorityCheck(
            self.outcome,
            "authority-1" if self.outcome is TernaryOutcome.PERMITTED else None,
        )


class FakeScopeDiscovery:
    def list_effective_proposal_scopes(self, **kwargs):
        return ProposalScopeOptions(("scope-a",), ("scope-ambiguous",))


class FakeInteractionCatalogue:
    def list_directed_interactions(self, *, page, page_size, search=None):
        return ProposalInteractionPage(
            identities=(
                _identity(),
            ),
            page=page,
            page_size=page_size,
            has_more=False,
        )


class FakeCatalogueDescriber:
    def __init__(self, *, fail=False):
        self.fail = fail

    def execute(self, identities):
        if self.fail:
            raise CataloguePersistenceError()
        return tuple(
            DirectedInteractionDescription(
                identity=identity,
                source_display_name="Checkout Web",
                destination_display_name="Orders API",
                dcs_display_name="HTTPS Orders",
                dcs_projection_payload=None,
                dcs_provenance_reference="dcs-1",
            )
            for identity in identities
        )


class FakeProposalCatalogue:
    def resolve_directed_interaction(self, *, identity, effective_time):
        return InteractionCheck(
            InteractionOutcome.VALID,
            identity,
            "catalogue-1",
        )


class FakeApplicationProjection:
    def resolve_projection(self, *, subject, as_of):
        return ApplicationProjectionFact(ApplicationProjectionOutcome.MISSING)


class FakeResourceProjection:
    def resolve_realization(self, **kwargs):
        raise AssertionError("resource projection must not run after missing ACC projection")


class FakeDecoder:
    def decode(self, payload):
        raise AssertionError("decoder must not run without successful snapshot")


class FakeRules:
    def __init__(self):
        self.rules = {}

    def find_by_identity(self, identity):
        return self.rules.get(identity)

    def get_by_id(self, rule_id):
        return next(
            (rule for rule in self.rules.values() if rule.rule_id == rule_id),
            None,
        )

    def list_by_governance_scope(self, scope):
        return tuple(
            rule for rule in self.rules.values() if rule.governance_scope == scope
        )

    def add(self, rule):
        self.rules[rule.semantic_identity] = rule

    def save(self, rule):
        self.rules[rule.semantic_identity] = rule

    def commit(self):
        return None


class FakeDecisions:
    def __init__(self, outcome=DecisionOutcome.ALLOWED):
        self.outcome = outcome
        self.calls = []

    def obtain(self, *, subject, governance_scope, as_of):
        self.calls.append(subject)
        return ConnectivityDecision(
            outcome=self.outcome,
            subject=subject,
            governance_scope=governance_scope,
            valid_from=as_of,
            decision_reference="decision-1",
        )


class Scope:
    def __init__(self, authority, catalogue_describer=None):
        self.authority = authority
        self.proposal_scope_discovery = FakeScopeDiscovery()
        self.proposal_interaction_catalogue = FakeInteractionCatalogue()
        self.catalogue_describer = catalogue_describer or FakeCatalogueDescriber()
        self.proposal_catalogue = FakeProposalCatalogue()
        self.access_rules = FakeRules()
        self.application_projection = FakeApplicationProjection()
        self.resource_projection = FakeResourceProjection()
        self.dcs_decoder = FakeDecoder()


def _identity():
    from napms.contexts.access_policy.domain.model import RuleSemanticIdentity

    return RuleSemanticIdentity(SOURCE, DESTINATION, DCS)


def _client(
    *,
    decision=DecisionOutcome.ALLOWED,
    authority=TernaryOutcome.PERMITTED,
    catalogue_describer=None,
):
    auth_port = FakeAuthority(authority)
    scope = Scope(auth_port, catalogue_describer=catalogue_describer)
    decisions = FakeDecisions(decision)
    sessions = InMemorySessionStore(new_session_id=lambda: "opaque-session")
    credential = LocalCredential(
        login="alexey",
        actor_id="actor-1",
        password_hash=hash_local_password(
            "secret",
            salt=b"0123456789abcdef",
        ),
    )

    @contextmanager
    def open_scope():
        yield scope

    app = create_http_api(
        HttpApiDependencies(
            authenticator=LocalPasswordAuthenticator(credential),
            sessions=sessions,
            open_scope=open_scope,
            decisions=decisions,
            readiness=lambda: True,
            clock=lambda: NOW,
        )
    )
    return TestClient(app), auth_port, decisions


def _login(client):
    response = client.post(
        "/api/v1/session",
        json={"login": "alexey", "password": "secret"},
    )
    assert response.status_code == 200
    return response


def _proposal_payload():
    return {
        "authorityScope": "scope-a",
        "sourceComponentDeploymentId": str(SOURCE),
        "destinationComponentDeploymentId": str(DESTINATION),
        "dcsContractRevisionId": str(DCS),
    }


def test_login_creates_opaque_server_side_session_and_bootstrap_uses_it():
    client, _, _ = _client()

    login = _login(client)
    assert login.json()["actor"] == {
        "actorId": "actor-1",
        "login": "alexey",
    }
    assert "napms_session=opaque-session" in login.headers["set-cookie"]
    assert "HttpOnly" in login.headers["set-cookie"]

    bootstrap = client.get("/api/v1/session")
    assert bootstrap.status_code == 200
    assert bootstrap.json()["actor"]["actorId"] == "actor-1"


def test_failed_login_is_generic():
    client, _, _ = _client()

    response = client.post(
        "/api/v1/session",
        json={"login": "unknown", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AuthenticationFailed"
    assert "unknown" not in response.text


def test_proposal_rejects_payload_actor_spoofing_before_business_execution():
    client, authority, decisions = _client()
    _login(client)
    payload = _proposal_payload()
    payload["actorId"] = "attacker"

    response = client.post("/api/v1/access-rule-proposals", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ValidationError"
    assert authority.calls == []
    assert decisions.calls == []


def test_proposal_uses_authenticated_actor_and_runtime_time():
    client, authority, decisions = _client()
    _login(client)

    response = client.post(
        "/api/v1/access-rule-proposals",
        json=_proposal_payload(),
        headers={"X-Correlation-ID": "request-123"},
    )

    assert response.status_code == 201
    assert response.headers["X-Correlation-ID"] == "request-123"
    assert response.json()["outcome"] == "Materialized"
    assert response.json()["rule"]["operationalState"] == "Active"
    assert authority.calls[0]["actor_id"] == "actor-1"
    assert authority.calls[0]["effective_time"] == NOW
    assert decisions.calls == [_identity()]


def test_not_allowed_is_normal_business_result_not_forbidden():
    client, _, _ = _client(decision=DecisionOutcome.NOT_ALLOWED)
    _login(client)

    response = client.post(
        "/api/v1/access-rule-proposals",
        json=_proposal_payload(),
    )

    assert response.status_code == 200
    assert response.json() == {"outcome": "NotAllowed", "rule": None}


def test_unauthenticated_proposal_fails_before_authority_or_decision():
    client, authority, decisions = _client()

    response = client.post(
        "/api/v1/access-rule-proposals",
        json=_proposal_payload(),
    )

    assert response.status_code == 401
    assert response.json()["error"]["code"] == "AuthenticationRequired"
    assert authority.calls == []
    assert decisions.calls == []


def test_scope_and_interaction_discovery_are_session_and_authority_aware():
    client, authority, _ = _client()
    _login(client)

    scopes = client.get("/api/v1/access-rule-proposals/scopes")
    assert scopes.status_code == 200
    assert scopes.json() == {
        "scopes": [{"scope": "scope-a"}],
        "ambiguousScopes": [{"scope": "scope-ambiguous"}],
    }

    interactions = client.get(
        "/api/v1/access-rule-proposals/interactions",
        params={"scope": "scope-a"},
    )
    assert interactions.status_code == 200
    assert interactions.json()["items"][0] == {
        "sourceComponentDeploymentId": str(SOURCE),
        "destinationComponentDeploymentId": str(DESTINATION),
        "dcsContractRevisionId": str(DCS),
        "catalogue": {
            "sourceDisplayName": "Checkout Web",
            "destinationDisplayName": "Orders API",
            "dcsDisplayName": "HTTPS Orders",
            "trafficAlternatives": [],
            "dcsProvenanceReference": "dcs-1",
        },
    }
    assert authority.calls[-1]["actor_id"] == "actor-1"


def test_authority_denied_does_not_return_interaction_catalogue_data():
    client, _, _ = _client(authority=TernaryOutcome.DENIED)
    _login(client)

    response = client.get(
        "/api/v1/access-rule-proposals/interactions",
        params={"scope": "scope-a"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AuthorityDenied"


def test_logout_invalidates_session():
    client, _, _ = _client()
    _login(client)

    logout = client.delete("/api/v1/session")
    assert logout.status_code == 204

    bootstrap = client.get("/api/v1/session")
    assert bootstrap.status_code == 401


def test_health_endpoints_are_explicit():
    client, _, _ = _client()

    assert client.get("/health/live").json() == {"status": "alive"}
    assert client.get("/health/ready").json() == {"status": "ready"}



def test_normalized_policy_empty_export_preserves_scope_as_of_and_authority():
    client, _, _ = _client()
    _login(client)

    response = client.get(
        "/api/v1/normalized-policy",
        params={"scope": "scope-a", "asOf": NOW.isoformat()},
    )

    assert response.status_code == 200
    assert response.json() == {
        "scope": "scope-a",
        "asOf": NOW.isoformat(),
        "authorityReference": "authority-1",
        "rows": [],
    }


def test_normalized_policy_fails_closed_on_read_authority_denial():
    client, _, _ = _client(authority=TernaryOutcome.DENIED)
    _login(client)

    response = client.get(
        "/api/v1/normalized-policy",
        params={"scope": "scope-a", "asOf": NOW.isoformat()},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AuthorityDenied"


def test_normalized_policy_rejects_naive_as_of():
    client, _, _ = _client()
    _login(client)

    response = client.get(
        "/api/v1/normalized-policy",
        params={"scope": "scope-a", "asOf": "2026-09-08T12:00:00"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "InvalidAsOf"


def test_normalized_policy_reports_snapshot_diagnostics_without_partial_rows():
    client, _, _ = _client()
    _login(client)
    submitted = client.post(
        "/api/v1/access-rule-proposals",
        json=_proposal_payload(),
    )
    assert submitted.status_code == 201

    response = client.get(
        "/api/v1/normalized-policy",
        params={"scope": "scope-a", "asOf": NOW.isoformat()},
    )

    assert response.status_code == 409
    error = response.json()["error"]
    assert error["code"] == "SnapshotIncomplete"
    assert error["details"]["diagnostics"][0]["source"] == (
        "ApplicationCommunicationCatalogue"
    )
    assert error["details"]["diagnostics"][0]["category"] == "Missing"
    assert "rows" not in response.json()



def test_optional_catalogue_presentation_failure_does_not_change_proposal_outcome():
    client, _, _ = _client(
        catalogue_describer=FakeCatalogueDescriber(fail=True)
    )
    _login(client)

    interactions = client.get(
        "/api/v1/access-rule-proposals/interactions",
        params={"scope": "scope-a"},
    )
    submitted = client.post(
        "/api/v1/access-rule-proposals",
        json=_proposal_payload(),
    )

    assert interactions.status_code == 200
    assert interactions.json()["items"][0]["catalogue"] is None
    assert submitted.status_code == 201
    assert submitted.json()["outcome"] == "Materialized"
    assert submitted.json()["rule"]["catalogue"] is None
