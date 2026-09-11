from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from napms.technical_access_evidence.application.ports import (
    EvidenceSetFilters,
    TechnicalAccessEvidenceRepository,
)
from napms.technical_access_evidence.domain.model import (
    EvidenceSourceReference,
    SourceCaptureReference,
    TechnicalAccessEvidenceSet,
)


class EvidenceSetDetailOutcome(str, Enum):
    FOUND = "Found"
    NOT_FOUND = "NotFound"


@dataclass(frozen=True, slots=True)
class EvidenceSetDetailResult:
    outcome: EvidenceSetDetailOutcome
    evidence_set: TechnicalAccessEvidenceSet | None = None


class GetTechnicalAccessEvidenceSet:
    def __init__(
        self,
        *,
        evidence_sets: TechnicalAccessEvidenceRepository,
    ) -> None:
        self._evidence_sets = evidence_sets

    def execute(self, evidence_set_id: UUID) -> EvidenceSetDetailResult:
        evidence_set = self._evidence_sets.get_by_id(evidence_set_id)
        return EvidenceSetDetailResult(
            (
                EvidenceSetDetailOutcome.FOUND
                if evidence_set is not None
                else EvidenceSetDetailOutcome.NOT_FOUND
            ),
            evidence_set=evidence_set,
        )


class FindTechnicalAccessEvidenceSet:
    def __init__(
        self,
        *,
        evidence_sets: TechnicalAccessEvidenceRepository,
    ) -> None:
        self._evidence_sets = evidence_sets

    def execute(
        self,
        *,
        source: EvidenceSourceReference,
        source_capture_reference: SourceCaptureReference,
    ) -> EvidenceSetDetailResult:
        evidence_set = self._evidence_sets.find_by_capture(
            source=source,
            source_capture_reference=source_capture_reference,
        )
        return EvidenceSetDetailResult(
            (
                EvidenceSetDetailOutcome.FOUND
                if evidence_set is not None
                else EvidenceSetDetailOutcome.NOT_FOUND
            ),
            evidence_set=evidence_set,
        )


@dataclass(frozen=True, slots=True)
class EvidenceSetListPage:
    evidence_sets: tuple[TechnicalAccessEvidenceSet, ...]
    page: int
    page_size: int
    has_more: bool


class ListTechnicalAccessEvidenceSets:
    def __init__(
        self,
        *,
        evidence_sets: TechnicalAccessEvidenceRepository,
    ) -> None:
        self._evidence_sets = evidence_sets

    def execute(
        self,
        *,
        filters: EvidenceSetFilters = EvidenceSetFilters(),
        page: int = 1,
        page_size: int = 50,
    ) -> EvidenceSetListPage:
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        rows = self._evidence_sets.list(
            filters=filters,
            offset=(page - 1) * page_size,
            limit=page_size + 1,
        )
        return EvidenceSetListPage(
            evidence_sets=rows[:page_size],
            page=page,
            page_size=page_size,
            has_more=len(rows) > page_size,
        )
