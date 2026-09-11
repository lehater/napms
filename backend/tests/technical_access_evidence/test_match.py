from napms.technical_access_evidence.application.match import (
    PredicateMatchKind,
    match_predicates,
)
from napms.technical_access_evidence.domain.model import (
    AddressConstraint,
    AddressRange,
    PortConstraint,
    PortRange,
    ProtocolSelector,
    TechnicalAccessPredicate,
)


def predicate(
    source_first: str,
    source_last: str,
    destination_first: str,
    destination_last: str,
    port_first: int,
    port_last: int,
) -> TechnicalAccessPredicate:
    return TechnicalAccessPredicate(
        source_addresses=AddressConstraint.ranged(
            AddressRange(source_first, source_last)
        ),
        destination_addresses=AddressConstraint.ranged(
            AddressRange(destination_first, destination_last)
        ),
        protocol=ProtocolSelector.ip_protocol(6),
        source_ports=PortConstraint.any(),
        destination_ports=PortConstraint.ranged(PortRange(port_first, port_last)),
    )


QUERY = predicate(
    "10.10.10.10",
    "10.10.10.10",
    "10.20.20.20",
    "10.20.20.20",
    443,
    443,
)


def test_exact_predicate_match() -> None:
    assert match_predicates(evidence=QUERY, query=QUERY) is PredicateMatchKind.EXACT


def test_broader_evidence_covers_query() -> None:
    evidence = predicate(
        "10.10.10.0",
        "10.10.10.255",
        "10.20.20.0",
        "10.20.20.255",
        400,
        500,
    )
    assert (
        match_predicates(evidence=evidence, query=QUERY)
        is PredicateMatchKind.COVERS_QUERY
    )


def test_narrower_evidence_is_covered_by_broad_query() -> None:
    broad_query = predicate(
        "10.10.10.0",
        "10.10.10.255",
        "10.20.20.0",
        "10.20.20.255",
        400,
        500,
    )
    assert (
        match_predicates(evidence=QUERY, query=broad_query)
        is PredicateMatchKind.COVERED_BY_QUERY
    )


def test_partial_overlap_is_not_promoted_to_coverage() -> None:
    evidence = predicate(
        "10.10.10.10",
        "10.10.10.20",
        "10.20.20.20",
        "10.20.20.30",
        443,
        450,
    )
    query = predicate(
        "10.10.10.15",
        "10.10.10.25",
        "10.20.20.25",
        "10.20.20.35",
        445,
        455,
    )
    assert match_predicates(evidence=evidence, query=query) is PredicateMatchKind.OVERLAP


def test_protocol_or_address_disjoint_is_no_match() -> None:
    udp_query = TechnicalAccessPredicate(
        source_addresses=QUERY.source_addresses,
        destination_addresses=QUERY.destination_addresses,
        protocol=ProtocolSelector.ip_protocol(17),
        source_ports=PortConstraint.any(),
        destination_ports=QUERY.destination_ports,
    )
    assert (
        match_predicates(evidence=QUERY, query=udp_query)
        is PredicateMatchKind.NO_MATCH
    )
