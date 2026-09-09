from ipaddress import IPv4Address, IPv4Network

from napms.access_policy_realization.domain.model import (
    AddressRange,
    PortRegion,
    TechnicalRegionFragment,
)


def project_asa_permit_regions(content: str) -> tuple[TechnicalRegionFragment, ...]:
    regions: list[TechnicalRegionFragment] = []
    for raw_line in content.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        tokens = line.split()
        if len(tokens) < 9 or tokens[0] != "access-list" or tokens[2:5] != [
            "extended",
            "permit",
            tokens[4],
        ]:
            raise ValueError("unsupported ASA ACL statement")
        protocol_number = {"tcp": 6, "udp": 17}.get(tokens[4])
        if protocol_number is None:
            raise ValueError("unsupported ASA protocol")
        index = 5
        source_address, index = _parse_address(tokens, index)
        source_ports, index = _parse_optional_port(tokens, index)
        destination_address, index = _parse_address(tokens, index)
        destination_ports, index = _parse_optional_port(tokens, index)
        if index != len(tokens):
            raise ValueError("unsupported trailing ASA ACL syntax")
        regions.append(
            TechnicalRegionFragment(
                source_address=source_address,
                destination_address=destination_address,
                protocol_number=protocol_number,
                source_ports=source_ports,
                destination_ports=destination_ports,
            )
        )
    return tuple(regions)


def _parse_address(tokens: list[str], index: int) -> tuple[AddressRange, int]:
    if index >= len(tokens):
        raise ValueError("missing ASA address")
    if tokens[index] == "host":
        address = IPv4Address(tokens[index + 1])
        return AddressRange(str(address), str(address)), index + 2
    network = IPv4Network((tokens[index], tokens[index + 1]), strict=False)
    return (
        AddressRange(str(network.network_address), str(network.broadcast_address)),
        index + 2,
    )


def _parse_optional_port(tokens: list[str], index: int) -> tuple[PortRegion, int]:
    if index >= len(tokens) or tokens[index] not in {"eq", "range"}:
        return PortRegion.numeric(0, 65535), index
    if tokens[index] == "eq":
        value = int(tokens[index + 1])
        return PortRegion.numeric(value, value), index + 2
    first = int(tokens[index + 1])
    last = int(tokens[index + 2])
    return PortRegion.numeric(first, last), index + 3
