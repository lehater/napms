from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import UUID

from fastapi.testclient import TestClient

from napms.contexts.access_policy.application.ports import (
    ConnectivityDecision,
    DecisionOutcome,
)
from napms.contexts.access_policy.domain.model import RuleSemanticIdentity
from napms.platform.auth.local import (
    InMemorySessionStore,
    LocalCredential,
    LocalPasswordAuthenticator,
    hash_local_password,
)
from napms.platform.http.api import HttpApiDependencies, create_http_api
from napms.workflows.scoped_connectivity_inventory.application.model import (
    ComponentInventoryItem,
    ConnectivityRelationshipItem,
    CoverageSummary,
    DecisionSummary,
    DecisionSummaryState,
    Direction,
    EffectiveAtAsOf,
    EndpointSnapshot,
    InteractionIdentity,
    PolicyOperationalState,
    PolicySummary,
    RealizationState,
    RequirementCurrent,
    RequirementSummary,
    ResourceInventoryItem,
    ResourceSnapshot,
    RuleExists,
    ScopedConnectivityInventoryPage,
)
from napms.workflows.scoped_connectivity_inventory.application.read import (
    InventoryQueryOutcome,
    ScopedConnectivityInventoryResult,
    ScopeDiscoveryQueryOutcome,
    ScopeDiscoveryQueryResult,
)


AS_OF = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=1)
DESTINATION = UUID(int=2)
DCS = UUID(int=3)
IDENTITY = InteractionIdentity(SOURCE, DESTINATION, DCS)


class FakeDecisions:
    def obtain(self, *, subject: RuleSemanticIdentity, governance_scope, as_of):
        return ConnectivityDecision(
            outcome=DecisionOutcome.ALLOWED,
            subject=subject,
            governance_scope=governance_scope,
            valid_from=as_of,
            decision_reference="unused",
        )


class FakeScopeDiscovery:
    def __init__(self, *, unavailable=False):
        self.unavailable = unavailable
        self.calls = []

    def execute(self, *, actor_id, as_of):
        self.calls.append((actor_id, as_of))
        if self.unavailable:
            return ScopeDiscoveryQueryResult(
                outcome=ScopeDiscoveryQueryOutcome.UNAVAILABLE,
                permitted_scopes=(),
                ambiguous_scopes=(),
            )
        return ScopeDiscoveryQueryResult(
            outcome=ScopeDiscoveryQueryOutcome.AVAILABLE,
            permitted_scopes=("scope-a",),
            ambiguous_scopes=("scope-b",),
        )


def inventory_page():
    local = ResourceSnapshot(
        resource_reference="resource-local",
        endpoints=(EndpointSnapshot("local:ep", "10.0.0.1"),),
        realization_state=RealizationState.RESOLVED,
    )
    remote = ResourceSnapshot(
        resource_reference="resource-remote",
        endpoints=(EndpointSnapshot("remote:ep", "10.0.0.2"),),
        realization_state=RealizationState.RESOLVED,
    )
    relationship = ConnectivityRelationshipItem(
        identity=IDENTITY,
        direction=Direction.OUTGOING,
        remote_component_deployment_id=DESTINATION,
        remote_component_display_name="Orders API",
        dcs_display_name="HTTPS Orders",
        access_summary="tcp 443",
        remote_resources=(remote,),
        remote_resources_known=True,
        requirement=RequirementSummary(
            identity=IDENTITY,
            current=RequirementCurrent.REQUIRED,
            historical_only=False,
            coverage=CoverageSummary.COVERED,
        ),
        decision=DecisionSummary(
            identity=IDENTITY,
            state=DecisionSummaryState.UNKNOWN,
        ),
        policy=PolicySummary(
            identity=IDENTITY,
            rule_exists=RuleExists.YES,
            operational_state=PolicyOperationalState.ACTIVE,
            effective_at_as_of=EffectiveAtAsOf.YES,
        ),
    )
    return ScopedConnectivityInventoryPage(
        scope="scope-a",
        as_of=AS_OF,
        items=(
            ResourceInventoryItem(
                resource=local,
                components=(
                    ComponentInventoryItem(
                        component_deployment_id=SOURCE,
                        display_name="Checkout",
                        relationships=(relationship,),
                        relationships_known=True,
                    ),
                ),
                components_known=True,
            ),
        ),
        page=1,
        page_size=50,
        has_more=False,
        partial=True,
        read_authority_reference="auth-scoped",
    )


