from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Callable
from uuid import UUID, uuid4

from napms.contexts.connectivity_decision.application.ports import (
    ConnectivityDecisionRepository,
    DecisionAuthorityAction,
    DecisionAuthorityPort,
    DecisionCurrentConflict,
    DecisionInteractionCataloguePort,
    SubjectOutcome,
    TernaryOutcome,
)
from napms.contexts.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionEvidenceReference,
    DecisionOutcome,
    DecisionProvenance,
    DecisionSubject,
    DecisionValidity,
)


class RecordDecisionOutcome(str, Enum):
    RECORDED = "Recorded"
    RESOLVED = "Resolved"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    SUBJECT_INVALID = "SubjectInvalid"
    SUBJECT_UNKNOWN = "SubjectUnknown"
    CURRENT_AMBIGUOUS = "CurrentAmbiguous"
    SUPERSESSION_REQUIRED = "SupersessionRequired"
    SUPERSESSION_INVALID = "SupersessionInvalid"
    CURRENT_CONFLICT = "CurrentConflict"


@dataclass(frozen=True, slots=True)
class RecordDecision:
    subject: DecisionSubject
    governance_scope: str
    outcome: DecisionOutcome
    validity: DecisionValidity
    reason_code: str
    reason_text: str
    evidence_references: tuple[DecisionEvidenceReference, ...]
    actor_id: str
    effective_time: datetime
    supersedes_decision_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class RecordDecisionResult:
    outcome: RecordDecisionOutcome
    decision: ConnectivityDecision | None = None


class RecordConnectivityDecision:
    def __init__(
        self,
        *,
        authority: DecisionAuthorityPort,
        catalogue: DecisionInteractionCataloguePort,
        decisions: ConnectivityDecisionRepository,
        id_factory: Callable[[], UUID] = uuid4,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._decisions = decisions
        self._id_factory = id_factory

    def execute(self, command: RecordDecision) -> RecordDecisionResult:
        authority = self._authority.check(
            actor_id=command.actor_id,
            action=DecisionAuthorityAction.DECIDE,
            scope=command.governance_scope,
            effective_time=command.effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return RecordDecisionResult(RecordDecisionOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not TernaryOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return RecordDecisionResult(RecordDecisionOutcome.AUTHORITY_UNKNOWN)

        subject = self._catalogue.validate_decision_subject(
            subject=command.subject,
            effective_time=command.effective_time,
        )
        if subject.outcome is SubjectOutcome.INVALID:
            return RecordDecisionResult(RecordDecisionOutcome.SUBJECT_INVALID)
        if (
            subject.outcome is not SubjectOutcome.VALID
            or subject.subject != command.subject
        ):
            return RecordDecisionResult(RecordDecisionOutcome.SUBJECT_UNKNOWN)

        current = self._decisions.find_current(
            subject=command.subject,
            governance_scope=command.governance_scope,
            as_of=command.validity.valid_from,
        )
        if len(current) > 1:
            return RecordDecisionResult(RecordDecisionOutcome.CURRENT_AMBIGUOUS)

        if current:
            selected = current[0]
            if selected.has_same_intent(
                subject=command.subject,
                governance_scope=command.governance_scope,
                outcome=command.outcome,
                validity=command.validity,
                reason_code=command.reason_code,
                reason_text=command.reason_text,
                evidence_references=command.evidence_references,
            ):
                return RecordDecisionResult(
                    RecordDecisionOutcome.RESOLVED,
                    decision=selected,
                )
            if command.supersedes_decision_id != selected.decision_id:
                return RecordDecisionResult(
                    RecordDecisionOutcome.SUPERSESSION_REQUIRED
                )
        elif command.supersedes_decision_id is not None:
            superseded = self._decisions.get_by_id(command.supersedes_decision_id)
            if (
                superseded is None
                or superseded.subject != command.subject
                or superseded.governance_scope != command.governance_scope
            ):
                return RecordDecisionResult(
                    RecordDecisionOutcome.SUPERSESSION_INVALID
                )
            return RecordDecisionResult(RecordDecisionOutcome.SUPERSESSION_INVALID)

        decision = ConnectivityDecision(
            decision_id=self._id_factory(),
            subject=command.subject,
            governance_scope=command.governance_scope,
            outcome=command.outcome,
            validity=command.validity,
            reason_code=command.reason_code,
            reason_text=command.reason_text,
            evidence_references=command.evidence_references,
            provenance=DecisionProvenance(
                actor_id=command.actor_id,
                decided_at=command.effective_time,
                authority_reference=authority.authority_reference,
            ),
            supersedes_decision_id=command.supersedes_decision_id,
        )

        try:
            self._decisions.add(decision)
            self._decisions.commit()
        except DecisionCurrentConflict:
            winner = self._decisions.find_current(
                subject=command.subject,
                governance_scope=command.governance_scope,
                as_of=command.validity.valid_from,
            )
            if len(winner) == 1 and winner[0].has_same_intent(
                subject=command.subject,
                governance_scope=command.governance_scope,
                outcome=command.outcome,
                validity=command.validity,
                reason_code=command.reason_code,
                reason_text=command.reason_text,
                evidence_references=command.evidence_references,
            ):
                return RecordDecisionResult(
                    RecordDecisionOutcome.RESOLVED,
                    decision=winner[0],
                )
            return RecordDecisionResult(RecordDecisionOutcome.CURRENT_CONFLICT)

        return RecordDecisionResult(
            RecordDecisionOutcome.RECORDED,
            decision=decision,
        )
