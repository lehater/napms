from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from napms.access_policy.application.ports import (
    AccessRulePersistenceError,
    AccessRuleReadScopeOptions,
    AuthorityCheck,
    EffectivePolicyReadScopeOptions,
    ConnectivityDecision,
    DecisionOutcome,
    TernaryOutcome,
)
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    EffectiveWindow,
    OperationalState,
    ProposalProvenance,
    RuleSemanticIdentity,
)
from napms.contexts.application_catalogue.application.describe_interactions import (
    DirectedInteractionDescription,
)
from napms.runtime.auth import (
    InMemorySessionStore,
    LocalCredential,
    LocalPasswordAuthenticator,
    hash_local_password,
)
from napms.runtime.http_api import HttpApiDependencies, create_http_api


NOW = datetime(2026, 9, 9, 9, 0, tzinfo=timezone.utc)


def make_rule(index: int, scope: str, state=OperationalState.ACTIVE) -> AccessRule:
    identity = RuleSemanticIdentity(
        UUID(int=index * 10 + 1),
        UUID(int=index * 10 + 2),
        UUID(int=index * 10 + 3),
    )
    rule = AccessRule.materialized_from_allowed_decision(
        rule_id=UUID(int=index),
        semantic_identity=identity,
        decision=DecisionReference(
            subject=identity,
            result=ConnectivityDecisionResult.ALLOWED,
            decision_id=f"decision-{index}",
        ),
        proposal_provenance=ProposalProvenance(
            actor_id="proposer",
            authority_scope=scope,
            effective_time=NOW,
            authority_reference=f"proposal-auth-{index}",
            catalogue_reference=f"catalogue-{index}",
        ),
    )
    if state is OperationalState.INACTIVE:
        return rule.with_operational_state(
            target_state=OperationalState.INACTIVE,
            actor_id="previous-operator",
            effective_time=NOW,
            authority_reference="previous-authority",
        )
    return rule


class FakeReadScopes:
    def __init__(self, permitted=("scope-a",), ambiguous=("scope-b",)):
        self.permitted = permitted
        self.ambiguous = ambiguous

    def list_effective_read_rule_scopes(self, **kwargs):
        return AccessRuleReadScopeOptions(self.permitted, self.ambiguous)


class FakeAuthority:
    def __init__(
        self,
        *,
        read=TernaryOutcome.PERMITTED,
        mutate=TernaryOutcome.PERMITTED,
        policy_read=TernaryOutcome.PERMITTED,
    ):
        self.read = read
        self.mutate = mutate
        self.policy_read = policy_read
        self.calls = []

    def check(self, **kwargs):
        self.calls.append(kwargs)
        action = kwargs["action"].value
        outcome = (
            self.read
            if action == "ReadAccessRule"
            else self.policy_read
            if action == "ReadEffectiveDesiredPolicy"
            else self.mutate
        )
        reference = (
            f"{action}-authority"
            if outcome is TernaryOutcome.PERMITTED
            else None
        )
        return AuthorityCheck(outcome, reference)


class FakePolicyScopes:
    def __init__(self, permitted=("scope-a",), ambiguous=()):
        self.permitted = permitted
        self.ambiguous = ambiguous

    def list_effective_policy_read_scopes(self, **kwargs):
        return EffectivePolicyReadScopeOptions(self.permitted, self.ambiguous)


class MemoryRules:
    def __init__(self, rules=(), fail_commit=False):
        self.rules = {rule.rule_id: rule for rule in rules}
        self.fail_commit = fail_commit
        self.list_calls = []

    def get_by_id(self, rule_id):
        return self.rules.get(rule_id)

    def find_by_identity(self, identity):
        return next(
            (rule for rule in self.rules.values() if rule.semantic_identity == identity),
            None,
        )

    def list_by_governance_scope(self, scope):
        return tuple(
            rule for rule in self.rules.values() if rule.governance_scope == scope
        )

    def list_by_governance_scopes(self, scopes, *, offset, limit):
        self.list_calls.append((scopes, offset, limit))
        visible = tuple(
            sorted(
                (
                    rule
                    for rule in self.rules.values()
                    if rule.governance_scope in scopes
                ),
                key=lambda rule: rule.rule_id,
            )
        )
        return visible[offset : offset + limit]

    def add(self, rule):
        self.rules[rule.rule_id] = rule

    def save(self, rule):
        self.rules[rule.rule_id] = rule

    def commit(self):
        if self.fail_commit:
            raise AccessRulePersistenceError()


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


