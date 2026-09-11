from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from ipaddress import ip_address
from uuid import UUID


class EvidenceInvariantError(Exception):
    """Raised when Technical Access Evidence state is structurally invalid."""


def _require_non_empty(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise EvidenceInvariantError(f"{field_name} must be non-empty")
    return normalized


def _require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise EvidenceInvariantError(f"{field_name} must be offset-aware")


@dataclass(frozen=True, slots=True)
class EvidenceSourceReference:
    namespace: str
    reference: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "namespace",
            _require_non_empty(self.namespace, field_name="source namespace"),
        )
        object.__setattr__(
            self,
            "reference",
            _require_non_empty(self.reference, field_name="source reference"),
        )


@dataclass(frozen=True, slots=True)
class SourceScopeReference:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_non_empty(self.value, field_name="source scope reference"),
        )


@dataclass(frozen=True, slots=True)
class SourceCaptureReference:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_non_empty(self.value, field_name="source capture reference"),
        )


class EvidenceKind(str, Enum):
    CONFIGURED = "Configured"
    TRAFFIC_DERIVED = "TrafficDerived"
    IMPORTED = "Imported"


class EvidenceTimeKind(str, Enum):
    UNKNOWN = "Unknown"
    INSTANT = "Instant"
    WINDOW = "Window"


@dataclass(frozen=True, slots=True)
class EvidenceTime:
    kind: EvidenceTimeKind
    at: datetime | None = None
    start: datetime | None = None
    end: datetime | None = None

    def __post_init__(self) -> None:
        if self.kind is EvidenceTimeKind.UNKNOWN:
            if self.at is not None or self.start is not None or self.end is not None:
                raise EvidenceInvariantError("Unknown evidence time cannot carry instants")
            return
        if self.kind is EvidenceTimeKind.INSTANT:
            if self.at is None or self.start is not None or self.end is not None:
                raise EvidenceInvariantError("Instant evidence time requires only at")
            _require_aware(self.at, field_name="evidence time at")
            return
        if self.kind is EvidenceTimeKind.WINDOW:
            if self.at is not None or self.start is None or self.end is None:
                raise EvidenceInvariantError("Window evidence time requires start and end")
            _require_aware(self.start, field_name="evidence time start")
            _require_aware(self.end, field_name="evidence time end")
            if self.start >= self.end:
                raise EvidenceInvariantError("evidence time window requires start < end")
            return
        raise EvidenceInvariantError("unsupported evidence time kind")

    @classmethod
    def unknown(cls) -> "EvidenceTime":
        return cls(EvidenceTimeKind.UNKNOWN)

    @classmethod
    def instant(cls, at: datetime) -> "EvidenceTime":
        return cls(EvidenceTimeKind.INSTANT, at=at)

    @classmethod
    def window(cls, start: datetime, end: datetime) -> "EvidenceTime":
        return cls(EvidenceTimeKind.WINDOW, start=start, end=end)


@dataclass(frozen=True, slots=True)
class AddressRange:
    first: str
    last: str

    def __post_init__(self) -> None:
        try:
            first = ip_address(self.first)
            last = ip_address(self.last)
        except ValueError as exc:
            raise EvidenceInvariantError(
                "address range requires valid IP addresses"
            ) from exc
        if first.version != last.version:
            raise EvidenceInvariantError("address range cannot cross IP families")
        if int(first) > int(last):
            raise EvidenceInvariantError("address range requires first <= last")
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
                raise EvidenceInvariantError(
                    "Any address constraint cannot carry ranges"
                )
            return
        if self.kind is not AddressConstraintKind.RANGES:
            raise EvidenceInvariantError("unsupported address constraint kind")
        if not self.ranges:
            raise EvidenceInvariantError("Ranges address constraint requires ranges")

        ordered = sorted(
            self.ranges,
            key=lambda item: (item.version, item.first_int, item.last_int),
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
                last = (
                    previous.last
                    if previous.last_int >= current.last_int
                    else current.last
                )
                canonical[-1] = AddressRange(previous.first, last)
            else:
                canonical.append(current)
        object.__setattr__(self, "ranges", tuple(canonical))

    @classmethod
    def any(cls) -> "AddressConstraint":
        return cls(AddressConstraintKind.ANY)

    @classmethod
    def ranged(cls, *ranges: AddressRange) -> "AddressConstraint":
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
        ):
            raise EvidenceInvariantError("port boundaries must be integers")
        if not (0 <= self.first <= 65535 and 0 <= self.last <= 65535):
            raise EvidenceInvariantError(
                "port range boundaries must be within 0..65535"
            )
        if self.first > self.last:
            raise EvidenceInvariantError("port range requires first <= last")


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
                raise EvidenceInvariantError(
                    "Any/NotApplicable port constraints cannot carry ranges"
                )
            return
        if self.kind is not PortConstraintKind.RANGES:
            raise EvidenceInvariantError("unsupported port constraint kind")
        if not self.ranges:
            raise EvidenceInvariantError("Ranges port constraint requires ranges")

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
    def ranged(cls, *ranges: PortRange) -> "PortConstraint":
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
                raise EvidenceInvariantError("Any protocol cannot carry a number")
            return
        if self.kind is ProtocolSelectorKind.IP_PROTOCOL_NUMBER:
            if (
                self.number is None
                or not isinstance(self.number, int)
                or isinstance(self.number, bool)
                or not 0 <= self.number <= 255
            ):
                raise EvidenceInvariantError(
                    "IP protocol number must be within 0..255"
                )
            return
        raise EvidenceInvariantError("unsupported protocol selector kind")

    @classmethod
    def any(cls) -> "ProtocolSelector":
        return cls(ProtocolSelectorKind.ANY)

    @classmethod
    def ip_protocol(cls, number: int) -> "ProtocolSelector":
        return cls(ProtocolSelectorKind.IP_PROTOCOL_NUMBER, number=number)


