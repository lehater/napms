from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from napms.contexts.access_policy.application.ports import (
    ConnectivityDecision,
    DecisionOutcome,
)
from napms.contexts.application_catalogue.application.describe_interactions import (
    DirectedInteractionDescription,
)
from napms.contexts.connectivity_requirements.infrastructure.integrations.requirement_policy_alignment import (
    ConnectivityRequirementsAlignmentAdapter,
)
from napms.contexts.connectivity_requirements.application.ports import (
    InteractionOutcome,
    RequirementAuthorityCheck,
    RequirementInteractionCheck,
    RequirementInteractionPage,
    RequirementScopeOptions,
    TernaryOutcome,
)
from napms.contexts.connectivity_requirements.application.read import (
    GetAuthorizedRequirement,
    ListConnectivityRequirements,
)
from napms.contexts.connectivity_requirements.domain.model import (
    RequiredSemanticInteraction,
    RequirementLifecycleState,
)
from napms.workflows.requirement_policy_alignment.application.ports import (
    PolicyCoverageOutcome,
)
from napms.platform.auth.local import (
    InMemorySessionStore,
    LocalCredential,
    LocalPasswordAuthenticator,
    hash_local_password,
)
from napms.platform.bootstrap.http_process import HttpApiDependencies, create_http_api


NOW = datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=101)
DESTINATION = UUID(int=102)
DCS = UUID(int=103)
INTERACTION = RequiredSemanticInteraction(SOURCE, DESTINATION, DCS)


class FakeAuthority:
    def __init__(self, outcomes=None):
        self.outcomes = outcomes or {}
        self.calls = []

    def check(self, **kwargs):
        self.calls.append(kwargs)
        action = kwargs["action"].value
        outcome = self.outcomes.get(action, TernaryOutcome.PERMITTED)
        return RequirementAuthorityCheck(
            outcome,
            f"{action}-authority"
            if outcome is TernaryOutcome.PERMITTED
            else None,
        )


class FakeDeclarationScopes:
    def list_effective_declaration_scopes(self, **kwargs):
        return RequirementScopeOptions(
            permitted_scopes=("scope-a",),
            ambiguous_scopes=("scope-b",),
        )


class FakeReadScopes:
    def list_effective_read_scopes(self, **kwargs):
        return RequirementScopeOptions(
            permitted_scopes=("scope-a",),
            ambiguous_scopes=("scope-b",),
        )


class FakeCatalogue:
    def __init__(self, outcome=InteractionOutcome.VALID):
        self.outcome = outcome
        self.calls = []

    def validate_required_interaction(self, **kwargs):
        self.calls.append(kwargs)
        return RequirementInteractionCheck(
            outcome=self.outcome,
            identity=INTERACTION if self.outcome is InteractionOutcome.VALID else None,
            provenance_reference=(
                "catalogue-validation-1"
                if self.outcome is InteractionOutcome.VALID
                else None
            ),
        )


class FakeInteractionDiscovery:
    def __init__(self):
        self.calls = []

    def list_required_interactions(self, *, page, page_size, search=None):
        self.calls.append((page, page_size, search))
        return RequirementInteractionPage(
            interactions=(INTERACTION,),
            page=page,
            page_size=page_size,
            has_more=False,
        )


class MemoryRequirements:
    def __init__(self):
        self.values = {}
        self.commits = 0

    def find_active_by_semantic_key(self, key):
        return next(
            (
                value
                for value in self.values.values()
                if value.lifecycle_state is RequirementLifecycleState.ACTIVE
                and value.semantic_key == key
            ),
            None,
        )

    def get_by_id(self, requirement_id):
        return self.values.get(requirement_id)

    def list_by_governance_scopes(self, scopes, *, offset, limit):
        rows = tuple(
            sorted(
                (
                    value
                    for value in self.values.values()
                    if value.governance_scope in scopes
                ),
                key=lambda value: value.requirement_id,
            )
        )
        return rows[offset : offset + limit]

    def add(self, requirement):
        self.values[requirement.requirement_id] = requirement

    def save(self, requirement, *, expected_version):
        current = self.values[requirement.requirement_id]
        assert current.version == expected_version
        self.values[requirement.requirement_id] = requirement

    def commit(self):
        self.commits += 1


class FakeCatalogueDescriber:
    def execute(self, identities):
        return tuple(
            DirectedInteractionDescription(
                identity=identity,
                source_display_name="Demo Web Frontend",
                destination_display_name="Demo Orders API",
                dcs_display_name="HTTPS Orders API",
                dcs_projection_payload=None,
                dcs_provenance_reference="dcs-provenance",
            )
            for identity in identities
        )