class FakeDecoder:
    def decode(self, payload):
        raise AssertionError("presentation decoder must not run without payload")


class FakeDecisions:
    def obtain(self, *, subject, governance_scope, as_of):
        return ConnectivityDecision(
            outcome=DecisionOutcome.ALLOWED,
            subject=subject,
            governance_scope=governance_scope,
            valid_from=as_of,
            decision_reference="unused-decision",
        )


class Scope:
    def __init__(
        self,
        *,
        rules,
        authority,
        read_scopes=None,
        policy_scopes=None,
    ):
        self.access_rules = rules
        self.authority = authority
        self.rule_read_scope_discovery = read_scopes or FakeReadScopes()
        self.effective_policy_scope_discovery = policy_scopes or FakePolicyScopes()
        self.catalogue_describer = FakeCatalogueDescriber()
        self.dcs_decoder = FakeDecoder()


def build_client(
    *,
    rules=None,
    authority=None,
    read_scopes=None,
    policy_scopes=None,
):
    rules = rules or MemoryRules(
        (
            make_rule(1, "scope-a"),
            make_rule(2, "scope-b"),
        )
    )
    authority = authority or FakeAuthority()
    scope = Scope(
        rules=rules,
        authority=authority,
        read_scopes=read_scopes,
        policy_scopes=policy_scopes,
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
            decisions=FakeDecisions(),
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


def test_list_returns_only_rules_from_permitted_read_scopes():
    client, scope = build_client()
    login(client)

    response = client.get("/api/v1/access-rules")

    assert response.status_code == 200
    payload = response.json()
    assert [item["ruleId"] for item in payload["items"]] == [str(UUID(int=1))]
    assert payload["ambiguousScopes"] == [{"scope": "scope-b"}]
    assert scope.access_rules.list_calls == [(("scope-a",), 0, 51)]


def test_detail_returns_rule_and_independent_mutation_capability():
    authority = FakeAuthority(mutate=TernaryOutcome.DENIED)
    client, _ = build_client(authority=authority)
    login(client)

    response = client.get(f"/api/v1/access-rules/{UUID(int=1)}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["rule"]["ruleId"] == str(UUID(int=1))
    assert payload["rule"]["governanceScope"] == "scope-a"
    assert payload["capabilities"]["setOperationalState"] == "Denied"
    assert payload["capabilities"]["setEffectiveWindow"] == "Denied"
    assert [call["action"].value for call in authority.calls] == [
        "ReadAccessRule",
        "SetRuleOperationalState",
        "SetRuleEffectiveWindow",
    ]


def test_detail_read_denial_returns_no_rule_data():
    client, _ = build_client(
        authority=FakeAuthority(read=TernaryOutcome.DENIED)
    )
    login(client)

    response = client.get(f"/api/v1/access-rules/{UUID(int=1)}")

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AuthorityDenied"
    assert "rule" not in response.json()


def test_detail_unknown_rule_is_explicit_not_found():
    client, _ = build_client()
    login(client)

    response = client.get(f"/api/v1/access-rules/{UUID(int=999)}")

    assert response.status_code == 404
    assert response.json()["error"]["code"] == "RuleNotFound"


def test_state_mutation_uses_session_actor_runtime_time_and_rule_scope():
    authority = FakeAuthority()
    client, scope = build_client(authority=authority)
    login(client)

    response = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/operational-state",
        json={"targetState": "Inactive"},
    )

    assert response.status_code == 200
    assert response.json()["outcome"] == "Updated"
    assert response.json()["rule"]["operationalState"] == "Inactive"

    updated = scope.access_rules.get_by_id(UUID(int=1))
    transition = updated.operational_state_history[-1]
    assert transition.actor_id == "actor-1"
    assert transition.effective_time == NOW
    assert transition.governance_scope == "scope-a"
    assert transition.authority_reference == "SetRuleOperationalState-authority"

    mutation_call = authority.calls[-1]
    assert mutation_call["actor_id"] == "actor-1"
    assert mutation_call["scope"] == "scope-a"
    assert mutation_call["effective_time"] == NOW


def test_state_mutation_rejects_actor_scope_and_time_spoofing_in_payload():
    authority = FakeAuthority()
    client, scope = build_client(authority=authority)
    login(client)

    response = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/operational-state",
        json={
            "targetState": "Inactive",
            "actorId": "attacker",
            "scope": "scope-b",
            "effectiveTime": "2030-01-01T00:00:00Z",
        },
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ValidationError"
    assert scope.access_rules.get_by_id(UUID(int=1)).operational_state is OperationalState.ACTIVE
    assert authority.calls == []


def test_same_state_is_explicit_successful_non_transition():
    client, scope = build_client()
    login(client)

    response = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/operational-state",
        json={"targetState": "Active"},
    )

    assert response.status_code == 200
    assert response.json()["outcome"] == "AlreadyInRequestedState"
    assert scope.access_rules.get_by_id(UUID(int=1)).operational_state_history == ()


