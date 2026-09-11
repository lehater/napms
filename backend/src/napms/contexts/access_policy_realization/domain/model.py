from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from ipaddress import IPv4Address, IPv6Address, ip_address
from uuid import UUID


class ResolutionInvariantError(Exception):
    """Raised when Access Policy Realization resolution state is invalid."""


def require_aware(value: datetime, *, field_name: str = "as_of") -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ResolutionInvariantError(f"{field_name} must be offset-aware")


def _non_empty(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ResolutionInvariantError(f"{field_name} must be non-empty")
    return normalized


@dataclass(frozen=True, slots=True)
class AddressRange:
    first: str
    last: str

    def __post_init__(self) -> None:
        try:
            first = ip_address(self.first)
            last = ip_address(self.last)
        except ValueError as exc:
            raise ResolutionInvariantError(
                "address range requires valid IP addresses"
            ) from exc
        if first.version != last.version:
            raise ResolutionInvariantError(
                "address range cannot cross IP families"
            )
        if int(first) > int(last):
            raise ResolutionInvariantError(
                "address range requires first <= last"
            )
        object.__setattr__(self, "first", str(first))
        object.__setattr__(self, "last", str(last))

    @property
    def version(self) -> int:
        return ip_address(self.first).version

    @property
    def first_int(self) -> int:
        return int(ip_address(self.first))

    @property
    def last_int(self) -> int:
        return int(ip_address(self.last))

    @classmethod
    def from_ints(
        cls,
        first: int,
        last: int,
        *,
        version: int,
    ) -> "AddressRange":
        constructor = IPv4Address if version == 4 else IPv6Address
        return cls(str(constructor(first)), str(constructor(last)))


class AddressConstraintKind(str, Enum):
    ANY = "Any"
    RANGES = "Ranges"


@dataclass(frozen=True, slots=True)
class AddressConstraint:
    kind: AddressConstraintKind
    ranges: tuple[AddressRange, ...] = ()

    def __post_init__(self) -> None:
        if self.kind is AddressConstraintKind.ANY:
            if self.ranges:
                raise ResolutionInvariantError(
                    "Any address constraint cannot carry ranges"
                )
            return
        if self.kind is not AddressConstraintKind.RANGES or not self.ranges:
            raise ResolutionInvariantError(
                "Ranges address constraint requires ranges"
            )
        ordered = sorted(
            self.ranges,
            key=lambda item: (
                item.version,
                item.first_int,
                item.last_int,
            ),
        )
        canonical: list[AddressRange] = []
        for current in ordered:
            if not canonical:
                canonical.append(current)
                continue
            previous = canonical[-1]
            if (
                previous.version == current.version
                and current.first_int <= previous.last_int + 1
            ):
                canonical[-1] = AddressRange.from_ints(
                    previous.first_int,
                    max(previous.last_int, current.last_int),
                    version=previous.version,
                )
            else:
                canonical.append(current)
        object.__setattr__(self, "ranges", tuple(canonical))

    @classmethod
    def any(cls) -> "AddressConstraint":
        return cls(AddressConstraintKind.ANY)

    @classmethod
    def ranged(
        cls,
        *ranges: AddressRange,
    ) -> "AddressConstraint":
        return cls(AddressConstraintKind.RANGES, tuple(ranges))


@dataclass(frozen=True, slots=True, order=True)
class PortRange:
    first: int
    last: int

    def __post_init__(self) -> None:
        if (
            not isinstance(self.first, int)
            or isinstance(self.first, bool)
            or not isinstance(self.last, int)
            or isinstance(self.last, bool)
            or not 0 <= self.first <= self.last <= 65535
        ):
            raise ResolutionInvariantError(
                "port range must be within 0..65535 with first <= last"
            )


class PortConstraintKind(str, Enum):
    NOT_APPLICABLE = "NotApplicable"
    ANY = "Any"
    RANGES = "Ranges"


@dataclass(frozen=True, slots=True)
class PortConstraint:
    kind: PortConstraintKind
    ranges: tuple[PortRange, ...] = ()

    def __post_init__(self) -> None:
        if self.kind in (
            PortConstraintKind.ANY,
            PortConstraintKind.NOT_APPLICABLE,
        ):
            if self.ranges:
                raise ResolutionInvariantError(
                    "Any/NotApplicable port constraints cannot carry ranges"
                )
            return
        if self.kind is not PortConstraintKind.RANGES or not self.ranges:
            raise ResolutionInvariantError(
                "Ranges port constraint requires ranges"
            )
        ordered = sorted(self.ranges)
        canonical: list[PortRange] = []
        for current in ordered:
            if not canonical:
                canonical.append(current)
                continue
            previous = canonical[-1]
            if current.first <= previous.last + 1:
                canonical[-1] = PortRange(
                    previous.first,
                    max(previous.last, current.last),
                )
            else:
                canonical.append(current)
        object.__setattr__(self, "ranges", tuple(canonical))

    @classmethod
    def not_applicable(cls) -> "PortConstraint":
        return cls(PortConstraintKind.NOT_APPLICABLE)

    @classmethod
    def any(cls) -> "PortConstraint":
        return cls(PortConstraintKind.ANY)

    @classmethod
    def ranged(
        cls,
        *ranges: PortRange,
    ) -> "PortConstraint":
        return cls(PortConstraintKind.RANGES, tuple(ranges))


class ProtocolSelectorKind(str, Enum):
    ANY = "Any"
    IP_PROTOCOL_NUMBER = "IpProtocolNumber"


@dataclass(frozen=True, slots=True)
class ProtocolSelector:
    kind: ProtocolSelectorKind
    number: int | None = None

    def __post_init__(self) -> None:
        if self.kind is ProtocolSelectorKind.ANY:
            if self.number is not None:
                raise ResolutionInvariantError(
                    "Any protocol cannot carry a number"
                )
            return
        if self.kind is ProtocolSelectorKind.IP_PROTOCOL_NUMBER:
            if (
                self.number is None
                or not isinstance(self.number, int)
                or isinstance(self.number, bool)
                or not 0 <= self.number <= 255
            ):
                raise ResolutionInvariantError(
                    "IP protocol number must be within 0..255"
                )
            return
        raise ResolutionInvariantError(
            "unsupported protocol selector kind"
        )

    @classmethod
    def any(cls) -> "ProtocolSelector":
        return cls(ProtocolSelectorKind.ANY)

    @classmethod
    def ip_protocol(cls, number: int) -> "ProtocolSelector":
        return cls(
            ProtocolSelectorKind.IP_PROTOCOL_NUMBER,
            number=number,
        )


@dataclass(frozen=True, slots=True)
class TechnicalAccessPredicate:
    source_addresses: AddressConstraint
    destination_addresses: AddressConstraint
    protocol: ProtocolSelector
    source_ports: PortConstraint
    destination_ports: PortConstraint

    def __post_init__(self) -> None:
        if self.protocol.kind is ProtocolSelectorKind.ANY and (
            self.source_ports.kind is not PortConstraintKind.ANY
            or self.destination_ports.kind is not PortConstraintKind.ANY
        ):
            raise ResolutionInvariantError(
                "Any protocol requires Any source and destination ports"
            )


class PortRegionKind(str, Enum):
    NUMERIC = "Numeric"
    NOT_APPLICABLE = "NotApplicable"


@dataclass(frozen=True, slots=True)
class PortRegion:
    kind: PortRegionKind
    first: int | None = None
    last: int | None = None

    def __post_init__(self) -> None:
        if self.kind is PortRegionKind.NOT_APPLICABLE:
            if self.first is not None or self.last is not None:
                raise ResolutionInvariantError(
                    "NotApplicable port region cannot carry bounds"
                )
            return
        if self.kind is PortRegionKind.NUMERIC:
            if (
                self.first is None
                or self.last is None
                or not 0 <= self.first <= self.last <= 65535
            ):
                raise ResolutionInvariantError(
                    "numeric port region requires "
                    "0 <= first <= last <= 65535"
                )
            return
        raise ResolutionInvariantError(
            "unsupported port region kind"
        )

    @classmethod
    def numeric(
        cls,
        first: int,
        last: int,
    ) -> "PortRegion":
        return cls(
            PortRegionKind.NUMERIC,
            first=first,
            last=last,
        )

    @classmethod
    def not_applicable(cls) -> "PortRegion":
        return cls(PortRegionKind.NOT_APPLICABLE)


@dataclass(frozen=True, slots=True)
class TechnicalRegionFragment:
    source_address: AddressRange
    destination_address: AddressRange
    protocol_number: int
    source_ports: PortRegion
    destination_ports: PortRegion

    def __post_init__(self) -> None:
        if (
            not isinstance(self.protocol_number, int)
            or isinstance(self.protocol_number, bool)
            or not 0 <= self.protocol_number <= 255
        ):
            raise ResolutionInvariantError(
                "fragment protocol number must be within 0..255"
            )


@dataclass(frozen=True, slots=True)
class DomainInteractionIdentity:
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    dcs_contract_revision_id: UUID


@dataclass(frozen=True, slots=True)
class DomainRegionProvenance:
    acc_references: tuple[str, ...]
    source_rc_references: tuple[str, ...]
    destination_rc_references: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name, values in (
            ("acc_references", self.acc_references),
            ("source_rc_references", self.source_rc_references),
            (
                "destination_rc_references",
                self.destination_rc_references,
            ),
        ):
            normalized = tuple(
                sorted(
                    {
                        _non_empty(
                            value,
                            field_name=field_name,
                        )
                        for value in values
                    }
                )
            )
            if not normalized:
                raise ResolutionInvariantError(
                    f"{field_name} must not be empty"
                )
            object.__setattr__(
                self,
                field_name,
                normalized,
            )

    def merged(
        self,
        other: "DomainRegionProvenance",
    ) -> "DomainRegionProvenance":
        return DomainRegionProvenance(
            acc_references=(
                self.acc_references
                + other.acc_references
            ),
            source_rc_references=(
                self.source_rc_references
                + other.source_rc_references
            ),
            destination_rc_references=(
                self.destination_rc_references
                + other.destination_rc_references
            ),
        )


@dataclass(frozen=True, slots=True)
class DomainInteractionRegion:
    interaction: DomainInteractionIdentity
    fragment: TechnicalRegionFragment
    provenance: DomainRegionProvenance


@dataclass(frozen=True, slots=True)
class KnowledgeGap:
    owner: str
    reason: str
    references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "owner",
            _non_empty(
                self.owner,
                field_name="knowledge gap owner",
            ),
        )
        object.__setattr__(
            self,
            "reason",
            _non_empty(
                self.reason,
                field_name="knowledge gap reason",
            ),
        )
        object.__setattr__(
            self,
            "references",
            tuple(
                sorted(
                    {
                        _non_empty(
                            value,
                            field_name="knowledge gap reference",
                        )
                        for value in self.references
                    }
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class DomainKnowledgeSnapshot:
    regions: tuple[DomainInteractionRegion, ...]
    knowledge_gaps: tuple[KnowledgeGap, ...] = ()
    complete_for_predicate: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "regions",
            tuple(self.regions),
        )
        object.__setattr__(
            self,
            "knowledge_gaps",
            tuple(self.knowledge_gaps),
        )
        if (
            self.complete_for_predicate
            and self.knowledge_gaps
        ):
            raise ResolutionInvariantError(
                "complete knowledge cannot carry "
                "predicate-relevant gaps"
            )


class AccessCorrespondence(str, Enum):
    EXACT = "Exact"
    COVERS = "Covers"
    COVERED_BY = "CoveredBy"
    PARTIAL_OVERLAP = "PartialOverlap"
    NONE = "None"


@dataclass(frozen=True, slots=True)
class DomainCorrespondence:
    interaction: DomainInteractionIdentity
    relation: AccessCorrespondence
    overlap: TechnicalRegionFragment
    domain_region: TechnicalRegionFragment
    provenance: DomainRegionProvenance


@dataclass(frozen=True, slots=True)
class AmbiguityWitness:
    overlap: TechnicalRegionFragment
    interactions: tuple[DomainInteractionIdentity, ...]

    def __post_init__(self) -> None:
        if len(set(self.interactions)) < 2:
            raise ResolutionInvariantError(
                "ambiguity requires at least "
                "two distinct interactions"
            )


class ResolutionStatus(str, Enum):
    EXACT = "Exact"
    COVERED = "Covered"
    PARTIAL = "Partial"
    AMBIGUOUS = "Ambiguous"
    UNRESOLVED = "Unresolved"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class InputProvenance:
    references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "references",
            tuple(
                sorted(
                    {
                        _non_empty(
                            value,
                            field_name="input provenance reference",
                        )
                        for value in self.references
                    }
                )
            ),
        )


@dataclass(frozen=True, slots=True)
class UnresolvedTechnicalRemainder:
    original_predicate: TechnicalAccessPredicate
    fragments: tuple[TechnicalRegionFragment, ...]
    complete: bool

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "fragments",
            tuple(self.fragments),
        )


@dataclass(frozen=True, slots=True)
class DomainAccessResolution:
    predicate: TechnicalAccessPredicate
    as_of: datetime
    status: ResolutionStatus
    correspondences: tuple[DomainCorrespondence, ...]
    ambiguities: tuple[AmbiguityWitness, ...]
    remainder: UnresolvedTechnicalRemainder
    knowledge_gaps: tuple[KnowledgeGap, ...]
    input_provenance: InputProvenance

    def __post_init__(self) -> None:
        require_aware(self.as_of)
        object.__setattr__(
            self,
            "correspondences",
            tuple(self.correspondences),
        )
        object.__setattr__(
            self,
            "ambiguities",
            tuple(self.ambiguities),
        )
        object.__setattr__(
            self,
            "knowledge_gaps",
            tuple(self.knowledge_gaps),
        )
