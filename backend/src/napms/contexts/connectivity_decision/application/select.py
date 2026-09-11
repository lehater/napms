from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from napms.contexts.connectivity_decision.application.ports import (
    ConnectivityDecisionRepository,
)
from napms.contexts.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionSubject,
)


class SelectionOutcome(str, Enum):
    FOUND = "Found"
    NOT_FOUND = "NotFound"
    AMBIGUOUS = "Ambiguous"


@dataclass(frozen=True, slots=True)
class SelectionResult:
    outcome: SelectionOutcome
    decision: ConnectivityDecision | None = None


class SelectEffectiveConnectivityDecision:
    def __init__(self, *, decisions: ConnectivityDecisionRepository) -> None:
        self._decisions = decisions

    def execute(
        self,
        *,
        subject: DecisionSubject,
        governance_scope: str,
        as_of: datetime,
    ) -> SelectionResult:
        current = self._decisions.find_current(
            subject=subject,
            governance_scope=governance_scope,
            as_of=as_of,
        )
        if not current:
            return SelectionResult(SelectionOutcome.NOT_FOUND)
        if len(current) != 1:
            return SelectionResult(SelectionOutcome.AMBIGUOUS)
        return SelectionResult(SelectionOutcome.FOUND, current[0])
