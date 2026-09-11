from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class TrafficAnalysisInvariantError(Exception):
    pass


def require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise TrafficAnalysisInvariantError("as_of must be offset-aware")


class ResolutionState(str, Enum):
    RESOLVED = "Resolved"
    AMBIGUOUS = "Ambiguous"
    UNKNOWN = "Unknown"
    HISTORICAL = "Historical"


class RuleMatchKind(str, Enum):
    EXACT = "Exact"
    COVERS_QUERY = "CoversQuery"
    COVERED_BY_QUERY = "CoveredByQuery"
    OVERLAP = "Overlap"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class TrafficAnalysisQuery:
    source_address: str
    destination_address: str
    protocol: str
    destination_port_first: int
    destination_port_last: int
    as_of: datetime

    def __post_init__(self) -> None:
        for field_name, value in (
            ("source_address", self.source_address),
            ("destination_address", self.destination_address),
            ("protocol", self.protocol),
        ):
            if not value or not value.strip():
                raise TrafficAnalysisInvariantError(f"{field_name} must be non-empty")
        if not 0 <= self.destination_port_first <= self.destination_port_last <= 65535:
            raise TrafficAnalysisInvariantError("destination port range must be within 0..65535")
        require_aware(self.as_of)


@dataclass(frozen=True, slots=True)
class ResolvedResource:
    resource_reference: str
    endpoint_reference: str
    technical_address: str
    component_names: tuple[str, ...] = ()
    responsibility_scope: str | None = None
    provenance_references: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class EndpointResolution:
    state: ResolutionState
    address: str
    resources: tuple[ResolvedResource, ...] = ()


@dataclass(frozen=True, slots=True)
class ResponsibilityItem:
    resource_reference: str
    role: str
    party_reference: str
    party_kind: str
    display_name: str
    contact: str | None
    provenance_reference: str


@dataclass(frozen=True, slots=True)
class PolicyMatch:
    source_component: str | None
    destination_component: str | None
    dcs_reference: str | None
    dcs_display_name: str | None
    access_summary: str | None
    requirement: str
    decision: str
    rule: str
    effective: str
    scope: str | None
    partial: bool = False


@dataclass(frozen=True, slots=True)
class TechnicalRuleMatch:
    entry_reference: str
    action: str
    normalized: str
    match_kind: RuleMatchKind


@dataclass(frozen=True, slots=True)
class EvidenceSnapshot:
    evidence_set_reference: str
    source_reference: str
    source_scope_reference: str
    captured_at: datetime | None
    recorded_at: datetime
    provenance_references: tuple[str, ...]
    matches: tuple[TechnicalRuleMatch, ...]


@dataclass(frozen=True, slots=True)
class NetworkCandidateView:
    provider_namespace: str
    device_reference: str
    logical_firewall_reference: str | None
    enforcement_attachment_reference: str | None
    path_attachment_reference: str | None
    source_relevance: str | None
    provenance_references: tuple[str, ...]
    evidence: EvidenceSnapshot | None = None


@dataclass(frozen=True, slots=True)
class NetworkContextView:
    candidates: tuple[NetworkCandidateView, ...]
    complete_for_pair: bool
    knowledge_gaps: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class TrafficAnalysisResult:
    query: TrafficAnalysisQuery
    source: EndpointResolution
    destination: EndpointResolution
    policy_matches: tuple[PolicyMatch, ...]
    source_responsibilities: tuple[ResponsibilityItem, ...]
    destination_responsibilities: tuple[ResponsibilityItem, ...]
    network_context: NetworkContextView
    findings: tuple[str, ...]
