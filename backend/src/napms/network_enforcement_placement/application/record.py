from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable
from uuid import UUID, uuid4

from napms.network_enforcement_placement.application.capture import (
    PersistedPlacementKnowledgeCapture,
    PlacementKnowledgeCapture,
)
from napms.network_enforcement_placement.application.ports import (
    PlacementCaptureConflict,
    PlacementKnowledgeCaptureRepository,
)


class RecordPlacementKnowledgeOutcome(
    str,
    Enum,
):
    RECORDED = "Recorded"
    RESOLVED = "Resolved"
    CAPTURE_CONFLICT = "CaptureConflict"


@dataclass(frozen=True, slots=True)
class RecordPlacementKnowledgeResult:
    outcome: RecordPlacementKnowledgeOutcome
    capture: (
        PersistedPlacementKnowledgeCapture
        | None
    ) = None


class RecordPlacementKnowledge:
    def __init__(
        self,
        *,
        captures: PlacementKnowledgeCaptureRepository,
        capture_id_factory: Callable[
            [], UUID
        ] = uuid4,
        clock: Callable[
            [], datetime
        ] = lambda: datetime.now(
            timezone.utc
        ),
    ) -> None:
        self._captures = captures
        self._capture_id_factory = (
            capture_id_factory
        )
        self._clock = clock

    def execute(
        self,
        command: PlacementKnowledgeCapture,
    ) -> RecordPlacementKnowledgeResult:
        existing = (
            self._captures.find_by_capture(
                source=command.source,
                source_capture_reference=(
                    command
                    .source_capture_reference
                ),
            )
        )
        if existing is not None:
            if existing.matches(command):
                return (
                    RecordPlacementKnowledgeResult(
                        RecordPlacementKnowledgeOutcome.RESOLVED,
                        existing,
                    )
                )
            return RecordPlacementKnowledgeResult(
                RecordPlacementKnowledgeOutcome.CAPTURE_CONFLICT
            )

        persisted = (
            PersistedPlacementKnowledgeCapture(
                capture_id=(
                    self._capture_id_factory()
                ),
                recorded_at=self._clock(),
                payload=command,
            )
        )
        try:
            self._captures.add(persisted)
            self._captures.commit()
        except PlacementCaptureConflict:
            winner = (
                self._captures.find_by_capture(
                    source=command.source,
                    source_capture_reference=(
                        command
                        .source_capture_reference
                    ),
                )
            )
            if (
                winner is not None
                and winner.matches(command)
            ):
                return (
                    RecordPlacementKnowledgeResult(
                        RecordPlacementKnowledgeOutcome.RESOLVED,
                        winner,
                    )
                )
            return RecordPlacementKnowledgeResult(
                RecordPlacementKnowledgeOutcome.CAPTURE_CONFLICT
            )

        return RecordPlacementKnowledgeResult(
            RecordPlacementKnowledgeOutcome.RECORDED,
            persisted,
        )
