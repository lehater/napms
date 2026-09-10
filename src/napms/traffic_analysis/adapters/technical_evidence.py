from datetime import timedelta

from napms.technical_access_evidence.application.match import (
    PredicateMatchKind,
    match_predicates,
)
from napms.technical_access_evidence.application.ports import (
    EvidenceSetFilters,
    TechnicalAccessEvidenceRepository,
)
from napms.technical_access_evidence.domain.model import (
    AddressConstraint,
    AddressRange,
    EvidenceKind,
    EvidenceTimeKind,
    PortConstraint,
    PortRange,
    ProtocolSelector,
    SourceScopeReference,
    TechnicalAccessPredicate,
)
from napms.traffic_analysis.application.model import (
    EvidenceSnapshot,
    RuleMatchKind,
    TechnicalRuleMatch,
    TrafficAnalysisInvariantError,
    TrafficAnalysisQuery,
)


_PROTOCOLS = {"ICMP": 1, "TCP": 6, "UDP": 17, "IPV6-ICMP": 58}


class TechnicalAccessEvidenceTrafficAnalysisAdapter:
    """Read last-known configured snapshots; never contacts network devices."""

    def __init__(self, *, evidence_sets: TechnicalAccessEvidenceRepository) -> None:
        self._evidence_sets = evidence_sets

    def latest_applicable(
        self,
        *,
        query: TrafficAnalysisQuery,
        provider_namespace: str,
        device_reference: str,
    ) -> EvidenceSnapshot | None:
        del provider_namespace  # source-specific correspondence belongs to composition.
        rows = self._evidence_sets.list(
            filters=EvidenceSetFilters(
                source_scope=SourceScopeReference(device_reference),
                kind=EvidenceKind.CONFIGURED,
                recorded_until=query.as_of + timedelta(microseconds=1),
            ),
            offset=0,
            limit=1000,
        )
        applicable = tuple(
            item
            for item in rows
            if item.evidence_time.kind is EvidenceTimeKind.INSTANT
            and item.evidence_time.at is not None
            and item.evidence_time.at <= query.as_of
            and item.recorded_at <= query.as_of
        )
        if not applicable:
            return None

        selected = max(
            applicable,
            key=lambda item: (
                item.evidence_time.at,
                item.recorded_at,
                str(item.evidence_set_id),
            ),
        )
        query_predicate = _query_predicate(query)
        matches = []
        for entry in selected.entries:
            relation = match_predicates(
                evidence=entry.payload.predicate,
                query=query_predicate,
            )
            if relation is PredicateMatchKind.NO_MATCH:
                continue
            matches.append(
                TechnicalRuleMatch(
                    entry_reference=(
                        entry.payload.source_entry_reference
                        or str(entry.evidence_entry_id)
                    ),
                    action=(
                        entry.payload.action.value
                        if entry.payload.action is not None
                        else "Unknown"
                    ),
                    normalized=_format_predicate(entry.payload.predicate),
                    match_kind=RuleMatchKind(relation.value),
                )
            )

        return EvidenceSnapshot(
            evidence_set_reference=str(selected.evidence_set_id),
            source_reference=(
                f"{selected.source.namespace}:{selected.source.reference}"
            ),
            source_scope_reference=selected.source_scope.value,
            captured_at=selected.evidence_time.at,
            recorded_at=selected.recorded_at,
            provenance_references=(
                f"capture:{selected.source_capture_reference.value}",
            ),
            matches=tuple(matches),
        )


def _query_predicate(query: TrafficAnalysisQuery) -> TechnicalAccessPredicate:
    protocol = query.protocol.strip().upper()
    try:
        number = _PROTOCOLS.get(protocol, int(protocol))
    except ValueError as exc:
        raise TrafficAnalysisInvariantError(
            f"unsupported protocol {query.protocol!r}"
        ) from exc
    if not 0 <= number <= 255:
        raise TrafficAnalysisInvariantError("IP protocol number must be within 0..255")
    return TechnicalAccessPredicate(
        source_addresses=AddressConstraint.ranged(
            AddressRange(query.source_address, query.source_address)
        ),
        destination_addresses=AddressConstraint.ranged(
            AddressRange(query.destination_address, query.destination_address)
        ),
        protocol=ProtocolSelector.ip_protocol(number),
        source_ports=PortConstraint.any(),
        destination_ports=PortConstraint.ranged(
            PortRange(query.destination_port_first, query.destination_port_last)
        ),
    )


def _format_predicate(predicate: TechnicalAccessPredicate) -> str:
    return (
        f"{_format_addresses(predicate.source_addresses)} → "
        f"{_format_addresses(predicate.destination_addresses)} "
        f"{_format_protocol(predicate.protocol)} "
        f"{_format_ports(predicate.destination_ports)}"
    )


def _format_addresses(value: AddressConstraint) -> str:
    if not value.ranges:
        return "any"
    return ", ".join(
        item.first if item.first == item.last else f"{item.first}-{item.last}"
        for item in value.ranges
    )


def _format_ports(value: PortConstraint) -> str:
    if not value.ranges:
        return value.kind.value
    return ", ".join(
        str(item.first) if item.first == item.last else f"{item.first}-{item.last}"
        for item in value.ranges
    )


def _format_protocol(value: ProtocolSelector) -> str:
    if value.number is None:
        return "any"
    names = {1: "ICMP", 6: "TCP", 17: "UDP", 58: "IPV6-ICMP"}
    return names.get(value.number, str(value.number))
