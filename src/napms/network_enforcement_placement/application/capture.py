from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from napms.network_enforcement_placement.domain.model import (
    EffectiveWindow,
    PlacementInvariantError,
    PlacementKnowledgeSnapshot,
    TrafficRelation,
    require_aware,
)


def _non_empty(
    value: str,
    *,
    field_name: str,
) -> str:
    normalized = value.strip()
    if not normalized:
        raise PlacementInvariantError(
            f"{field_name} must be non-empty"
        )
    return normalized


@dataclass(frozen=True, slots=True)
class KnowledgeSourceReference:
    namespace: str
    reference: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "namespace",
            _non_empty(
                self.namespace,
                field_name="knowledge source namespace",
            ),
        )
        object.__setattr__(
            self,
            "reference",
            _non_empty(
                self.reference,
                field_name="knowledge source reference",
            ),
        )


@dataclass(frozen=True, slots=True)
class SourceCaptureReference:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _non_empty(
                self.value,
                field_name="source capture reference",
            ),
        )


@dataclass(frozen=True, slots=True)
class PlacementKnowledgeCapture:
    source: KnowledgeSourceReference
    source_capture_reference: SourceCaptureReference
    relation: TrafficRelation
    validity: EffectiveWindow
    knowledge: PlacementKnowledgeSnapshot

    def __post_init__(self) -> None:
        if (
            self.knowledge.path is not None
            and self.knowledge.path.validity
            != self.validity
        ):
            raise PlacementInvariantError(
                "capture validity must equal forwarding-path validity"
            )
        if (
            self.knowledge.no_forwarding_path
            is not None
            and self.knowledge.no_forwarding_path.validity
            != self.validity
        ):
            raise PlacementInvariantError(
                "capture validity must equal NoForwardingPath validity"
            )


@dataclass(frozen=True, slots=True)
class PersistedPlacementKnowledgeCapture:
    capture_id: UUID
    recorded_at: datetime
    payload: PlacementKnowledgeCapture

    def __post_init__(self) -> None:
        require_aware(
            self.recorded_at,
            field_name="recorded_at",
        )

    def matches(
        self,
        capture: PlacementKnowledgeCapture,
    ) -> bool:
        return self.payload == capture
