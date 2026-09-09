from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Callable
from uuid import UUID, uuid4

from napms.technical_access_evidence.application.ports import (
    EvidenceCaptureConflict,
    TechnicalAccessEvidenceRepository,
)
from napms.technical_access_evidence.domain.model import (
    EvidenceKind,
    EvidenceSourceReference,
    EvidenceTime,
    SourceCaptureReference,
    SourceScopeReference,
    TechnicalAccessEntry,
    TechnicalAccessEntryPayload,
    TechnicalAccessEvidenceCapturePayload,
    TechnicalAccessEvidenceSet,
)


class RecordEvidenceOutcome(str, Enum):
    RECORDED = "Recorded"
    RESOLVED = "Resolved"
    CAPTURE_CONFLICT = "CaptureConflict"


@dataclass(frozen=True, slots=True)
class RecordEvidenceSet:
    kind: EvidenceKind
    source: EvidenceSourceReference
    source_scope: SourceScopeReference
    source_capture_reference: SourceCaptureReference
    evidence_time: EvidenceTime
    entries: tuple[TechnicalAccessEntryPayload, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "entries", tuple(self.entries))

    @property
    def capture_payload(self) -> TechnicalAccessEvidenceCapturePayload:
        return TechnicalAccessEvidenceCapturePayload(
            kind=self.kind,
            source_scope=self.source_scope,
            evidence_time=self.evidence_time,
            entries=self.entries,
        )


@dataclass(frozen=True, slots=True)
class RecordEvidenceSetResult:
    outcome: RecordEvidenceOutcome
    evidence_set: TechnicalAccessEvidenceSet | None = None


class RecordTechnicalAccessEvidenceSet:
    def __init__(
        self,
        *,
        evidence_sets: TechnicalAccessEvidenceRepository,
        set_id_factory: Callable[[], UUID] = uuid4,
        entry_id_factory: Callable[[], UUID] = uuid4,
        clock: Callable[[], datetime] = lambda: datetime.now(timezone.utc),
    ) -> None:
        self._evidence_sets = evidence_sets
        self._set_id_factory = set_id_factory
        self._entry_id_factory = entry_id_factory
        self._clock = clock

    def execute(self, command: RecordEvidenceSet) -> RecordEvidenceSetResult:
        existing = self._evidence_sets.find_by_capture(
            source=command.source,
            source_capture_reference=command.source_capture_reference,
        )
        if existing is not None:
            if existing.matches_capture(
                source=command.source,
                source_capture_reference=command.source_capture_reference,
                payload=command.capture_payload,
            ):
                return RecordEvidenceSetResult(
                    RecordEvidenceOutcome.RESOLVED,
                    evidence_set=existing,
                )
            return RecordEvidenceSetResult(
                RecordEvidenceOutcome.CAPTURE_CONFLICT
            )

        evidence_set = TechnicalAccessEvidenceSet(
            evidence_set_id=self._set_id_factory(),
            kind=command.kind,
            source=command.source,
            source_scope=command.source_scope,
            source_capture_reference=command.source_capture_reference,
            evidence_time=command.evidence_time,
            recorded_at=self._clock(),
            entries=tuple(
                TechnicalAccessEntry(
                    evidence_entry_id=self._entry_id_factory(),
                    payload=payload,
                )
                for payload in command.entries
            ),
        )

        try:
            self._evidence_sets.add(evidence_set)
            self._evidence_sets.commit()
        except EvidenceCaptureConflict:
            winner = self._evidence_sets.find_by_capture(
                source=command.source,
                source_capture_reference=command.source_capture_reference,
            )
            if winner is not None and winner.matches_capture(
                source=command.source,
                source_capture_reference=command.source_capture_reference,
                payload=command.capture_payload,
            ):
                return RecordEvidenceSetResult(
                    RecordEvidenceOutcome.RESOLVED,
                    evidence_set=winner,
                )
            return RecordEvidenceSetResult(
                RecordEvidenceOutcome.CAPTURE_CONFLICT
            )

        return RecordEvidenceSetResult(
            RecordEvidenceOutcome.RECORDED,
            evidence_set=evidence_set,
        )
