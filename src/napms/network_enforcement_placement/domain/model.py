from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from ipaddress import ip_address
from uuid import UUID


class PlacementInvariantError(Exception):
    """Raised when Network Enforcement Placement state is structurally invalid."""


def require_aware(value: datetime, *, field_name: str = "as_of") -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise PlacementInvariantError(f"{field_name} must be offset-aware")


def _non_empty(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise PlacementInvariantError(f"{field_name} must be non-empty")
    return normalized


def _normalize_references(
    values: tuple[str, ...],
    *,
    field_name: str,
) -> tuple[str, ...]:
    return tuple(
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


@dataclass(frozen=True, slots=True)
class TrafficRelation:
    source_ip: str
    destination_ip: str

    def __post_init__(self) -> None:
        try:
            source = ip_address(self.source_ip)
            destination = ip_address(self.destination_ip)
        except ValueError as exc:
            raise PlacementInvariantError(
                "traffic relation requires valid source and destination IP addresses"
            ) from exc
        object.__setattr__(self, "source_ip", str(source))
        object.__setattr__(self, "destination_ip", str(destination))


@dataclass(frozen=True, slots=True, order=True)
class ProviderRealizationReference:
    namespace: str
    reference: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "namespace",
            _non_empty(
                self.namespace,
                field_name="provider realization namespace",
            ),
        )
        object.__setattr__(
            self,
            "reference",
            _non_empty(
                self.reference,
                field_name="provider realization reference",
            ),
        )


@dataclass(frozen=True, slots=True, order=True)
class PathAttachmentReference:
    namespace: str
    reference: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "namespace",
            _non_empty(
                self.namespace,
                field_name="path attachment namespace",
            ),
        )
        object.__setattr__(
            self,
            "reference",
            _non_empty(
                self.reference,
                field_name="path attachment reference",
            ),
        )


@dataclass(frozen=True, slots=True)
class Provenance:
    references: tuple[str, ...]

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "references",
            _normalize_references(
                self.references,
                field_name="provenance reference",
            ),
        )

    def merged(
        self,
        other: "Provenance",
    ) -> "Provenance":
        return Provenance(
            self.references + other.references
        )


@dataclass(frozen=True, slots=True)
class InputProvenance:
    references: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "references",
            _normalize_references(
                self.references,
                field_name="input provenance reference",
            ),
        )


@dataclass(frozen=True, slots=True)
class EffectiveWindow:
    valid_from: datetime
    valid_until: datetime | None = None

    def __post_init__(self) -> None:
        require_aware(
            self.valid_from,
            field_name="valid_from",
        )
        if self.valid_until is not None:
            require_aware(
                self.valid_until,
                field_name="valid_until",
            )
            if self.valid_from >= self.valid_until:
                raise PlacementInvariantError(
                    "effective window requires valid_from < valid_until"
                )

    def contains(self, as_of: datetime) -> bool:
        require_aware(as_of)
        return self.valid_from <= as_of and (
            self.valid_until is None
            or as_of < self.valid_until
        )


@dataclass(frozen=True, slots=True)
class LogicalFirewall:
    logical_firewall_id: UUID
    validity: EffectiveWindow
    provenance: Provenance


@dataclass(frozen=True, slots=True)
class LogicalFirewallCorrespondence:
    logical_firewall_id: UUID
    provider_realization: ProviderRealizationReference
    validity: EffectiveWindow
    provenance: Provenance


@dataclass(frozen=True, slots=True)
class EnforcementAttachment:
    enforcement_attachment_id: UUID
    logical_firewall_id: UUID
    provider_realization: ProviderRealizationReference
    path_attachment: PathAttachmentReference
    validity: EffectiveWindow
    provenance: Provenance


@dataclass(frozen=True, slots=True)
class TraversalPoint:
    provider_realization: ProviderRealizationReference
    path_attachment: PathAttachmentReference
    provenance: Provenance


@dataclass(frozen=True, slots=True)
class ForwardingPath:
    path_reference: str
    traversal_points: tuple[TraversalPoint, ...]
    validity: EffectiveWindow
    provenance: Provenance

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "path_reference",
            _non_empty(
                self.path_reference,
                field_name="path reference",
            ),
        )
        object.__setattr__(
            self,
            "traversal_points",
            tuple(self.traversal_points),
        )


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
            _normalize_references(
                self.references,
                field_name="knowledge gap reference",
            ),
        )


