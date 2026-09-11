from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.scoped_connectivity_inventory.application.model import (
    BoundComponentSnapshot,
    ComponentResourceBindingSnapshot,
    CoverageSummary,
    DecisionSummary,
    DecisionSummaryState,
    Direction,
    EffectiveAtAsOf,
    EndpointSnapshot,
    InteractionIdentity,
    InteractionSnapshot,
    PolicyOperationalState,
    PolicySummary,
    RealizationState,
    RequirementCurrent,
    RequirementSummary,
    ResourceSnapshot,
    RuleExists,
    ScopedConnectivityInventoryInvariantError,
)
from napms.scoped_connectivity_inventory.application.ports import (
    BoundComponentReadResult,
    ComponentResourceBindingReadResult,
    DecisionSummaryReadResult,
    DependencyAvailability,
    InteractionReadResult,
    LocalResourcePage,
    LocalResourceReadResult,
    PolicySummaryReadResult,
    RequirementSummaryReadResult,
    ResourceResolutionResult,
    ScopeAdmissionOutcome,
    ScopeAdmissionResult,
    ScopeDiscoveryResult,
)
from napms.scoped_connectivity_inventory.application.read import (
    DiscoverScopedConnectivityScopes,
    InventoryQueryOutcome,
    ReadScopedConnectivityInventory,
    ScopeDiscoveryQueryOutcome,
)


AS_OF = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
C1 = UUID("00000000-0000-0000-0000-000000000101")
C2 = UUID("00000000-0000-0000-0000-000000000102")
DCS = UUID("00000000-0000-0000-0000-000000000103")
IDENTITY = InteractionIdentity(C1, C2, DCS)


def resource(reference, address):
    return ResourceSnapshot(
        resource_reference=reference,
        endpoints=(EndpointSnapshot(f"{reference}:ep", address),),
        realization_state=RealizationState.RESOLVED,
    )


R1 = resource("r1", "10.0.0.1")
R2 = resource("r2", "10.0.0.2")


class FakeAuthority:
    def __init__(
        self,
        *,
        admission=ScopeAdmissionResult(
            ScopeAdmissionOutcome.PERMITTED,
            "auth:read-scoped",
        ),
        discovery=ScopeDiscoveryResult(
            DependencyAvailability.AVAILABLE,
            permitted_scopes=("scope-b", "scope-a"),
            ambiguous_scopes=("scope-x",),
        ),
    ):
        self.admission = admission
        self.discovery = discovery
        self.check_calls = []

    def discover_scopes(self, *, actor_id, as_of):
        return self.discovery

    def check_scope(self, *, actor_id, scope, as_of):
        self.check_calls.append((actor_id, scope, as_of))
        return self.admission


class FakeResources:
    def __init__(self, *, items=(R1,), unavailable=False):
        self.items = tuple(items)
        self.unavailable = unavailable
        self.list_calls = []
        self.resolve_calls = []

    def list_local_resources(
        self,
        *,
        responsibility_scope,
        as_of,
        page,
        page_size,
        search,
    ):
        self.list_calls.append(
            (responsibility_scope, as_of, page, page_size, search)
        )
        if self.unavailable:
            return LocalResourceReadResult(DependencyAvailability.UNAVAILABLE)
        return LocalResourceReadResult(
            DependencyAvailability.AVAILABLE,
            LocalResourcePage(
                resources=self.items,
                page=page,
                page_size=page_size,
                has_more=False,
            ),
        )

    def resolve_resources(self, *, resource_references, as_of):
        self.resolve_calls.append((resource_references, as_of))
        by_ref = {item.resource_reference: item for item in self.items}
        return ResourceResolutionResult(
            DependencyAvailability.AVAILABLE,
            tuple(
                by_ref.get(
                    ref,
                    ResourceSnapshot(
                        resource_reference=ref,
                        endpoints=(),
                        realization_state=RealizationState.UNRESOLVED,
                    ),
                )
                for ref in resource_references
            ),
        )


