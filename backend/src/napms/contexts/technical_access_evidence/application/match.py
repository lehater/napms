from enum import Enum

from napms.contexts.technical_access_evidence.domain.model import (
    AddressConstraint,
    AddressConstraintKind,
    PortConstraint,
    PortConstraintKind,
    ProtocolSelector,
    ProtocolSelectorKind,
    TechnicalAccessPredicate,
)


class PredicateMatchKind(str, Enum):
    EXACT = "Exact"
    COVERS_QUERY = "CoversQuery"
    COVERED_BY_QUERY = "CoveredByQuery"
    OVERLAP = "Overlap"
    NO_MATCH = "NoMatch"
    UNKNOWN = "Unknown"


class _SetRelation(str, Enum):
    EXACT = "Exact"
    SUPERSET = "Superset"
    SUBSET = "Subset"
    OVERLAP = "Overlap"
    DISJOINT = "Disjoint"
    UNKNOWN = "Unknown"


def match_predicates(
    *,
    evidence: TechnicalAccessPredicate,
    query: TechnicalAccessPredicate,
) -> PredicateMatchKind:
    """Classify the packet-set relation of one evidence predicate to a query.

    `CoversQuery` means the evidence predicate is a strict superset of the query;
    `CoveredByQuery` means it is a strict subset. The relation is deliberately
    independent from evidence action/authorization.
    """

    relations = (
        _address_relation(evidence.source_addresses, query.source_addresses),
        _address_relation(
            evidence.destination_addresses,
            query.destination_addresses,
        ),
        _protocol_relation(evidence.protocol, query.protocol),
        _port_relation(evidence.source_ports, query.source_ports),
        _port_relation(evidence.destination_ports, query.destination_ports),
    )
    if _SetRelation.DISJOINT in relations:
        return PredicateMatchKind.NO_MATCH
    if _SetRelation.UNKNOWN in relations:
        return PredicateMatchKind.UNKNOWN
    if all(item is _SetRelation.EXACT for item in relations):
        return PredicateMatchKind.EXACT
    if all(item in (_SetRelation.EXACT, _SetRelation.SUPERSET) for item in relations):
        return PredicateMatchKind.COVERS_QUERY
    if all(item in (_SetRelation.EXACT, _SetRelation.SUBSET) for item in relations):
        return PredicateMatchKind.COVERED_BY_QUERY
    return PredicateMatchKind.OVERLAP


def _protocol_relation(left: ProtocolSelector, right: ProtocolSelector) -> _SetRelation:
    if left == right:
        return _SetRelation.EXACT
    if left.kind is ProtocolSelectorKind.ANY:
        return _SetRelation.SUPERSET
    if right.kind is ProtocolSelectorKind.ANY:
        return _SetRelation.SUBSET
    return _SetRelation.DISJOINT


def _address_relation(left: AddressConstraint, right: AddressConstraint) -> _SetRelation:
    if left == right:
        return _SetRelation.EXACT
    if left.kind is AddressConstraintKind.ANY:
        return _SetRelation.SUPERSET
    if right.kind is AddressConstraintKind.ANY:
        return _SetRelation.SUBSET
    return _interval_relation(
        tuple((item.version, item.first_int, item.last_int) for item in left.ranges),
        tuple((item.version, item.first_int, item.last_int) for item in right.ranges),
    )


def _port_relation(left: PortConstraint, right: PortConstraint) -> _SetRelation:
    if left == right:
        return _SetRelation.EXACT
    if (
        left.kind is PortConstraintKind.NOT_APPLICABLE
        or right.kind is PortConstraintKind.NOT_APPLICABLE
    ):
        return _SetRelation.DISJOINT
    if left.kind is PortConstraintKind.ANY:
        return _SetRelation.SUPERSET
    if right.kind is PortConstraintKind.ANY:
        return _SetRelation.SUBSET
    return _interval_relation(
        tuple((0, item.first, item.last) for item in left.ranges),
        tuple((0, item.first, item.last) for item in right.ranges),
    )


def _interval_relation(
    left: tuple[tuple[int, int, int], ...],
    right: tuple[tuple[int, int, int], ...],
) -> _SetRelation:
    left_subset = _is_subset(left, right)
    right_subset = _is_subset(right, left)
    if left_subset and right_subset:
        return _SetRelation.EXACT
    if right_subset:
        return _SetRelation.SUPERSET
    if left_subset:
        return _SetRelation.SUBSET
    if _overlaps(left, right):
        return _SetRelation.OVERLAP
    return _SetRelation.DISJOINT


def _is_subset(
    candidate: tuple[tuple[int, int, int], ...],
    container: tuple[tuple[int, int, int], ...],
) -> bool:
    for family, first, last in candidate:
        if not any(
            other_family == family and other_first <= first and last <= other_last
            for other_family, other_first, other_last in container
        ):
            return False
    return True


def _overlaps(
    left: tuple[tuple[int, int, int], ...],
    right: tuple[tuple[int, int, int], ...],
) -> bool:
    return any(
        left_family == right_family
        and max(left_first, right_first) <= min(left_last, right_last)
        for left_family, left_first, left_last in left
        for right_family, right_first, right_last in right
    )