def test_state_mutation_authority_denied_fails_closed():
    client, scope = build_client(
        authority=FakeAuthority(mutate=TernaryOutcome.DENIED)
    )
    login(client)

    response = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/operational-state",
        json={"targetState": "Inactive"},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AuthorityDenied"
    assert scope.access_rules.get_by_id(UUID(int=1)).operational_state is OperationalState.ACTIVE


def test_state_mutation_persistence_failure_is_not_success():
    rules = MemoryRules((make_rule(1, "scope-a"),), fail_commit=True)
    client, _ = build_client(rules=rules)
    login(client)

    response = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/operational-state",
        json={"targetState": "Inactive"},
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "PersistenceUnavailable"



def test_list_rejects_invalid_pagination_at_transport_boundary():
    client, _ = build_client()
    login(client)

    too_small = client.get("/api/v1/access-rules", params={"page": 0})
    too_large = client.get("/api/v1/access-rules", params={"pageSize": 101})

    assert too_small.status_code == 422
    assert too_small.json()["error"]["code"] == "ValidationError"
    assert too_large.status_code == 422
    assert too_large.json()["error"]["code"] == "ValidationError"



def test_effective_window_set_uses_session_actor_runtime_time_and_rule_scope():
    authority = FakeAuthority()
    client, scope = build_client(authority=authority)
    login(client)

    start = NOW + timedelta(hours=1)
    end = NOW + timedelta(hours=5)
    response = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/effective-window",
        json={
            "window": {
                "start": start.isoformat(),
                "end": end.isoformat(),
            }
        },
    )

    assert response.status_code == 200
    assert response.json()["outcome"] == "Updated"
    assert response.json()["rule"]["effectiveWindow"] == {
        "start": start.isoformat(),
        "end": end.isoformat(),
    }

    updated = scope.access_rules.get_by_id(UUID(int=1))
    change = updated.effective_window_history[-1]
    assert change.actor_id == "actor-1"
    assert change.effective_time == NOW
    assert change.governance_scope == "scope-a"
    assert change.authority_reference == "SetRuleEffectiveWindow-authority"

    call = authority.calls[-1]
    assert call["action"].value == "SetRuleEffectiveWindow"
    assert call["actor_id"] == "actor-1"
    assert call["scope"] == "scope-a"
    assert call["effective_time"] == NOW


def test_effective_window_clear_and_same_value_semantics():
    client, scope = build_client()
    login(client)
    start = NOW + timedelta(hours=1)
    end = NOW + timedelta(hours=5)
    payload = {
        "window": {
            "start": start.isoformat(),
            "end": end.isoformat(),
        }
    }

    first = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/effective-window",
        json=payload,
    )
    same = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/effective-window",
        json=payload,
    )
    cleared = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/effective-window",
        json={"window": None},
    )

    assert first.status_code == 200
    assert first.json()["outcome"] == "Updated"
    assert same.status_code == 200
    assert same.json()["outcome"] == "AlreadyInRequestedWindow"
    assert cleared.status_code == 200
    assert cleared.json()["outcome"] == "Updated"
    assert cleared.json()["rule"]["effectiveWindow"] is None

    rule = scope.access_rules.get_by_id(UUID(int=1))
    assert rule.effective_window is None
    assert len(rule.effective_window_history) == 2
    assert rule.effective_window_history[0].previous_window is None
    assert rule.effective_window_history[0].new_window == EffectiveWindow(start, end)
    assert rule.effective_window_history[1].previous_window == EffectiveWindow(start, end)
    assert rule.effective_window_history[1].new_window is None