class FakeDecoder:
    def decode(self, payload):
        raise AssertionError("decoder must not run when presentation payload is absent")


class FakePolicyAlignment:
    def __init__(self, outcome=PolicyCoverageOutcome.COVERED):
        self.outcome = outcome
        self.calls = []

    def check_exact_coverage(self, **kwargs):
        self.calls.append(kwargs)
        return self.outcome


class FakeDecisions:
    def __init__(self):
        self.calls = []

    def obtain(self, *, subject, governance_scope, as_of):
        self.calls.append(subject)
        return ConnectivityDecision(
            outcome=DecisionOutcome.ALLOWED,
            subject=subject,
            governance_scope=governance_scope,
            valid_from=as_of,
            decision_reference="unexpected-decision",
        )


class Scope:
    def __init__(
        self,
        *,
        authority=None,
        catalogue=None,
        requirements=None,
        policy_alignment=None,
    ):
        self.requirement_authority = authority or FakeAuthority()
        self.requirement_declaration_scopes = FakeDeclarationScopes()
        self.requirement_read_scopes = FakeReadScopes()
        self.requirement_catalogue = catalogue or FakeCatalogue()
        self.requirement_interaction_catalogue = FakeInteractionDiscovery()
        self.connectivity_requirements = requirements or MemoryRequirements()
        self.requirement_alignment = ConnectivityRequirementsAlignmentAdapter(
            reader=GetAuthorizedRequirement(
                authority=self.requirement_authority,
                requirements=self.connectivity_requirements,
            ),
            lister=ListConnectivityRequirements(
                read_scopes=self.requirement_read_scopes,
                requirements=self.connectivity_requirements,
            ),
        )
        self.policy_alignment = policy_alignment or FakePolicyAlignment()
        self.catalogue_describer = FakeCatalogueDescriber()
        self.dcs_decoder = FakeDecoder()


def build_client(
    *,
    authority=None,
    catalogue=None,
    requirements=None,
    policy_alignment=None,
):
    scope = Scope(
        authority=authority,
        catalogue=catalogue,
        requirements=requirements,
        policy_alignment=policy_alignment,
    )
    decisions = FakeDecisions()
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
            decisions=decisions,
            readiness=lambda: True,
            clock=lambda: NOW,
        )
    )
    return TestClient(app), scope, decisions


def login(client):
    response = client.post(
        "/api/v1/session",
        json={"login": "alexey", "password": "secret"},
    )
    assert response.status_code == 200


def payload(**overrides):
    value = {
        "authorityScope": "scope-a",
        "dependentComponentDeploymentId": str(SOURCE),
        "sourceComponentDeploymentId": str(SOURCE),
        "destinationComponentDeploymentId": str(DESTINATION),
        "dcsContractRevisionId": str(DCS),
        "applicability": {"kind": "Ongoing"},
        "justification": "Checkout requires Orders API.",
    }
    value.update(overrides)
    return value


def declare(client):
    response = client.post(
        "/api/v1/connectivity-requirements",
        json=payload(),
    )
    assert response.status_code == 201
    return response.json()["requirement"]


def test_scope_and_interaction_discovery_are_authorized_and_labelled():
    client, scope, _ = build_client()
    login(client)

    scopes = client.get("/api/v1/connectivity-requirements/scopes")
    interactions = client.get(
        "/api/v1/connectivity-requirements/interactions",
        params={"scope": "scope-a", "search": "orders"},
    )

    assert scopes.status_code == 200
    assert scopes.json()["scopes"] == [{"scope": "scope-a"}]
    assert scopes.json()["ambiguousScopes"] == [{"scope": "scope-b"}]
    assert interactions.status_code == 200
    item = interactions.json()["items"][0]
    assert item["sourceComponentDeploymentId"] == str(SOURCE)
    assert item["catalogue"]["sourceDisplayName"] == "Demo Web Frontend"
    assert item["catalogue"]["destinationDisplayName"] == "Demo Orders API"
    assert item["catalogue"]["dcsDisplayName"] == "HTTPS Orders API"
    assert scope.requirement_interaction_catalogue.calls == [(1, 50, "orders")]


