from napms.application_catalogue.adapters.dcs_json_codec import JsonDcsProjectionCodec
from napms.application_catalogue.application.ports import ApplicationCatalogueRepository
from napms.policy_export.application.normalization_types import PortConstraintKind
from napms.scoped_connectivity_inventory.application.model import Direction, RuleExists
from napms.scoped_connectivity_inventory.application.read import (
    DiscoverScopedConnectivityScopes,
    InventoryQueryOutcome,
    ReadScopedConnectivityInventory,
    ScopeDiscoveryQueryOutcome,
)
from napms.traffic_analysis.application.model import (
    EndpointResolution,
    PolicyMatch,
    ResolutionState,
    TrafficAnalysisQuery,
)


class ScopedConnectivityTrafficPolicyAdapter:
    """Reuse the accepted owner-preserving connectivity projection for Checker policy."""

    def __init__(
        self,
        *,
        discover: DiscoverScopedConnectivityScopes,
        inventory: ReadScopedConnectivityInventory,
        catalogue: ApplicationCatalogueRepository,
        decoder: JsonDcsProjectionCodec,
    ) -> None:
        self._discover = discover
        self._inventory = inventory
        self._catalogue = catalogue
        self._decoder = decoder

    def find_matches(
        self,
        *,
        actor_id: str,
        query: TrafficAnalysisQuery,
        source: EndpointResolution,
        destination: EndpointResolution,
    ) -> tuple[PolicyMatch, ...]:
        if (
            source.state not in (ResolutionState.RESOLVED, ResolutionState.AMBIGUOUS)
            or destination.state not in (ResolutionState.RESOLVED, ResolutionState.AMBIGUOUS)
        ):
            return ()

        source_refs = {item.resource_reference for item in source.resources}
        destination_refs = {item.resource_reference for item in destination.resources}
        discovered = self._discover.execute(actor_id=actor_id, as_of=query.as_of)
        if discovered.outcome is not ScopeDiscoveryQueryOutcome.AVAILABLE:
            return ()

        found: dict[tuple[str, object], PolicyMatch] = {}
        for scope in discovered.permitted_scopes:
            page_number = 1
            while page_number <= 100:
                result = self._inventory.execute(
                    actor_id=actor_id,
                    responsibility_scope=scope,
                    as_of=query.as_of,
                    page=page_number,
                    page_size=100,
                )
                if (
                    result.outcome is not InventoryQueryOutcome.AVAILABLE
                    or result.page is None
                ):
                    break
                page = result.page
                for resource_item in page.items:
                    local_ref = resource_item.resource.resource_reference
                    local_is_source = local_ref in source_refs
                    local_is_destination = local_ref in destination_refs
                    if not local_is_source and not local_is_destination:
                        continue
                    for component in resource_item.components:
                        for relationship in component.relationships:
                            remote_refs = {
                                item.resource_reference
                                for item in relationship.remote_resources
                            }
                            directed_match = (
                                local_is_source
                                and relationship.direction is Direction.OUTGOING
                                and bool(remote_refs & destination_refs)
                            ) or (
                                local_is_destination
                                and relationship.direction is Direction.INCOMING
                                and bool(remote_refs & source_refs)
                            )
                            if not directed_match:
                                continue
                            if not self._dcs_matches(
                                relationship.identity.dcs_contract_revision_id,
                                query,
                            ):
                                continue

                            if local_is_source and relationship.direction is Direction.OUTGOING:
                                source_name = component.display_name
                                destination_name = relationship.remote_component_display_name
                            else:
                                source_name = relationship.remote_component_display_name
                                destination_name = component.display_name

                            rule = (
                                relationship.policy.operational_state.value
                                if relationship.policy.rule_exists is RuleExists.YES
                                else relationship.policy.rule_exists.value
                            )
                            found[(scope, relationship.identity)] = PolicyMatch(
                                source_component=source_name,
                                destination_component=destination_name,
                                dcs_reference=str(
                                    relationship.identity.dcs_contract_revision_id
                                ),
                                dcs_display_name=relationship.dcs_display_name,
                                access_summary=relationship.access_summary,
                                requirement=relationship.requirement.current.value,
                                decision=relationship.decision.state.value,
                                rule=rule,
                                effective=relationship.policy.effective_at_as_of.value,
                                scope=scope,
                                partial=(page.partial or not relationship.remote_resources_known),
                            )
                if not page.has_more:
                    break
                page_number += 1

        return tuple(
            found[key]
            for key in sorted(found, key=lambda item: (item[0], str(item[1])))
        )

    def _dcs_matches(self, revision_id, query: TrafficAnalysisQuery) -> bool:
        revision = self._catalogue.get_dcs_revision(revision_id)
        if revision is None:
            return False
        alternatives = self._decoder.decode(revision.projection_payload)
        query_protocol = query.protocol.strip().lower()
        aliases = {
            "6": "tcp",
            "17": "udp",
            "1": "icmp",
            "58": "ipv6-icmp",
        }
        query_protocol = aliases.get(query_protocol, query_protocol)
        for alternative in alternatives:
            if alternative.protocol.strip().lower() != query_protocol:
                continue
            ports = alternative.destination_ports
            if ports.kind is PortConstraintKind.ANY:
                return True
            if ports.kind is not PortConstraintKind.RANGES:
                continue
            if any(
                item.first <= query.destination_port_first
                and query.destination_port_last <= item.last
                for item in ports.ranges
            ):
                return True
        return False
