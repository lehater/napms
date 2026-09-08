from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.access_policy.domain.model import (
    EffectiveWindow,
    OperationalState,
    RuleSemanticIdentity,
)
from napms.policy_export.application.ports import ResourceReference


class NormalizationInvariantError(Exception):
    """The captured snapshot or decoded semantics cannot be normalized truthfully."""


@dataclass(frozen=True, slots=True, order=True)
class PortRange:
    first: int
    last: int

    def __post_init__(self) -> None:
        if not (0 <= self.first <= 65535 and 0 <= self.last <= 65535):
            raise NormalizationInvariantError("port range boundaries must be within 0..65535")
        if self.first > self.last:
            raise NormalizationInvariantError("port range requires first <= last")


class PortConstraintKind(str, Enum):
    NOT_APPLICABLE = "NotApplicable"
    ANY = "Any"
    RANGES = "Ranges"


@dataclass(frozen=True, slots=True)
class PortConstraint:
    kind: PortConstraintKind
    ranges: tuple[PortRange, ...] = ()

    def __post_init__(self) -> None:
        if self.kind is not PortConstraintKind.RANGES:
            if self.ranges:
                raise NormalizationInvariantError(
                    "Any/NotApplicable port constraints cannot carry ranges"
                )
            return

        if not self.ranges:
            raise NormalizationInvariantError("Ranges constraint requires at least one range")

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


@dataclass(frozen=True, slots=True)
class DcsTrafficAlternative:
    protocol: str
    source_ports: PortConstraint
    destination_ports: PortConstraint
    service_reference: str | None = None

    def __post_init__(self) -> None:
        if not self.protocol or self.protocol != self.protocol.strip():
            raise NormalizationInvariantError(
                "protocol must be a non-empty canonical token"
            )
        if self.service_reference is not None and not self.service_reference:
            raise NormalizationInvariantError(
                "service_reference must be non-empty when present"
            )


@dataclass(frozen=True, slots=True)
class NormalizedPolicyRow:
    rule_id: UUID
    rule_semantic_identity: RuleSemanticIdentity
    decision_reference: str | None
    rule_governance_scope: str
    rule_operational_state: OperationalState
    rule_effective_window: EffectiveWindow | None
    snapshot_as_of: datetime
    read_authority_reference: str

    source_resource_reference: ResourceReference
    source_endpoint_reference: str
    source_technical_address: str
    source_fact_reference: str
    source_validity_reference: str
    source_provenance_reference: str

    destination_resource_reference: ResourceReference
    destination_endpoint_reference: str
    destination_technical_address: str
    destination_fact_reference: str
    destination_validity_reference: str
    destination_provenance_reference: str

    protocol: str
    source_ports: PortConstraint
    destination_ports: PortConstraint
    service_reference: str | None

    acc_fact_reference: str
    acc_validity_reference: str
    acc_provenance_reference: str


@dataclass(frozen=True, slots=True)
class SuccessfulNormalizedPolicyExport:
    scope: str
    as_of: datetime
    authority_reference: str
    rows: tuple[NormalizedPolicyRow, ...]