def test_declaration_uses_session_actor_runtime_time_and_has_no_decision_side_effect():
    authority = FakeAuthority()
    client, scope, decisions = build_client(authority=authority)
    login(client)

    response = client.post(
        "/api/v1/connectivity-requirements",
        json=payload(),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["outcome"] == "Declared"
    requirement = body["requirement"]
    requirement_id = UUID(requirement["requirementId"])
    stored = scope.connectivity_requirements.get_by_id(requirement_id)
    assert stored.declaration_provenance.actor_id == "actor-1"
    assert stored.declaration_provenance.effective_time == NOW
    assert stored.governance_scope == "scope-a"
    assert stored.justification == "Checkout requires Orders API."
    assert requirement["catalogue"]["dcsDisplayName"] == "HTTPS Orders API"
    assert decisions.calls == []
    assert authority.calls[0]["actor_id"] == "actor-1"
    assert authority.calls[0]["scope"] == "scope-a"
    assert authority.calls[0]["effective_time"] == NOW


def test_repeated_declaration_resolves_same_requirement_without_overwrite():
    client, scope, _ = build_client()
    login(client)
    first = declare(client)

    response = client.post(
        "/api/v1/connectivity-requirements",
        json=payload(
            justification="Different reason",
            applicability={
                "kind": "AbsoluteWindow",
                "start": NOW.isoformat(),
                "end": (NOW + timedelta(hours=1)).isoformat(),
            },
        ),
    )

    assert response.status_code == 200
    assert response.json()["outcome"] == "Resolved"
    assert response.json()["requirement"]["requirementId"] == first["requirementId"]
    stored = scope.connectivity_requirements.get_by_id(UUID(first["requirementId"]))
    assert stored.justification == "Checkout requires Orders API."
    assert stored.applicability.kind.value == "Ongoing"


def test_spoofed_trusted_fields_are_rejected_before_business_authority():
    authority = FakeAuthority()
    client, _, _ = build_client(authority=authority)
    login(client)

    spoofed = payload(
        actorId="attacker",
        effectiveTime="2030-01-01T00:00:00Z",
        lifecycleState="Retired",
        version=99,
    )
    response = client.post(
        "/api/v1/connectivity-requirements",
        json=spoofed,
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ValidationError"
    assert authority.calls == []


def test_invalid_applicability_fails_before_authority():
    authority = FakeAuthority()
    client, _, _ = build_client(authority=authority)
    login(client)

    response = client.post(
        "/api/v1/connectivity-requirements",
        json=payload(
            applicability={
                "kind": "AbsoluteWindow",
                "start": "2026-09-09T10:00:00",
                "end": "2026-09-09T11:00:00",
            }
        ),
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "InvalidRequirementApplicability"
    assert authority.calls == []


def test_declaration_denied_creates_no_requirement_and_no_decision():
    authority = FakeAuthority(
        {"DeclareConnectivityRequirement": TernaryOutcome.DENIED}
    )
    client, scope, decisions = build_client(authority=authority)
    login(client)

    response = client.post(
        "/api/v1/connectivity-requirements",
        json=payload(),
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AuthorityDenied"
    assert scope.connectivity_requirements.values == {}
    assert decisions.calls == []


def test_list_detail_and_independent_capabilities():
    authority = FakeAuthority(
        {
            "SetConnectivityRequirementApplicability": TernaryOutcome.DENIED,
            "SetConnectivityRequirementJustification": TernaryOutcome.PERMITTED,
            "RetireConnectivityRequirement": TernaryOutcome.UNKNOWN,
        }
    )
    client, _, _ = build_client(authority=authority)
    login(client)
    created = declare(client)
    requirement_id = created["requirementId"]

    listing = client.get("/api/v1/connectivity-requirements")
    detail = client.get(
        f"/api/v1/connectivity-requirements/{requirement_id}"
    )

    assert listing.status_code == 200
    assert [item["requirementId"] for item in listing.json()["items"]] == [
        requirement_id
    ]
    assert listing.json()["ambiguousScopes"] == [{"scope": "scope-b"}]
    assert detail.status_code == 200
    assert detail.json()["capabilities"] == {
        "setApplicability": "Denied",
        "setJustification": "Permitted",
        "retire": "Unknown",
    }


def test_applicability_justification_and_retirement_mutations_use_stored_scope():
    authority = FakeAuthority()
    client, scope, _ = build_client(authority=authority)
    login(client)
    created = declare(client)
    requirement_id = created["requirementId"]

    window = client.patch(
        f"/api/v1/connectivity-requirements/{requirement_id}/applicability",
        json={
            "applicability": {
                "kind": "AbsoluteWindow",
                "start": NOW.isoformat(),
                "end": (NOW + timedelta(hours=2)).isoformat(),
            }
        },
    )
    reason = client.patch(
        f"/api/v1/connectivity-requirements/{requirement_id}/justification",
        json={"justification": "Updated reason."},
    )
    retired = client.post(
        f"/api/v1/connectivity-requirements/{requirement_id}/retirement"
    )

    assert window.status_code == 200
    assert window.json()["outcome"] == "Updated"
    assert reason.status_code == 200
    assert reason.json()["outcome"] == "Updated"
    assert retired.status_code == 200
    assert retired.json()["outcome"] == "Retired"

    stored = scope.connectivity_requirements.get_by_id(UUID(requirement_id))
    assert stored.lifecycle_state is RequirementLifecycleState.RETIRED
    assert stored.version == 4
    mutation_calls = [
        call
        for call in authority.calls
        if call["action"].value
        in {
            "SetConnectivityRequirementApplicability",
            "SetConnectivityRequirementJustification",
            "RetireConnectivityRequirement",
        }
    ]
    assert all(call["scope"] == "scope-a" for call in mutation_calls)
    assert all(call["actor_id"] == "actor-1" for call in mutation_calls)
    assert all(call["effective_time"] == NOW for call in mutation_calls)


def test_retired_requirement_rejects_further_property_mutation():
    client, _, _ = build_client()
    login(client)
    created = declare(client)
    requirement_id = created["requirementId"]
    assert client.post(
        f"/api/v1/connectivity-requirements/{requirement_id}/retirement"
    ).status_code == 200

    response = client.patch(
        f"/api/v1/connectivity-requirements/{requirement_id}/justification",
        json={"justification": "Too late"},
    )

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "RequirementRetired"


def test_unknown_requirement_is_not_found():
    client, _, _ = build_client()
    login(client)

    response = client.get(
        f"/api/v1/connectivity-requirements/{UUID(int=999)}"
    )

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RequirementNotFound"



def test_alignment_detail_exposes_covered_status_without_rule_details():
    policy = FakePolicyAlignment(PolicyCoverageOutcome.COVERED)
    client, scope, _ = build_client(policy_alignment=policy)
    login(client)
    created = declare(client)

    response = client.get(
        f"/api/v1/connectivity-requirements/{created['requirementId']}/alignment",
        params={"asOf": NOW.isoformat()},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "Covered"
    assert body["requirementId"] == created["requirementId"]
    assert body["requirementReadAuthorityReference"] == (
        "ReadConnectivityRequirement-authority"
    )
    assert "ruleId" not in body
    assert "governanceScope" not in body
    assert len(policy.calls) == 1
    assert policy.calls[0]["as_of"] == NOW


def test_alignment_unknown_is_normal_200_result_not_false_uncovered():
    client, _, _ = build_client(
        policy_alignment=FakePolicyAlignment(PolicyCoverageOutcome.UNKNOWN)
    )
    login(client)
    created = declare(client)

    response = client.get(
        f"/api/v1/connectivity-requirements/{created['requirementId']}/alignment",
        params={"asOf": NOW.isoformat()},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "Unknown"


def test_alignment_requirement_read_denied_returns_no_status_and_skips_policy():
    authority = FakeAuthority()
    policy = FakePolicyAlignment()
    client, scope, _ = build_client(
        authority=authority,
        policy_alignment=policy,
    )
    login(client)
    created = declare(client)
    authority.outcomes["ReadConnectivityRequirement"] = TernaryOutcome.DENIED
    policy.calls.clear()

    response = client.get(
        f"/api/v1/connectivity-requirements/{created['requirementId']}/alignment",
        params={"asOf": NOW.isoformat()},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AuthorityDenied"
    assert policy.calls == []


def test_alignment_page_marks_retired_requirement_not_current_without_policy_read():
    policy = FakePolicyAlignment()
    client, _, _ = build_client(policy_alignment=policy)
    login(client)
    created = declare(client)
    assert client.post(
        f"/api/v1/connectivity-requirements/{created['requirementId']}/retirement"
    ).status_code == 200
    policy.calls.clear()

    response = client.get(
        "/api/v1/connectivity-requirements/alignment",
        params={"asOf": NOW.isoformat(), "page": 1, "pageSize": 50},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == [
        {
            "requirementId": created["requirementId"],
            "status": "NotCurrent",
            "semanticIdentity": {
                "sourceComponentDeploymentId": str(SOURCE),
                "destinationComponentDeploymentId": str(DESTINATION),
                "dcsContractRevisionId": str(DCS),
            },
        }
    ]
    assert body["ambiguousScopes"] == [{"scope": "scope-b"}]
    assert policy.calls == []


def test_alignment_requires_explicit_offset_before_alignment_ports():
    policy = FakePolicyAlignment()
    client, _, _ = build_client(policy_alignment=policy)
    login(client)
    created = declare(client)
    policy.calls.clear()

    response = client.get(
        f"/api/v1/connectivity-requirements/{created['requirementId']}/alignment",
        params={"asOf": "2026-09-09T09:00:00"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "InvalidAsOf"
    assert policy.calls == []
