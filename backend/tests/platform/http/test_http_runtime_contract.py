import json
from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

import napms.platform.http.api as http_api_module
from napms.contexts.access_policy.application.ports import (
    AccessRuleCommitOutcomeUnknown,
    AccessRulePersistenceError,
    AuthorityCheck,
    ConnectivityDecision,
    DecisionOutcome,
    InteractionCheck,
    InteractionOutcome,
    TernaryOutcome,
)
from napms.contexts.access_policy.domain.model import RuleSemanticIdentity
from napms.contexts.application_catalogue.application.discovery.describe_interactions import (
    DirectedInteractionDescription,
)
from napms.workflows.policy_export.application.normalization_types import (
    DcsTrafficAlternative,
    PortConstraint,
    PortRange,
)
from napms.workflows.policy_export.application.ports import (
    ApplicationProjectionFact,
    ApplicationProjectionOutcome,
    EndpointRealization,
    ResourceRealizationFact,
    ResourceRealizationOutcome,
    ResourceReference,
)
from napms.platform.auth.local import (
    InMemorySessionStore,
    LocalCredential,
    LocalPasswordAuthenticator,
    hash_local_password,
)
from napms.platform.bootstrap.http_process import HttpApiDependencies, create_http_api


NOW = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=11)
DESTINATION = UUID(int=12)
DCS = UUID(int=13)
IDENTITY = RuleSemanticIdentity(SOURCE, DESTINATION, DCS)
WRONG_IDENTITY = RuleSemanticIdentity(UUID(int=21), UUID(int=22), UUID(int=23))


class FakeAuthority:
    def __init__(self, outcome=TernaryOutcome.PERMITTED):
        self.outcome = outcome

    def check(self, **kwargs):
        return AuthorityCheck(
            self.outcome,
            "authority-1" if self.outcome is TernaryOutcome.PERMITTED else None,
        )


class FakeProposalCatalogue:
    def __init__(self, outcome=InteractionOutcome.VALID):
        self.outcome = outcome

    def resolve_directed_interaction(self, *, identity, effective_time):
        return InteractionCheck(
            self.outcome,
            identity if self.outcome is InteractionOutcome.VALID else None,
            "catalogue-1" if self.outcome is InteractionOutcome.VALID else None,
        )


class FakeDecision:
    def __init__(
        self,
        outcome=DecisionOutcome.ALLOWED,
        subject_override=None,
        error=None,
    ):
        self.outcome = outcome
        self.subject_override = subject_override
        self.error = error

    def obtain(self, *, subject, governance_scope, as_of):
        if self.error is not None:
            raise self.error
        return ConnectivityDecision(
            outcome=self.outcome,
            subject=self.subject_override or subject,
            governance_scope=governance_scope,
            valid_from=as_of,
            decision_reference="decision-1",
        )


class FakeRules:
    def __init__(self, commit_error=None):
        self.rules = {}
        self.commit_error = commit_error

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
        if self.commit_error is not None:
            raise self.commit_error


class FakeCatalogueDescriber:
    def execute(self, identities):
        return tuple(
            DirectedInteractionDescription(
                identity=identity,
                source_display_name=None,
                destination_display_name=None,
                dcs_display_name=None,
                dcs_projection_payload=None,
                dcs_provenance_reference=None,
            )
            for identity in identities
        )


class FakeApplicationProjection:
    def __init__(self, mode="resolved"):
        self.mode = mode

    def resolve_projection(self, *, subject, as_of):
        if self.mode == "missing":
            return ApplicationProjectionFact(ApplicationProjectionOutcome.MISSING)
        projection_subject = WRONG_IDENTITY if self.mode == "mismatch" else subject
        return ApplicationProjectionFact(
            outcome=ApplicationProjectionOutcome.RESOLVED,
            subject=projection_subject,
            as_of=as_of,
            source_resource_references=(ResourceReference("src-resource"),),
            destination_resource_references=(ResourceReference("dst-resource"),),
            dcs_projection_payload=b"dcs",
            fact_reference="acc-fact",
            validity_reference="acc-validity",
            provenance_reference="acc-provenance",
        )


class FakeResourceProjection:
    def __init__(self, mode="resolved"):
        self.mode = mode

    def resolve_realization(self, *, resource_reference, as_of):
        if self.mode == "stale":
            return ResourceRealizationFact(
                outcome=ResourceRealizationOutcome.STALE,
                resource_reference=resource_reference,
                as_of=as_of,
            )
        resolved_reference = (
            ResourceReference("wrong-resource")
            if self.mode == "mismatch"
            else resource_reference
        )
        return ResourceRealizationFact(
            outcome=ResourceRealizationOutcome.RESOLVED,
            resource_reference=resolved_reference,
            as_of=as_of,
            endpoint_realizations=(
                EndpointRealization(
                    endpoint_reference=f"{resource_reference.value}-endpoint",
                    technical_address=(
                        "198.51.100.10"
                        if resource_reference.value == "src-resource"
                        else "203.0.113.20"
                    ),
                ),
            ),
            fact_reference=f"{resource_reference.value}-fact",
            validity_reference=f"{resource_reference.value}-validity",
            provenance_reference=f"{resource_reference.value}-provenance",
        )