def test_effective_window_rejects_invalid_or_spoofed_payload_before_authority():
    authority = FakeAuthority()
    client, scope = build_client(authority=authority)
    login(client)

    naive = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/effective-window",
        json={
            "window": {
                "start": "2026-09-10T08:00:00",
                "end": "2026-09-10T18:00:00",
            }
        },
    )
    reversed_window = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/effective-window",
        json={
            "window": {
                "start": "2026-09-10T18:00:00+00:00",
                "end": "2026-09-10T08:00:00+00:00",
            }
        },
    )
    spoofed = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/effective-window",
        json={
            "window": None,
            "actorId": "attacker",
            "scope": "scope-b",
            "effectiveTime": "2030-01-01T00:00:00Z",
        },
    )

    assert naive.status_code == 422
    assert naive.json()["error"]["code"] == "InvalidEffectiveWindow"
    assert reversed_window.status_code == 422
    assert reversed_window.json()["error"]["code"] == "InvalidEffectiveWindow"
    assert spoofed.status_code == 422
    assert spoofed.json()["error"]["code"] == "ValidationError"
    assert authority.calls == []
    assert scope.access_rules.get_by_id(UUID(int=1)).effective_window is None


def test_effective_window_authority_denied_fails_closed():
    client, scope = build_client(
        authority=FakeAuthority(mutate=TernaryOutcome.DENIED)
    )
    login(client)

    response = client.patch(
        f"/api/v1/access-rules/{UUID(int=1)}/effective-window",
        json={
            "window": {
                "start": (NOW + timedelta(hours=1)).isoformat(),
                "end": (NOW + timedelta(hours=2)).isoformat(),
            }
        },
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AuthorityDenied"
    assert scope.access_rules.get_by_id(UUID(int=1)).effective_window is None


def test_policy_view_scope_discovery_is_fail_closed():
    client, _ = build_client(
        policy_scopes=FakePolicyScopes(
            permitted=("scope-a",),
            ambiguous=("scope-b",),
        )
    )
    login(client)

    response = client.get(
        "/api/v1/policy-views/scopes",
        params={"asOf": NOW.isoformat()},
    )

    assert response.status_code == 200
    assert response.json() == {
        "scopes": [{"scope": "scope-a"}],
        "ambiguousScopes": [{"scope": "scope-b"}],
    }


def test_effective_policy_returns_only_rules_effective_at_explicit_as_of():
    inside = NOW + timedelta(hours=2)
    outside = NOW + timedelta(hours=8)
    base = make_rule(1, "scope-a")
    windowed = base.with_effective_window(
        window=EffectiveWindow(
            NOW + timedelta(hours=1),
            NOW + timedelta(hours=4),
        ),
        actor_id="window-operator",
        effective_time=NOW,
        authority_reference="window-authority",
    )
    client, _ = build_client(rules=MemoryRules((windowed,)))
    login(client)

    selected = client.get(
        "/api/v1/effective-desired-policy",
        params={"scope": "scope-a", "asOf": inside.isoformat()},
    )
    empty = client.get(
        "/api/v1/effective-desired-policy",
        params={"scope": "scope-a", "asOf": outside.isoformat()},
    )

    assert selected.status_code == 200
    assert selected.json()["authorityReference"] == "ReadEffectiveDesiredPolicy-authority"
    assert [rule["ruleId"] for rule in selected.json()["rules"]] == [str(UUID(int=1))]
    assert empty.status_code == 200
    assert empty.json()["rules"] == []


def test_effective_policy_denied_or_naive_as_of_returns_no_policy_data():
    denied_client, _ = build_client(
        authority=FakeAuthority(policy_read=TernaryOutcome.DENIED)
    )
    login(denied_client)

    denied = denied_client.get(
        "/api/v1/effective-desired-policy",
        params={"scope": "scope-a", "asOf": NOW.isoformat()},
    )
    assert denied.status_code == 403
    assert denied.json()["error"]["code"] == "AuthorityDenied"
    assert "rules" not in denied.json()

    client, _ = build_client()
    login(client)
    naive = client.get(
        "/api/v1/effective-desired-policy",
        params={"scope": "scope-a", "asOf": "2026-09-09T12:00:00"},
    )
    assert naive.status_code == 422
    assert naive.json()["error"]["code"] == "InvalidAsOf"



def test_policy_view_scope_discovery_rejects_naive_as_of():
    client, _ = build_client()
    login(client)

    response = client.get(
        "/api/v1/policy-views/scopes",
        params={"asOf": "2026-09-09T12:00:00"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "InvalidAsOf"
