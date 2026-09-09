from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from napms.scoped_connectivity_inventory.application.model import (
    ComponentInventoryItem,
    ConnectivityRelationshipItem,
    CoverageSummary,
    DecisionSummary,
    DecisionSummaryState,
    Direction,
    EffectiveAtAsOf,
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
    require_aware,
)
from napms.scoped_connectivity_inventory.application.ports import (
    DecisionSummaryPort,
    DependencyAvailability,
    PolicySummaryPort,
    RequirementSummaryPort,
    ScopeAdmissionOutcome,
    ScopedCataloguePort,
    ScopedConnectivityAuthorityPort,
    ScopedResourcePort,
)


class ScopeDiscoveryQueryOutcome(str, Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"


@dataclass(frozen=True, slots=True)
class ScopeDiscoveryQueryResult:
    outcome: ScopeDiscoveryQueryOutcome
    permitted_scopes: tuple[str, ...]
    ambiguous_scopes: tuple[str, ...]


class InventoryQueryOutcome(str, Enum):
    AVAILABLE = "Available"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    AUTHORITY_AMBIGUOUS = "AuthorityAmbiguous"
    UNAVAILABLE = "Unavailable"


@dataclass(frozen=True, slots=True)
class ScopedConnectivityInventoryResult:
    outcome: InventoryQueryOutcome
    scope: str
    as_of: datetime
    page: ScopedConnectivityInventoryPage | None = None


def _unknown_requirement(identity: InteractionIdentity) -> RequirementSummary:
    return RequirementSummary(
        identity=identity,
        current=RequirementCurrent.UNKNOWN,
        historical_only=None,
        coverage=CoverageSummary.UNKNOWN,
    )


def _unknown_decision(identity: InteractionIdentity) -> DecisionSummary:
    return DecisionSummary(
        identity=identity,
        state=DecisionSummaryState.UNKNOWN,
    )


def _unknown_policy(identity: InteractionIdentity) -> PolicySummary:
    return PolicySummary(
        identity=identity,
        rule_exists=RuleExists.UNKNOWN,
        operational_state=PolicyOperationalState.UNAVAILABLE,
        effective_at_as_of=EffectiveAtAsOf.UNKNOWN,
    )


class DiscoverScopedConnectivityScopes:
    def __init__(self, *, authority: ScopedConnectivityAuthorityPort) -> None:
        self._authority = authority

    def execute(
        self,
        *,
        actor_id: str,
        as_of: datetime,
    ) -> ScopeDiscoveryQueryResult:
        if not actor_id:
            raise ValueError("actor_id must be non-empty")
        require_aware(as_of, field_name="as_of")

        discovered = self._authority.discover_scopes(
            actor_id=actor_id,
            as_of=as_of,
        )
        if discovered.availability is DependencyAvailability.UNAVAILABLE:
            return ScopeDiscoveryQueryResult(
                outcome=ScopeDiscoveryQueryOutcome.UNAVAILABLE,
                permitted_scopes=(),
                ambiguous_scopes=(),
            )
        return ScopeDiscoveryQueryResult(
            outcome=ScopeDiscoveryQueryOutcome.AVAILABLE,
            permitted_scopes=tuple(sorted(set(discovered.permitted_scopes))),
            ambiguous_scopes=tuple(sorted(set(discovered.ambiguous_scopes))),
        )


class ReadScopedConnectivityInventory:
    def __init__(
        self,
        *,
        authority: ScopedConnectivityAuthorityPort,
        resources: ScopedResourcePort,
        catalogue: ScopedCataloguePort,
        requirements: RequirementSummaryPort,
        decisions: DecisionSummaryPort,
        policy: PolicySummaryPort,
    ) -> None:
        self._authority = authority
        self._resources = resources
        self._catalogue = catalogue
        self._requirements = requirements
        self._decisions = decisions
        self._policy = policy

    def execute(
        self,
        *,
        actor_id: str,
        responsibility_scope: str,
        as_of: datetime,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
    ) -> ScopedConnectivityInventoryResult:
        if not actor_id:
            raise ValueError("actor_id must be non-empty")
        if not responsibility_scope:
            raise ValueError("responsibility_scope must be non-empty")
        require_aware(as_of, field_name="as_of")
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        normalized_search = search.strip() if search is not None else None
        if normalized_search == "":
            normalized_search = None
        if normalized_search is not None and len(normalized_search) > 256:
            raise ValueError("search must be at most 256 characters")

        admission = self._authority.check_scope(
            actor_id=actor_id,
            scope=responsibility_scope,
            as_of=as_of,
        )
        if admission.outcome is not ScopeAdmissionOutcome.PERMITTED:
            mapping = {
                ScopeAdmissionOutcome.DENIED: InventoryQueryOutcome.AUTHORITY_DENIED,
                ScopeAdmissionOutcome.UNKNOWN: InventoryQueryOutcome.AUTHORITY_UNKNOWN,
                ScopeAdmissionOutcome.AMBIGUOUS: (
                    InventoryQueryOutcome.AUTHORITY_AMBIGUOUS
                ),
            }
            return ScopedConnectivityInventoryResult(
                outcome=mapping[admission.outcome],
                scope=responsibility_scope,
                as_of=as_of,
            )
        if admission.authority_reference is None:
            return ScopedConnectivityInventoryResult(
                outcome=InventoryQueryOutcome.AUTHORITY_UNKNOWN,
                scope=responsibility_scope,
                as_of=as_of,
            )

        local_read = self._resources.list_local_resources(
            responsibility_scope=responsibility_scope,
            as_of=as_of,
            page=page,
            page_size=page_size,
            search=normalized_search,
        )
        if (
            local_read.availability is DependencyAvailability.UNAVAILABLE
            or local_read.page is None
        ):
            return ScopedConnectivityInventoryResult(
                outcome=InventoryQueryOutcome.UNAVAILABLE,
                scope=responsibility_scope,
                as_of=as_of,
            )

        local_page = local_read.page
        local_resources = local_page.resources
        partial = any(
            resource.realization_state is RealizationState.UNKNOWN
            for resource in local_resources
        )

        if not local_resources:
            return ScopedConnectivityInventoryResult(
                outcome=InventoryQueryOutcome.AVAILABLE,
                scope=responsibility_scope,
                as_of=as_of,
                page=ScopedConnectivityInventoryPage(
                    scope=responsibility_scope,
                    as_of=as_of,
                    items=(),
                    page=local_page.page,
                    page_size=local_page.page_size,
                    has_more=local_page.has_more,
                    partial=partial,
                    read_authority_reference=admission.authority_reference,
                ),
            )

        resource_refs = tuple(
            dict.fromkeys(resource.resource_reference for resource in local_resources)
        )
        components_read = self._catalogue.list_bound_components(
            resource_references=resource_refs,
            as_of=as_of,
        )
        if components_read.availability is DependencyAvailability.UNAVAILABLE:
            partial = True
            items = tuple(
                ResourceInventoryItem(
                    resource=resource,
                    components=(),
                    components_known=False,
                )
                for resource in local_resources
            )
            return ScopedConnectivityInventoryResult(
                outcome=InventoryQueryOutcome.AVAILABLE,
                scope=responsibility_scope,
                as_of=as_of,
                page=ScopedConnectivityInventoryPage(
                    scope=responsibility_scope,
                    as_of=as_of,
                    items=items,
                    page=local_page.page,
                    page_size=local_page.page_size,
                    has_more=local_page.has_more,
                    partial=partial,
                    read_authority_reference=admission.authority_reference,
                ),
            )

        local_ref_set = set(resource_refs)
        components_by_resource: dict[str, list] = {ref: [] for ref in resource_refs}
        for component in components_read.items:
            if component.resource_reference in local_ref_set:
                components_by_resource[component.resource_reference].append(component)

        component_ids = tuple(
            dict.fromkeys(
                component.component_deployment_id
                for ref in resource_refs
                for component in components_by_resource[ref]
            )
        )

        if not component_ids:
            items = tuple(
                ResourceInventoryItem(
                    resource=resource,
                    components=(),
                    components_known=True,
                )
                for resource in local_resources
            )
            return ScopedConnectivityInventoryResult(
                outcome=InventoryQueryOutcome.AVAILABLE,
                scope=responsibility_scope,
                as_of=as_of,
                page=ScopedConnectivityInventoryPage(
                    scope=responsibility_scope,
                    as_of=as_of,
                    items=items,
                    page=local_page.page,
                    page_size=local_page.page_size,
                    has_more=local_page.has_more,
                    partial=partial,
                    read_authority_reference=admission.authority_reference,
                ),
            )

        interactions_read = self._catalogue.list_interactions_for_components(
            component_deployment_ids=component_ids,
        )
        if interactions_read.availability is DependencyAvailability.UNAVAILABLE:
            partial = True
            interactions = ()
        else:
            interactions = interactions_read.items

        component_id_set = set(component_ids)
        relevant_interactions = tuple(
            interaction
            for interaction in interactions
            if (
                interaction.identity.source_component_deployment_id in component_id_set
                or interaction.identity.destination_component_deployment_id
                in component_id_set
            )
        )
        identities = tuple(
            dict.fromkeys(interaction.identity for interaction in relevant_interactions)
        )

        if identities:
            requirement_read = self._requirements.summarize_requirements(
                responsibility_scope=responsibility_scope,
                identities=identities,
                as_of=as_of,
            )
            decision_read = self._decisions.summarize_decisions(
                responsibility_scope=responsibility_scope,
                identities=identities,
                as_of=as_of,
            )
            policy_read = self._policy.summarize_policy(
                identities=identities,
                as_of=as_of,
            )
        else:
            requirement_read = None
            decision_read = None
            policy_read = None

        requirement_map = {}
        if requirement_read is not None:
            if requirement_read.availability is DependencyAvailability.UNAVAILABLE:
                partial = True
            else:
                requirement_map = {
                    item.identity: item for item in requirement_read.items
                }
        decision_map = {}
        if decision_read is not None:
            if decision_read.availability is DependencyAvailability.UNAVAILABLE:
                partial = True
            else:
                decision_map = {item.identity: item for item in decision_read.items}
        policy_map = {}
        if policy_read is not None:
            if policy_read.availability is DependencyAvailability.UNAVAILABLE:
                partial = True
            else:
                policy_map = {item.identity: item for item in policy_read.items}

        remote_component_ids = tuple(
            dict.fromkeys(
                (
                    interaction.identity.destination_component_deployment_id
                    if interaction.identity.source_component_deployment_id
                    in component_id_set
                    else interaction.identity.source_component_deployment_id
                )
                for interaction in relevant_interactions
            )
        )
        remote_bindings_read = self._catalogue.list_resource_bindings_for_components(
            component_deployment_ids=remote_component_ids,
            as_of=as_of,
        )
        remote_bindings_available = (
            remote_bindings_read.availability is DependencyAvailability.AVAILABLE
        )
        if not remote_bindings_available:
            partial = True

        remote_refs_by_component: dict[object, list[str]] = {
            component_id: [] for component_id in remote_component_ids
        }
        if remote_bindings_available:
            for binding in remote_bindings_read.items:
                if binding.component_deployment_id in remote_refs_by_component:
                    remote_refs_by_component[binding.component_deployment_id].append(
                        binding.resource_reference
                    )

        remote_resource_refs = tuple(
            dict.fromkeys(
                ref
                for refs in remote_refs_by_component.values()
                for ref in refs
            )
        )
        if remote_bindings_available and remote_resource_refs:
            remote_resolution = self._resources.resolve_resources(
                resource_references=remote_resource_refs,
                as_of=as_of,
            )
        else:
            remote_resolution = None

        resolved_remote_resources = {}
        remote_resolution_available = True
        if remote_resolution is not None:
            remote_resolution_available = (
                remote_resolution.availability is DependencyAvailability.AVAILABLE
            )
            if remote_resolution_available:
                resolved_remote_resources = {
                    item.resource_reference: item
                    for item in remote_resolution.resources
                }
            else:
                partial = True

        interaction_by_component: dict[object, list] = {
            component_id: [] for component_id in component_ids
        }
        for interaction in relevant_interactions:
            source = interaction.identity.source_component_deployment_id
            destination = interaction.identity.destination_component_deployment_id
            if source in interaction_by_component:
                interaction_by_component[source].append(interaction)
            if destination in interaction_by_component and destination != source:
                interaction_by_component[destination].append(interaction)

        resource_items = []
        for resource in local_resources:
            component_items = []
            for component in sorted(
                components_by_resource[resource.resource_reference],
                key=lambda item: (
                    item.display_name or "",
                    str(item.component_deployment_id),
                ),
            ):
                relationship_items = []
                for interaction in sorted(
                    interaction_by_component[component.component_deployment_id],
                    key=lambda item: (
                        str(item.identity.source_component_deployment_id),
                        str(item.identity.destination_component_deployment_id),
                        str(item.identity.dcs_contract_revision_id),
                    ),
                ):
                    identity = interaction.identity
                    if (
                        identity.source_component_deployment_id
                        == component.component_deployment_id
                    ):
                        direction = Direction.OUTGOING
                        remote_component_id = (
                            identity.destination_component_deployment_id
                        )
                        remote_display_name = interaction.destination_display_name
                    elif (
                        identity.destination_component_deployment_id
                        == component.component_deployment_id
                    ):
                        direction = Direction.INCOMING
                        remote_component_id = identity.source_component_deployment_id
                        remote_display_name = interaction.source_display_name
                    else:
                        continue

                    remote_resources_known = remote_bindings_available
                    remote_resources = []
                    if remote_bindings_available:
                        for ref in tuple(
                            dict.fromkeys(
                                remote_refs_by_component.get(remote_component_id, [])
                            )
                        ):
                            if remote_resolution_available:
                                snapshot = resolved_remote_resources.get(ref)
                                if snapshot is None:
                                    snapshot = ResourceSnapshot(
                                        resource_reference=ref,
                                        endpoints=(),
                                        realization_state=RealizationState.UNKNOWN,
                                    )
                                    partial = True
                                elif (
                                    snapshot.realization_state
                                    is RealizationState.UNKNOWN
                                ):
                                    partial = True
                                remote_resources.append(snapshot)
                            else:
                                remote_resources_known = False
                                remote_resources = []
                                break

                    requirement = requirement_map.get(identity)
                    if requirement is None:
                        requirement = _unknown_requirement(identity)
                        if requirement_read is not None:
                            partial = True

                    decision = decision_map.get(identity)
                    if decision is None:
                        decision = _unknown_decision(identity)
                        if decision_read is not None:
                            partial = True

                    policy = policy_map.get(identity)
                    if policy is None:
                        policy = _unknown_policy(identity)
                        if policy_read is not None:
                            partial = True

                    relationship_items.append(
                        ConnectivityRelationshipItem(
                            identity=identity,
                            direction=direction,
                            remote_component_deployment_id=remote_component_id,
                            remote_component_display_name=remote_display_name,
                            dcs_display_name=interaction.dcs_display_name,
                            access_summary=interaction.access_summary,
                            remote_resources=tuple(remote_resources),
                            remote_resources_known=remote_resources_known,
                            requirement=requirement,
                            decision=decision,
                            policy=policy,
                        )
                    )

                component_items.append(
                    ComponentInventoryItem(
                        component_deployment_id=component.component_deployment_id,
                        display_name=component.display_name,
                        relationships=tuple(relationship_items),
                        relationships_known=(
                            interactions_read.availability
                            is DependencyAvailability.AVAILABLE
                        ),
                    )
                )

            resource_items.append(
                ResourceInventoryItem(
                    resource=resource,
                    components=tuple(component_items),
                    components_known=True,
                )
            )

        return ScopedConnectivityInventoryResult(
            outcome=InventoryQueryOutcome.AVAILABLE,
            scope=responsibility_scope,
            as_of=as_of,
            page=ScopedConnectivityInventoryPage(
                scope=responsibility_scope,
                as_of=as_of,
                items=tuple(resource_items),
                page=local_page.page,
                page_size=local_page.page_size,
                has_more=local_page.has_more,
                partial=partial,
                read_authority_reference=admission.authority_reference,
            ),
        )