class FakeDecoder:
    def decode(self, payload):
        assert payload == b"dcs"
        return (
            DcsTrafficAlternative(
                protocol="tcp",
                source_ports=PortConstraint.any(),
                destination_ports=PortConstraint.ranged(PortRange(443, 443)),
                service_reference="https",
            ),
        )


class Scope:
    def __init__(
        self,
        *,
        authority,
        interaction=InteractionOutcome.VALID,
        commit_error=None,
        application_mode="resolved",
        resource_mode="resolved",
    ):
        self.authority = authority
        self.proposal_catalogue = FakeProposalCatalogue(interaction)
        self.access_rules = FakeRules(commit_error)
        self.catalogue_describer = FakeCatalogueDescriber()
        self.application_projection = FakeApplicationProjection(application_mode)
        self.resource_projection = FakeResourceProjection(resource_mode)
        self.dcs_decoder = FakeDecoder()


def build_client(
    *,
    authority=TernaryOutcome.PERMITTED,
    interaction=InteractionOutcome.VALID,
    decision=DecisionOutcome.ALLOWED,
    decision_subject_override=None,
    decision_error=None,
    commit_error=None,
    application_mode="resolved",
    resource_mode="resolved",
    readiness=True,
):
    scope = Scope(
        authority=FakeAuthority(authority),
        interaction=interaction,
        commit_error=commit_error,
        application_mode=application_mode,
        resource_mode=resource_mode,
    )
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
            decisions=FakeDecision(
                decision,
                decision_subject_override,
                decision_error,
            ),
            readiness=lambda: readiness,
            clock=lambda: NOW,
        )
    )
    return TestClient(app)


def login(client):
    response = client.post(
        "/api/v1/session",
        json={"login": "alexey", "password": "secret"},
    )
    assert response.status_code == 200


def proposal_payload():
    return {
        "authorityScope": "scope-a",
        "sourceComponentDeploymentId": str(SOURCE),
        "destinationComponentDeploymentId": str(DESTINATION),
        "dcsContractRevisionId": str(DCS),
    }


@pytest.mark.parametrize(
    (
        "kwargs",
        "expected_status",
        "expected_code",
    ),
    (
        ({"authority": TernaryOutcome.DENIED}, 403, "AuthorityDenied"),
        ({"authority": TernaryOutcome.UNKNOWN}, 409, "AuthorityUnknown"),
        ({"interaction": InteractionOutcome.INVALID}, 422, "InteractionInvalid"),
        ({"interaction": InteractionOutcome.UNKNOWN}, 409, "InteractionUnknown"),
        ({"decision": DecisionOutcome.UNKNOWN}, 503, "DecisionUnknown"),
        (
            {"decision_subject_override": WRONG_IDENTITY},
            502,
            "DecisionSubjectMismatch",
        ),
        (
            {"commit_error": AccessRulePersistenceError()},
            503,
            "PersistenceUnavailable",
        ),
        (
            {"commit_error": AccessRuleCommitOutcomeUnknown()},
            503,
            "PersistenceOutcomeUnknown",
        ),
    ),
)
def test_proposal_failure_mappings_are_stable_and_safe(
    kwargs,
    expected_status,
    expected_code,
):
    client = build_client(**kwargs)
    login(client)

    response = client.post(
        "/api/v1/access-rule-proposals",
        json=proposal_payload(),
    )

    assert response.status_code == expected_status
    assert response.json()["error"]["code"] == expected_code
    assert "Traceback" not in response.text
    assert "psycopg" not in response.text.lower()


