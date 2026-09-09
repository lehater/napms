from datetime import datetime
from typing import Protocol

from napms.network_enforcement_placement.application.capture import (
    KnowledgeSourceReference,
    PersistedPlacementKnowledgeCapture,
    SourceCaptureReference,
)
from napms.network_enforcement_placement.domain.model import (
    PlacementKnowledgeSnapshot,
    TrafficRelation,
)


class PlacementPersistenceError(Exception):
    """NEP persistence failed without a trustworthy semantic result."""


class PlacementCommitOutcomeUnknown(
    PlacementPersistenceError
):
    """Commit acknowledgement is unknown; success cannot be claimed."""


class PlacementCaptureConflict(
    PlacementPersistenceError
):
    """The same source/capture identity already exists."""


class PlacementKnowledgePort(Protocol):
    def load_for(
        self,
        *,
        relation: TrafficRelation,
        as_of: datetime,
    ) -> PlacementKnowledgeSnapshot: ...


class PlacementKnowledgeCaptureRepository(
    PlacementKnowledgePort,
    Protocol,
):
    def find_by_capture(
        self,
        *,
        source: KnowledgeSourceReference,
        source_capture_reference: SourceCaptureReference,
    ) -> PersistedPlacementKnowledgeCapture | None: ...

    def add(
        self,
        capture: PersistedPlacementKnowledgeCapture,
    ) -> None: ...

    def commit(self) -> None: ...