class FakeCatalogue:
    def __init__(
        self,
        *,
        components=(),
        interactions=(),
        bindings=(),
        component_availability=DependencyAvailability.AVAILABLE,
        interaction_availability=DependencyAvailability.AVAILABLE,
        binding_availability=DependencyAvailability.AVAILABLE,
    ):
        self.components = tuple(components)
        self.interactions = tuple(interactions)
        self.bindings = tuple(bindings)
        self.component_availability = component_availability
        self.interaction_availability = interaction_availability
        self.binding_availability = binding_availability

    def list_bound_components(self, *, resource_references, as_of):
        return BoundComponentReadResult(
            self.component_availability,
            self.components if self.component_availability is DependencyAvailability.AVAILABLE else (),
        )

    def list_interactions_for_components(self, *, component_deployment_ids):
        return InteractionReadResult(
            self.interaction_availability,
            self.interactions if self.interaction_availability is DependencyAvailability.AVAILABLE else (),
        )

    def list_resource_bindings_for_components(
        self,
        *,
        component_deployment_ids,
        as_of,
    ):
        allowed = set(component_deployment_ids)
        return ComponentResourceBindingReadResult(
            self.binding_availability,
            tuple(
                item
                for item in self.bindings
                if item.component_deployment_id in allowed
            )
            if self.binding_availability is DependencyAvailability.AVAILABLE
            else (),
        )


class FakeRequirements:
    def __init__(self, availability=DependencyAvailability.AVAILABLE):
        self.availability = availability

    def summarize_requirements(
        self,
        *,
        responsibility_scope,
        identities,
        as_of,
    ):
        return RequirementSummaryReadResult(
            self.availability,
            tuple(
                RequirementSummary(
                    identity=identity,
                    current=RequirementCurrent.REQUIRED,
                    historical_only=False,
                    coverage=CoverageSummary.COVERED,
                )
                for identity in identities
            )
            if self.availability is DependencyAvailability.AVAILABLE
            else (),
        )


class FakeDecisions:
    def __init__(self, availability=DependencyAvailability.AVAILABLE):
        self.availability = availability

    def summarize_decisions(
        self,
        *,
        responsibility_scope,
        identities,
        as_of,
    ):
        return DecisionSummaryReadResult(
            self.availability,
            tuple(
                DecisionSummary(identity, DecisionSummaryState.ALLOWED)
                for identity in identities
            )
            if self.availability is DependencyAvailability.AVAILABLE
            else (),
        )


class FakePolicy:
    def __init__(self, availability=DependencyAvailability.AVAILABLE):
        self.availability = availability

    def summarize_policy(self, *, identities, as_of):
        return PolicySummaryReadResult(
            self.availability,
            tuple(
                PolicySummary(
                    identity=identity,
                    rule_exists=RuleExists.YES,
                    operational_state=PolicyOperationalState.ACTIVE,
                    effective_at_as_of=EffectiveAtAsOf.YES,
                )
                for identity in identities
            )
            if self.availability is DependencyAvailability.AVAILABLE
            else (),
        )


def service(
    *,
    authority=None,
    resources=None,
    catalogue=None,
    requirements=None,
    decisions=None,
    policy=None,
):
    return ReadScopedConnectivityInventory(
        authority=authority or FakeAuthority(),
        resources=resources or FakeResources(),
        catalogue=catalogue or FakeCatalogue(),
        requirements=requirements or FakeRequirements(),
        decisions=decisions or FakeDecisions(),
        policy=policy or FakePolicy(),
    )


def test_scope_discovery_sorts_permitted_and_ambiguous_scopes():
    result = DiscoverScopedConnectivityScopes(
        authority=FakeAuthority()
    ).execute(actor_id="actor-1", as_of=AS_OF)

    assert result.outcome is ScopeDiscoveryQueryOutcome.AVAILABLE
    assert result.permitted_scopes == ("scope-a", "scope-b")
    assert result.ambiguous_scopes == ("scope-x",)


def test_scope_authority_denial_fails_before_resource_read():
    resources = FakeResources()
    result = service(
        authority=FakeAuthority(
            admission=ScopeAdmissionResult(ScopeAdmissionOutcome.DENIED)
        ),
        resources=resources,
    ).execute(
        actor_id="actor-1",
        responsibility_scope="scope-a",
        as_of=AS_OF,
    )

    assert result.outcome is InventoryQueryOutcome.AUTHORITY_DENIED
    assert result.page is None
    assert resources.list_calls == []


def test_authorized_scope_with_no_local_resources_is_empty_not_denied():
    result = service(
        resources=FakeResources(items=())
    ).execute(
        actor_id="actor-1",
        responsibility_scope="scope-a",
        as_of=AS_OF,
    )

    assert result.outcome is InventoryQueryOutcome.AVAILABLE
    assert result.page is not None
    assert result.page.items == ()
    assert result.page.partial is False


