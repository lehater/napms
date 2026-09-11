from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from napms.contexts.technical_access_evidence.domain.model import (
    EvidenceKind,
    EvidenceSourceReference,
    SourceCaptureReference,
    SourceScopeReference,
    TechnicalAccessEvidenceSet,
)


class EvidencePersistenceError(Exception):
    """TAE persistence failed without a trustworthy semantic result."""


class EvidenceCommitOutcomeUnknown(EvidencePersistenceError):
    """Commit acknowledgement is unknown; application success cannot be claimed."""


class EvidenceCaptureConflict(EvidencePersistenceError):
    """Concurrent persistence found the same source/capture identity."""


def _require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be offset-aware")


@dataclass(frozen=True, slots=True)
class EvidenceSetFilters:
    source: EvidenceSourceReference | None = None
    source_scope: SourceScopeReference | None = None
    kind: EvidenceKind | None = None
    recorded_from: datetime | None = None
    recorded_until: datetime | None = None

    def __post_init__(self) -> None:
        if self.recorded_from is not None:
            _require_aware(self.recorded_from, field_name="recorded_from")
        if self.recorded_until is not None:
            _require_aware(self.recorded_until, field_name="recorded_until")
        if (
            self.recorded_from is not None
            and self.recorded_until is not None
            and self.recorded_from >= self.recorded_until
        ):
            raise ValueError("recorded_from must be before recorded_until")


class TechnicalAccessEvidenceRepository(Protocol):
    def get_by_id(
        self,
        evidence_set_id: UUID,
    ) -> TechnicalAccessEvidenceSet | None: ...

    def find_by_capture(
        self,
        *,
        source: EvidenceSourceReference,
        source_capture_reference: SourceCaptureReference,
    ) -> TechnicalAccessEvidenceSet | None: ...

    def list(
        self,
        *,
        filters: EvidenceSetFilters,
        offset: int,
        limit: int,
    ) -> tuple[TechnicalAccessEvidenceSet, ...]: ...

    def add(self, evidence_set: TechnicalAccessEvidenceSet) -> None: ...

    def commit(self) -> None: ...
