from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class ScopedConnectivityInventoryInvariantError(Exception):
    """Raised when Scoped Connectivity Inventory input is structurally invalid."""


def require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ScopedConnectivityInventoryInvariantError(
            f"{field_name} must be offset-aware"
        )


@dataclass(frozen=True, slots=True, order=True)
class InteractionIdentity:
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    dcs_contract_revision_id: UUID


class Direction(str, Enum):
    OUTGOING = "Outgoing"
    INCOMING = "Incoming"


@dataclass(frozen=True, slots=True, order=True)
class EndpointSnapshot:
    endpoint_reference: str
    technical_address: str

    def __post_init__(self) -> None:
        if not self.endpoint_reference:
            raise ScopedConnectivityInventoryInvariantError(
                "endpoint_reference must be non-empty"
            )
        if not self.technical_address:
            raise ScopedConnectivityInventoryInvariantError(
                "technical_address must be non-empty"
            )


class RealizationState(str, Enum):
    RESOLVED = "Resolved"
    UNRESOLVED = "Unresolved"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class ResourceSnapshot:
    resource_reference: str
    endpoints: tuple[EndpointSnapshot, ...]
    realization_state: RealizationState

    def __post_init__(self) -> None:
        if not self.resource_reference:
            raise ScopedConnectivityInventoryInvariantError(
                "resource_reference must be non-empty"
            )


@dataclass(frozen=True, slots=True)
class BoundComponentSnapshot:
    resource_reference: str
    component_deployment_id: UUID
    display_name: str | None = None


@dataclass(frozen=True, slots=True)
class InteractionSnapshot:
    identity: InteractionIdentity
    source_display_name: str | None
    destination_display_name: str | None
    dcs_display_name: str | None
    access_summary: str | None = None


@dataclass(frozen=True, slots=True)
class ComponentResourceBindingSnapshot:
    component_deployment_id: UUID
    resource_reference: str

    def __post_init__(self) -> None:
        if not self.resource_reference:
            raise ScopedConnectivityInventoryInvariantError(
                "resource_reference must be non-empty"
            )


class RequirementCurrent(str, Enum):
    REQUIRED = "Required"
    NONE = "None"
    UNKNOWN = "Unknown"


class CoverageSummary(str, Enum):
    COVERED = "Covered"
    UNCOVERED = "Uncovered"
    NOT_CURRENT = "NotCurrent"
    UNKNOWN = "Unknown"
    NOT_APPLICABLE = "NotApplicable"


@dataclass(frozen=True, slots=True)
class RequirementSummary:
    identity: InteractionIdentity
    current: RequirementCurrent
    historical_only: bool | None
    coverage: CoverageSummary


class DecisionSummaryState(str, Enum):
    ALLOWED = "Allowed"
    NOT_ALLOWED = "NotAllowed"
    NO_FINAL_DECISION = "NoFinalDecision"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class DecisionSummary:
    identity: InteractionIdentity
    state: DecisionSummaryState


class RuleExists(str, Enum):
    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"


class PolicyOperationalState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"
    UNAVAILABLE = "Unavailable"


class EffectiveAtAsOf(str, Enum):
    YES = "Yes"
    NO = "No"
    UNKNOWN = "Unknown"
    UNAVAILABLE = "Unavailable"


@dataclass(frozen=True, slots=True)
class PolicySummary:
    identity: InteractionIdentity
    rule_exists: RuleExists
    operational_state: PolicyOperationalState
    effective_at_as_of: EffectiveAtAsOf


@dataclass(frozen=True, slots=True)
class ConnectivityRelationshipItem:
    identity: InteractionIdentity
    direction: Direction
    remote_component_deployment_id: UUID
    remote_component_display_name: str | None
    dcs_display_name: str | None
    access_summary: str | None
    remote_resources: tuple[ResourceSnapshot, ...]
    remote_resources_known: bool
    requirement: RequirementSummary
    decision: DecisionSummary
    policy: PolicySummary


@dataclass(frozen=True, slots=True)
class ComponentInventoryItem:
    component_deployment_id: UUID
    display_name: str | None
    relationships: tuple[ConnectivityRelationshipItem, ...]
    relationships_known: bool


@dataclass(frozen=True, slots=True)
class ResourceInventoryItem:
    resource: ResourceSnapshot
    components: tuple[ComponentInventoryItem, ...]
    components_known: bool


@dataclass(frozen=True, slots=True)
class ScopedConnectivityInventoryPage:
    scope: str
    as_of: datetime
    items: tuple[ResourceInventoryItem, ...]
    page: int
    page_size: int
    has_more: bool
    partial: bool
    read_authority_reference: str

    def __post_init__(self) -> None:
        if not self.scope:
            raise ScopedConnectivityInventoryInvariantError(
                "scope must be non-empty"
            )
        if not self.read_authority_reference:
            raise ScopedConnectivityInventoryInvariantError(
                "read_authority_reference must be non-empty"
            )
        require_aware(self.as_of, field_name="as_of")