def test_normalized_policy_positive_path_preserves_non_empty_row():
    client = build_client()
    login(client)
    assert client.post(
        "/api/v1/access-rule-proposals",
        json=proposal_payload(),
    ).status_code == 201

    response = client.get(
        "/api/v1/normalized-policy",
        params={"scope": "scope-a", "asOf": NOW.isoformat()},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["scope"] == "scope-a"
    assert payload["authorityReference"] == "authority-1"
    assert len(payload["rows"]) == 1
    row = payload["rows"][0]
    assert row["decisionReference"] == "decision-1"
    assert row["source"]["technicalAddress"] == "198.51.100.10"
    assert row["destination"]["technicalAddress"] == "203.0.113.20"
    assert row["traffic"]["sourcePorts"] == {"kind": "Any"}
    assert row["traffic"]["destinationPorts"] == {
        "kind": "Ranges",
        "ranges": [{"first": 443, "last": 443}],
    }


@pytest.mark.parametrize(
    ("resource_mode", "expected_category"),
    (
        ("stale", "Stale"),
        ("mismatch", "CorrelationMismatch"),
    ),
)
def test_normalized_policy_snapshot_failures_return_no_partial_rows(
    resource_mode,
    expected_category,
):
    client = build_client(resource_mode=resource_mode)
    login(client)
    assert client.post(
        "/api/v1/access-rule-proposals",
        json=proposal_payload(),
    ).status_code == 201

    response = client.get(
        "/api/v1/normalized-policy",
        params={"scope": "scope-a", "asOf": NOW.isoformat()},
    )

    assert response.status_code == 409
    error = response.json()["error"]
    assert error["code"] == "SnapshotIncomplete"
    assert error["details"]["diagnostics"][0]["category"] == expected_category
    assert "rows" not in response.json()


def test_application_projection_correlation_mismatch_is_reported():
    client = build_client(application_mode="mismatch")
    login(client)
    assert client.post(
        "/api/v1/access-rule-proposals",
        json=proposal_payload(),
    ).status_code == 201

    response = client.get(
        "/api/v1/normalized-policy",
        params={"scope": "scope-a", "asOf": NOW.isoformat()},
    )

    assert response.status_code == 409
    diagnostics = response.json()["error"]["details"]["diagnostics"]
    assert diagnostics[0]["source"] == "ApplicationCommunicationCatalogue"
    assert diagnostics[0]["category"] == "CorrelationMismatch"


def test_unknown_route_uses_safe_correlated_not_found_envelope():
    client = build_client()

    response = client.get(
        "/api/v1/not-a-route",
        headers={"X-Correlation-ID": "request-not-found"},
    )

    assert response.status_code == 404
    assert response.headers["X-Correlation-ID"] == "request-not-found"
    assert response.json()["error"] == {
        "code": "NotFound",
        "message": "The requested resource was not found.",
        "correlationId": "request-not-found",
    }


def test_invalid_correlation_header_is_replaced_not_reflected():
    client = build_client()

    response = client.get(
        "/health/live",
        headers={"X-Correlation-ID": "invalid correlation with spaces"},
    )

    assert response.status_code == 200
    correlation_id = response.headers["X-Correlation-ID"]
    assert correlation_id != "invalid correlation with spaces"
    UUID(correlation_id)


def test_readiness_failure_is_explicit_and_dependency_safe():
    client = build_client(readiness=False)

    response = client.get("/health/ready")

    assert response.status_code == 503
    assert response.json() == {"status": "not-ready"}
    assert "postgresql://" not in response.text


def test_completion_event_contains_semantic_and_safe_references(monkeypatch):
    events = []

    def capture(level, message, exc_info=None):
        events.append((level, json.loads(message), exc_info))

    monkeypatch.setattr(http_api_module._LOGGER, "log", capture)

    client = build_client()
    login(client)
    response = client.post(
        "/api/v1/access-rule-proposals",
        json=proposal_payload(),
        headers={"X-Correlation-ID": "request-telemetry"},
    )
    assert response.status_code == 201

    _, event, exc_info = events[-1]
    assert event["event"] == "operation_completed"
    assert event["operation"] == "SubmitAccessRuleProposal"
    assert event["correlationId"] == "request-telemetry"
    assert event["outcome"] == "Materialized"
    assert event["actorId"] == "actor-1"
    assert event["ruleId"] == response.json()["rule"]["ruleId"]
    assert event["authorityReference"] == "authority-1"
    assert event["decisionReference"] == "decision-1"
    assert event["durationMs"] >= 0
    assert exc_info is None
    assert "secret" not in json.dumps(event)


def test_degraded_completion_event_names_dependency(monkeypatch):
    events = []

    def capture(level, message, exc_info=None):
        events.append(json.loads(message))

    monkeypatch.setattr(http_api_module._LOGGER, "log", capture)

    client = build_client(decision=DecisionOutcome.UNKNOWN)
    login(client)
    response = client.post(
        "/api/v1/access-rule-proposals",
        json=proposal_payload(),
    )

    assert response.status_code == 503
    assert events[-1]["outcome"] == "DecisionUnknown"
    assert events[-1]["dependency"] == "ConnectivityDecision"



def test_unexpected_exception_is_generic_publicly_and_structured_internally(monkeypatch):
    events = []

    def capture(level, message):
        events.append(json.loads(message))

    monkeypatch.setattr(http_api_module._LOGGER, "log", capture)

    client = build_client(
        decision_error=RuntimeError("postgresql://user:secret@internal/db")
    )
    login(client)
    response = client.post(
        "/api/v1/access-rule-proposals",
        json=proposal_payload(),
        headers={"X-Correlation-ID": "request-exception"},
    )

    assert response.status_code == 500
    assert response.json()["error"]["code"] == "InternalError"
    assert "secret" not in response.text
    assert "postgresql://" not in response.text

    event = events[-1]
    assert event["outcome"] == "InternalError"
    assert event["exception"]["class"] == "RuntimeError"
    serialized = json.dumps(event)
    assert "secret" not in serialized
    assert "postgresql://" not in serialized
