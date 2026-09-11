from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.contexts.connectivity_decision.application.ports import (
    ConnectivityDecisionRepository,
    DecisionAuthorityAction,
    DecisionAuthorityPort,
    DecisionReadScopeDiscoveryPort,
    TernaryOutcome,
)
from napms.contexts.connectivity_decision.domain.model import ConnectivityDecision


@dataclass(frozen=True, slots=True)
class DecisionListPage:
    decisions: tuple[ConnectivityDecision, ...]
    page: int
    page_size: int
    has_more: bool
    ambiguous_scopes: tuple[str, ...]


class ListConnectivityDecisions:
    def __init__(
        self,
        *,
        read_scopes: DecisionReadScopeDiscoveryPort,
        decisions: ConnectivityDecisionRepository,
    ) -> None:
        self._read_scopes = read_scopes
        self._decisions = decisions

    def execute(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
        page: int = 1,
        page_size: int = 50,
    ) -> DecisionListPage:
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        scopes = self._read_scopes.list_effective_decision_read_scopes(
            actor_id=actor_id,
            effective_time=effective_time,
        )
        rows = (
            self._decisions.list_by_governance_scopes(
                scopes.permitted_scopes,
                offset=(page - 1) * page_size,
                limit=page_size + 1,
            )
            if scopes.permitted_scopes
            else ()
        )
        return DecisionListPage(
            decisions=rows[:page_size],
            page=page,
            page_size=page_size,
            has_more=len(rows) > page_size,
            ambiguous_scopes=scopes.ambiguous_scopes,
        )


class DecisionDetailOutcome(str, Enum):
    FOUND = "Found"
    DECISION_NOT_FOUND = "DecisionNotFound"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"


@dataclass(frozen=True, slots=True)
class DecisionDetailResult:
    outcome: DecisionDetailOutcome
    decision: ConnectivityDecision | None = None
    read_authority_reference: str | None = None


class GetConnectivityDecision:
    def __init__(
        self,
        *,
        authority: DecisionAuthorityPort,
        decisions: ConnectivityDecisionRepository,
    ) -> None:
        self._authority = authority
        self._decisions = decisions

    def execute(
        self,
        *,
        decision_id: UUID,
        actor_id: str,
        effective_time: datetime,
    ) -> DecisionDetailResult:
        decision = self._decisions.get_by_id(decision_id)
        if decision is None:
            return DecisionDetailResult(DecisionDetailOutcome.DECISION_NOT_FOUND)

        authority = self._authority.check(
            actor_id=actor_id,
            action=DecisionAuthorityAction.READ,
            scope=decision.governance_scope,
            effective_time=effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return DecisionDetailResult(DecisionDetailOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not TernaryOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return DecisionDetailResult(DecisionDetailOutcome.AUTHORITY_UNKNOWN)

        return DecisionDetailResult(
            DecisionDetailOutcome.FOUND,
            decision=decision,
            read_authority_reference=authority.authority_reference,
        )