class EvidenceAction(str, Enum):
    PERMIT = "Permit"
    BLOCK = "Block"


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
            raise EvidenceInvariantError(
                "Any protocol requires Any source and destination ports"
            )


@dataclass(frozen=True, slots=True)
class TechnicalAccessEntryPayload:
    predicate: TechnicalAccessPredicate
    action: EvidenceAction | None = None
    source_entry_reference: str | None = None
    source_position: int | None = None

    def __post_init__(self) -> None:
        if self.action is not None and not isinstance(
            self.action,
            EvidenceAction,
        ):
            raise EvidenceInvariantError("unsupported evidence action")
        if self.source_entry_reference is not None:
            object.__setattr__(
                self,
                "source_entry_reference",
                _require_non_empty(
                    self.source_entry_reference,
                    field_name="source entry reference",
                ),
            )
        if self.source_position is not None and (
            not isinstance(self.source_position, int)
            or isinstance(self.source_position, bool)
            or self.source_position < 0
        ):
            raise EvidenceInvariantError(
                "source position must be a non-negative integer"
            )


@dataclass(frozen=True, slots=True)
class TechnicalAccessEntry:
    evidence_entry_id: UUID
    payload: TechnicalAccessEntryPayload


@dataclass(frozen=True, slots=True)
class TechnicalAccessEvidenceCapturePayload:
    kind: EvidenceKind
    source_scope: SourceScopeReference
    evidence_time: EvidenceTime
    entries: tuple[TechnicalAccessEntryPayload, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.kind, EvidenceKind):
            raise EvidenceInvariantError("unsupported evidence kind")
        object.__setattr__(self, "entries", tuple(self.entries))

    def is_equivalent_to(
        self,
        other: "TechnicalAccessEvidenceCapturePayload",
    ) -> bool:
        return (
            self.kind is other.kind
            and self.source_scope == other.source_scope
            and self.evidence_time == other.evidence_time
            and Counter(self.entries) == Counter(other.entries)
        )


@dataclass(frozen=True, slots=True)
class TechnicalAccessEvidenceSet:
    evidence_set_id: UUID
    kind: EvidenceKind
    source: EvidenceSourceReference
    source_scope: SourceScopeReference
    source_capture_reference: SourceCaptureReference
    evidence_time: EvidenceTime
    recorded_at: datetime
    entries: tuple[TechnicalAccessEntry, ...]

    def __post_init__(self) -> None:
        if not isinstance(self.kind, EvidenceKind):
            raise EvidenceInvariantError("unsupported evidence kind")
        _require_aware(self.recorded_at, field_name="recorded_at")
        object.__setattr__(self, "entries", tuple(self.entries))
        ids = tuple(entry.evidence_entry_id for entry in self.entries)
        if len(ids) != len(set(ids)):
            raise EvidenceInvariantError(
                "evidence entry IDs must be unique within a set"
            )

    @property
    def capture_payload(self) -> TechnicalAccessEvidenceCapturePayload:
        return TechnicalAccessEvidenceCapturePayload(
            kind=self.kind,
            source_scope=self.source_scope,
            evidence_time=self.evidence_time,
            entries=tuple(entry.payload for entry in self.entries),
        )

    def matches_capture(
        self,
        *,
        source: EvidenceSourceReference,
        source_capture_reference: SourceCaptureReference,
        payload: TechnicalAccessEvidenceCapturePayload,
    ) -> bool:
        return (
            self.source == source
            and self.source_capture_reference == source_capture_reference
            and self.capture_payload.is_equivalent_to(payload)
        )