class FakeInventory:
    def __init__(self, outcome=InventoryQueryOutcome.AVAILABLE):
        self.outcome = outcome
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)
        return ScopedConnectivityInventoryResult(
            outcome=self.outcome,
            scope=kwargs["responsibility_scope"],
            as_of=kwargs["as_of"],
            page=(
                inventory_page()
                if self.outcome is InventoryQueryOutcome.AVAILABLE
                else None
            ),
        )


class Scope:
    def __init__(self, *, scope_discovery=None, inventory=None):
        self.scoped_connectivity_scopes = scope_discovery or FakeScopeDiscovery()
        self.scoped_connectivity_inventory = inventory or FakeInventory()


def client_for(*, scope_discovery=None, inventory=None):
    scope = Scope(
        scope_discovery=scope_discovery,
        inventory=inventory,
    )
    sessions = InMemorySessionStore(new_session_id=lambda: "session-1")
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
            decisions=FakeDecisions(),
            readiness=lambda: True,
            clock=lambda: AS_OF,
        )
    )
    client = TestClient(app)
    response = client.post(
        "/api/v1/session",
        json={"login": "alexey", "password": "secret"},
    )
    assert response.status_code == 200
    return client, scope


def test_connectivity_scope_discovery_uses_explicit_as_of():
    client, scope = client_for()

    response = client.get(
        "/api/v1/connectivity/scopes",
        params={"asOf": AS_OF.isoformat()},
    )

    assert response.status_code == 200
    assert response.json() == {
        "asOf": AS_OF.isoformat(),
        "scopes": [{"scope": "scope-a"}],
        "ambiguousScopes": [{"scope": "scope-b"}],
    }
    assert scope.scoped_connectivity_scopes.calls == [
        ("actor-1", AS_OF)
    ]


def test_connectivity_inventory_returns_resource_centric_safe_projection():
    client, scope = client_for()

    response = client.get(
        "/api/v1/connectivity",
        params={
            "scope": "scope-a",
            "asOf": AS_OF.isoformat(),
            "page": 1,
            "pageSize": 50,
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["scope"] == "scope-a"
    assert payload["asOf"] == AS_OF.isoformat()
    assert payload["partial"] is True
    assert payload["items"][0]["resource"] == {
        "resourceReference": "resource-local",
        "realizationState": "Resolved",
        "endpoints": [
            {
                "endpointReference": "local:ep",
                "technicalAddress": "10.0.0.1",
            }
        ],
    }
    component = payload["items"][0]["components"][0]
    assert component["displayName"] == "Checkout"
    relationship = component["relationships"][0]
    assert relationship["direction"] == "Outgoing"
    assert relationship["remoteComponent"]["displayName"] == "Orders API"
    assert relationship["accessSummary"] == "tcp 443"
    assert relationship["need"] == {
        "current": "Required",
        "historicalOnly": False,
        "coverage": "Covered",
    }
    assert relationship["decision"] == {"state": "Unknown"}
    assert relationship["policy"] == {
        "ruleExists": "Yes",
        "operationalState": "Active",
        "effectiveAtAsOf": "Yes",
    }
    assert scope.scoped_connectivity_inventory.calls[0]["actor_id"] == "actor-1"


def test_connectivity_inventory_authority_denied_is_403():
    client, _ = client_for(
        inventory=FakeInventory(InventoryQueryOutcome.AUTHORITY_DENIED)
    )

    response = client.get(
        "/api/v1/connectivity",
        params={"scope": "scope-a", "asOf": AS_OF.isoformat()},
    )

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "AuthorityDenied"


def test_connectivity_inventory_unavailable_is_503():
    client, _ = client_for(
        inventory=FakeInventory(InventoryQueryOutcome.UNAVAILABLE)
    )

    response = client.get(
        "/api/v1/connectivity",
        params={"scope": "scope-a", "asOf": AS_OF.isoformat()},
    )

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "ScopedConnectivityUnavailable"


def test_connectivity_requires_offset_aware_as_of():
    client, _ = client_for()

    response = client.get(
        "/api/v1/connectivity",
        params={"scope": "scope-a", "asOf": "2026-09-09T12:00:00"},
    )

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "InvalidAsOf"