@dataclass(frozen=True, slots=True)
class PlacementKnowledgeSnapshot:
    path: ForwardingPath | None = None
    no_forwarding_path: bool = False
    logical_firewalls: tuple[LogicalFirewall, ...] = ()
    correspondences: tuple[LogicalFirewallCorrespondence, ...] = ()
    attachments: tuple[EnforcementAttachment, ...] = ()
    complete_for_pair: bool = True
    complete_for_attachments: bool = True
    knowledge_gaps: tuple[KnowledgeGap, ...] = ()

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "logical_firewalls",
            tuple(self.logical_firewalls),
        )
        object.__setattr__(
            self,
            "correspondences",
            tuple(self.correspondences),
        )
        object.__setattr__(
            self,
            "attachments",
            tuple(self.attachments),
        )
        object.__setattr__(
            self,
            "knowledge_gaps",
            tuple(self.knowledge_gaps),
        )

        if (
            self.path is not None
            and self.no_forwarding_path
        ):
            raise PlacementInvariantError(
                "path and no_forwarding_path are mutually exclusive"
            )
        if (
            self.no_forwarding_path
            and not self.complete_for_pair
        ):
            raise PlacementInvariantError(
                "NoForwardingPath requires complete endpoint-pair knowledge"
            )
        if (
            self.path is None
            and not self.no_forwarding_path
            and self.complete_for_pair
        ):
            raise PlacementInvariantError(
                "complete endpoint-pair knowledge requires a path or NoForwardingPath"
            )
        if (
            self.complete_for_pair
            and self.complete_for_attachments
            and self.knowledge_gaps
        ):
            raise PlacementInvariantError(
                "fully complete placement knowledge cannot carry relevant gaps"
            )

        firewall_ids = [
            item.logical_firewall_id
            for item in self.logical_firewalls
        ]
        if len(firewall_ids) != len(set(firewall_ids)):
            raise PlacementInvariantError(
                "effective snapshot requires unique Logical Firewall identities"
            )

        attachment_ids = [
            item.enforcement_attachment_id
            for item in self.attachments
        ]
        if len(attachment_ids) != len(
            set(attachment_ids)
        ):
            raise PlacementInvariantError(
                "effective snapshot requires unique Enforcement Attachment identities"
            )

        correspondence_keys = [
            (
                item.logical_firewall_id,
                item.provider_realization,
            )
            for item in self.correspondences
        ]
        if len(correspondence_keys) != len(
            set(correspondence_keys)
        ):
            raise PlacementInvariantError(
                "effective snapshot requires unique Logical Firewall/provider correspondences"
            )


class SelectionStatus(str, Enum):
    PLACED = "Placed"
    NO_ENFORCEMENT = "NoEnforcement"
    NO_FORWARDING_PATH = "NoForwardingPath"
    AMBIGUOUS = "Ambiguous"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class PlacementProvenance:
    path_references: tuple[str, ...]
    logical_firewall_references: tuple[str, ...]
    correspondence_references: tuple[str, ...]
    attachment_references: tuple[str, ...]

    def __post_init__(self) -> None:
        for field_name in (
            "path_references",
            "logical_firewall_references",
            "correspondence_references",
            "attachment_references",
        ):
            object.__setattr__(
                self,
                field_name,
                _normalize_references(
                    getattr(self, field_name),
                    field_name=field_name,
                ),
            )


@dataclass(frozen=True, slots=True)
class EnforcementPlacement:
    logical_firewall_id: UUID
    enforcement_attachment_id: UUID
    provider_realization: ProviderRealizationReference
    path_attachment: PathAttachmentReference
    traversal_position: int
    provenance: PlacementProvenance

    def __post_init__(self) -> None:
        if (
            not isinstance(
                self.traversal_position,
                int,
            )
            or isinstance(
                self.traversal_position,
                bool,
            )
            or self.traversal_position < 0
        ):
            raise PlacementInvariantError(
                "traversal_position must be a non-negative integer"
            )


@dataclass(frozen=True, slots=True)
class PlacementAmbiguity:
    traversal_position: int
    provider_realization: ProviderRealizationReference
    path_attachment: PathAttachmentReference
    logical_firewall_ids: tuple[UUID, ...]

    def __post_init__(self) -> None:
        unique = tuple(
            sorted(
                set(self.logical_firewall_ids),
                key=str,
            )
        )
        if len(unique) < 2:
            raise PlacementInvariantError(
                "placement ambiguity requires at least two Logical Firewalls"
            )
        object.__setattr__(
            self,
            "logical_firewall_ids",
            unique,
        )


@dataclass(frozen=True, slots=True)
class EnforcementSelection:
    relation: TrafficRelation
    as_of: datetime
    status: SelectionStatus
    path_reference: str | None
    placements: tuple[EnforcementPlacement, ...]
    ambiguities: tuple[PlacementAmbiguity, ...]
    knowledge_gaps: tuple[KnowledgeGap, ...]
    input_provenance: InputProvenance
    complete: bool

    def __post_init__(self) -> None:
        require_aware(self.as_of)
        object.__setattr__(
            self,
            "placements",
            tuple(self.placements),
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
        if (
            self.status is SelectionStatus.UNKNOWN
            and self.complete
        ):
            raise PlacementInvariantError(
                "Unknown selection cannot be complete"
            )
        if (
            self.status is not SelectionStatus.UNKNOWN
            and not self.complete
        ):
            raise PlacementInvariantError(
                "non-Unknown selection must be complete under the first-slice model"
            )
