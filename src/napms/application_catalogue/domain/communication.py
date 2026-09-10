from dataclasses import dataclass
from enum import Enum

from .model import CatalogueInvariantError


@dataclass(frozen=True, slots=True, order=True)
class DcsPortRange:
    first: int
    last: int

    def __post_init__(self) -> None:
        if not (0 <= self.first <= 65535 and 0 <= self.last <= 65535):
            raise CatalogueInvariantError("port range boundaries must be within 0..65535")
        if self.first > self.last:
            raise CatalogueInvariantError("port range requires first <= last")


class DcsPortConstraintKind(str, Enum):
    NOT_APPLICABLE = "NotApplicable"
    ANY = "Any"
    RANGES = "Ranges"


@dataclass(frozen=True, slots=True)
class DcsPortConstraint:
    kind: DcsPortConstraintKind
    ranges: tuple[DcsPortRange, ...] = ()

    def __post_init__(self) -> None:
        if self.kind is not DcsPortConstraintKind.RANGES:
            if self.ranges:
                raise CatalogueInvariantError(
                    "Any/NotApplicable port constraints cannot carry ranges"
                )
            return

        if not self.ranges:
            raise CatalogueInvariantError(
                "Ranges port constraint requires at least one range"
            )

        ordered = sorted(self.ranges)
        canonical: list[DcsPortRange] = []
        for current in ordered:
            if not canonical:
                canonical.append(current)
                continue
            previous = canonical[-1]
            if current.first <= previous.last + 1:
                canonical[-1] = DcsPortRange(
                    previous.first,
                    max(previous.last, current.last),
                )
            else:
                canonical.append(current)
        object.__setattr__(self, "ranges", tuple(canonical))

    @classmethod
    def not_applicable(cls) -> "DcsPortConstraint":
        return cls(DcsPortConstraintKind.NOT_APPLICABLE)

    @classmethod
    def any(cls) -> "DcsPortConstraint":
        return cls(DcsPortConstraintKind.ANY)

    @classmethod
    def ranged(cls, *ranges: DcsPortRange) -> "DcsPortConstraint":
        return cls(DcsPortConstraintKind.RANGES, tuple(ranges))


@dataclass(frozen=True, slots=True)
class AuthoredDcsTrafficAlternative:
    protocol: str
    source_ports: DcsPortConstraint
    destination_ports: DcsPortConstraint
    service_reference: str | None = None

    def __post_init__(self) -> None:
        protocol = self.protocol.strip().lower() if self.protocol else ""
        if not protocol:
            raise CatalogueInvariantError("protocol must be a non-empty token")
        object.__setattr__(self, "protocol", protocol)

        if self.service_reference is not None:
            service_reference = self.service_reference.strip()
            if not service_reference:
                raise CatalogueInvariantError(
                    "service_reference must be non-empty when present"
                )
            object.__setattr__(self, "service_reference", service_reference)


def alternative_sort_key(value: AuthoredDcsTrafficAlternative):
    def constraint_key(constraint: DcsPortConstraint):
        return (
            constraint.kind.value,
            tuple((item.first, item.last) for item in constraint.ranges),
        )

    return (
        value.protocol,
        constraint_key(value.source_ports),
        constraint_key(value.destination_ports),
        value.service_reference or "",
    )


def canonical_dcs_alternatives(
    alternatives: tuple[AuthoredDcsTrafficAlternative, ...],
) -> tuple[AuthoredDcsTrafficAlternative, ...]:
    if not alternatives:
        raise CatalogueInvariantError(
            "DCS revision requires at least one traffic alternative"
        )
    if len(set(alternatives)) != len(alternatives):
        raise CatalogueInvariantError(
            "duplicate DCS traffic alternatives are not allowed"
        )
    return tuple(sorted(alternatives, key=alternative_sort_key))