def test_local_resource_is_preserved_when_no_component_is_bound():
    result = service().execute(
        actor_id="actor-1",
        responsibility_scope="scope-a",
        as_of=AS_OF,
    )

    assert result.outcome is InventoryQueryOutcome.AVAILABLE
    assert result.page is not None
    assert len(result.page.items) == 1
    row = result.page.items[0]
    assert row.resource.resource_reference == "r1"
    assert row.components == ()
    assert row.components_known is True


def test_same_interaction_is_outgoing_and_incoming_when_both_sides_are_local():
    resources = FakeResources(items=(R1, R2))
    catalogue = FakeCatalogue(
        components=(
            BoundComponentSnapshot("r1", C1, "Frontend"),
            BoundComponentSnapshot("r2", C2, "Orders"),
        ),
        interactions=(
            InteractionSnapshot(
                identity=IDENTITY,
                source_display_name="Frontend",
                destination_display_name="Orders",
                dcs_display_name="HTTPS",
                access_summary="TCP 443",
            ),
        ),
        bindings=(
            ComponentResourceBindingSnapshot(C1, "r1"),
            ComponentResourceBindingSnapshot(C2, "r2"),
        ),
    )

    result = service(
        resources=resources,
        catalogue=catalogue,
    ).execute(
        actor_id="actor-1",
        responsibility_scope="scope-a",
        as_of=AS_OF,
    )

    assert result.outcome is InventoryQueryOutcome.AVAILABLE
    assert result.page is not None
    by_resource = {
        item.resource.resource_reference: item for item in result.page.items
    }

    outgoing = by_resource["r1"].components[0].relationships[0]
    incoming = by_resource["r2"].components[0].relationships[0]

    assert outgoing.identity == incoming.identity == IDENTITY
    assert outgoing.direction is Direction.OUTGOING
    assert outgoing.remote_component_deployment_id == C2
    assert [r.resource_reference for r in outgoing.remote_resources] == ["r2"]

    assert incoming.direction is Direction.INCOMING
    assert incoming.remote_component_deployment_id == C1
    assert [r.resource_reference for r in incoming.remote_resources] == ["r1"]

    assert outgoing.requirement.current is RequirementCurrent.REQUIRED
    assert outgoing.decision.state is DecisionSummaryState.ALLOWED
    assert outgoing.policy.rule_exists is RuleExists.YES


def test_unavailable_summary_keeps_topology_and_marks_only_dimension_unknown():
    catalogue = FakeCatalogue(
        components=(BoundComponentSnapshot("r1", C1, "Frontend"),),
        interactions=(
            InteractionSnapshot(
                identity=IDENTITY,
                source_display_name="Frontend",
                destination_display_name="Orders",
                dcs_display_name="HTTPS",
            ),
        ),
        bindings=(ComponentResourceBindingSnapshot(C2, "r2"),),
    )
    result = service(
        catalogue=catalogue,
        requirements=FakeRequirements(DependencyAvailability.UNAVAILABLE),
    ).execute(
        actor_id="actor-1",
        responsibility_scope="scope-a",
        as_of=AS_OF,
    )

    assert result.outcome is InventoryQueryOutcome.AVAILABLE
    assert result.page is not None
    assert result.page.partial is True
    relationship = result.page.items[0].components[0].relationships[0]
    assert relationship.remote_component_deployment_id == C2
    assert relationship.requirement.current is RequirementCurrent.UNKNOWN
    assert relationship.decision.state is DecisionSummaryState.ALLOWED
    assert relationship.policy.rule_exists is RuleExists.YES


def test_component_dependency_failure_preserves_local_resource_as_partial():
    result = service(
        catalogue=FakeCatalogue(
            component_availability=DependencyAvailability.UNAVAILABLE
        )
    ).execute(
        actor_id="actor-1",
        responsibility_scope="scope-a",
        as_of=AS_OF,
    )

    assert result.outcome is InventoryQueryOutcome.AVAILABLE
    assert result.page is not None
    assert result.page.partial is True
    assert result.page.items[0].components == ()
    assert result.page.items[0].components_known is False


def test_naive_as_of_is_rejected():
    with pytest.raises(ScopedConnectivityInventoryInvariantError):
        service().execute(
            actor_id="actor-1",
            responsibility_scope="scope-a",
            as_of=datetime(2026, 9, 9, 12, 0),
        )
