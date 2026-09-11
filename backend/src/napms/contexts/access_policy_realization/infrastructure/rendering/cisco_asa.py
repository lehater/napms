from ipaddress import IPv4Address, IPv4Network, summarize_address_range

from napms.contexts.access_policy_realization.domain.model import (
    PortRegion,
    PortRegionKind,
    TechnicalRegionFragment,
)
from napms.contexts.access_policy_realization.domain.realization import (
    DesiredEnforcementPolicy,
    EnforcementTarget,
)
from napms.contexts.access_policy_realization.domain.rendering import (
    RenderedConfiguration,
    RenderedStatement,
    RenderStatus,
)


class CiscoAsaAclRenderer:
    name = "cisco-asa-extended-acl"
    contract_version = "1"

    def __init__(self, *, acl_name: str = "NAPMS") -> None:
        normalized = acl_name.strip()
        if not normalized or any(character.isspace() for character in normalized):
            raise ValueError("ASA ACL name must be non-empty and contain no whitespace")
        self._acl_name = normalized

    def render_target(
        self,
        *,
        target: EnforcementTarget,
        policy: DesiredEnforcementPolicy,
    ) -> RenderedConfiguration:
        intents = tuple(
            sorted(
                (item for item in policy.intents if item.target == target),
                key=lambda item: self._fragment_key(item.fragment),
            )
        )
        rendered: list[RenderedStatement] = []
        for intent in intents:
            try:
                lines = self._render_fragment(intent.fragment)
            except ValueError as exc:
                return RenderedConfiguration(
                    status=RenderStatus.UNSUPPORTED,
                    target=target,
                    renderer_name=self.name,
                    renderer_contract_version=self.contract_version,
                    reason=str(exc),
                )
            interaction_references = tuple(
                sorted(
                    f"{item.source_component_deployment_id}:"
                    f"{item.destination_component_deployment_id}:"
                    f"{item.dcs_contract_revision_id}"
                    for item in intent.interactions
                )
            )
            for line in lines:
                rendered.append(
                    RenderedStatement(
                        text=line,
                        rule_references=intent.rule_references,
                        interaction_references=interaction_references,
                        placement_provenance_references=(
                            intent.placement_provenance_references
                        ),
                    )
                )
        content = "\n".join(statement.text for statement in rendered)
        if content:
            content += "\n"
        return RenderedConfiguration(
            status=RenderStatus.RENDERED,
            target=target,
            renderer_name=self.name,
            renderer_contract_version=self.contract_version,
            content=content,
            statements=tuple(rendered),
        )

    def _render_fragment(self, fragment: TechnicalRegionFragment) -> tuple[str, ...]:
        if fragment.source_address.version != 4 or fragment.destination_address.version != 4:
            raise ValueError("Cisco ASA first slice supports IPv4 only")
        protocol = {6: "tcp", 17: "udp"}.get(fragment.protocol_number)
        if protocol is None:
            raise ValueError("Cisco ASA first slice supports TCP and UDP only")
        source_port = self._port_argument(fragment.source_ports)
        destination_port = self._port_argument(fragment.destination_ports)
        sources = self._address_arguments(
            fragment.source_address.first,
            fragment.source_address.last,
        )
        destinations = self._address_arguments(
            fragment.destination_address.first,
            fragment.destination_address.last,
        )
        lines: list[str] = []
        for source in sources:
            for destination in destinations:
                parts = [
                    "access-list",
                    self._acl_name,
                    "extended",
                    "permit",
                    protocol,
                    source,
                ]
                if source_port:
                    parts.append(source_port)
                parts.append(destination)
                if destination_port:
                    parts.append(destination_port)
                lines.append(" ".join(parts))
        return tuple(lines)

    @staticmethod
    def _address_arguments(first: str, last: str) -> tuple[str, ...]:
        networks = summarize_address_range(IPv4Address(first), IPv4Address(last))
        return tuple(CiscoAsaAclRenderer._network_argument(item) for item in networks)

    @staticmethod
    def _network_argument(network: IPv4Network) -> str:
        if network.prefixlen == 32:
            return f"host {network.network_address}"
        return f"{network.network_address} {network.netmask}"

    @staticmethod
    def _port_argument(region: PortRegion) -> str:
        if region.kind is not PortRegionKind.NUMERIC:
            raise ValueError("TCP/UDP rendering requires numeric port regions")
        assert region.first is not None and region.last is not None
        if region.first == 0 and region.last == 65535:
            return ""
        if region.first == region.last:
            return f"eq {region.first}"
        return f"range {region.first} {region.last}"

    @staticmethod
    def _fragment_key(fragment: TechnicalRegionFragment) -> tuple[object, ...]:
        return (
            fragment.source_address.version,
            fragment.source_address.first_int,
            fragment.source_address.last_int,
            fragment.destination_address.first_int,
            fragment.destination_address.last_int,
            fragment.protocol_number,
            fragment.source_ports.first,
            fragment.source_ports.last,
            fragment.destination_ports.first,
            fragment.destination_ports.last,
        )
