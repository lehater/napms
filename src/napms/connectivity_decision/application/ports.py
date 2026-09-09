from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionSubject,
)


class DecisionAuthorityAction(str, Enum):
    DECIDE = "DecideConnectivity"
    READ = "ReadConnectivityDecision"


class TernaryOutcome(str, Enum):
    PERMITTED = "Permitted"
    DENIED = "Denied"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class DecisionAuthorityCheck:
    outcome: TernaryOutcome
    authority_reference: str | None = None


class SubjectOutcome(str, Enum):
    VALID = "Valid"
    INVALID = "Invalid"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class DecisionSubjectCheck:
    outcome: SubjectOutcome
    subject: DecisionSubject | None = None
    provenance_reference: str | None = None


@dataclass(frozen=True, slots=True)
class DecisionScopeOptions:
    permitted_scopes: tuple[str, ...]
    ambiguous_scopes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DecisionInteractionPage:
    subjects: tuple[DecisionSubject, ...]
    page: int
    page_size: int
    has_more: bool


class DecisionPersistenceError(Exception):
    """Decision persistence failed without a trustworthy semantic result."""


class DecisionCommitOutcomeUnknown(DecisionPersistenceError):
    """Commit acknowledgement is unknown; application success cannot be claimed."""


class DecisionCurrentConflict(DecisionPersistenceError):
    """Concurrent state prevents establishing the requested current Decision."""


class DecisionAuthorityPort(Protocol):
    def check(
        self,
        *,
        actor_id: str,
        action: DecisionAuthorityAction,
        scope: str,
        effective_time: datetime,
    ) -> DecisionAuthorityCheck: ...


class DecisionScopeDiscoveryPort(Protocol):
    def list_effective_decision_scopes(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> DecisionScopeOptions: ...


class DecisionReadScopeDiscoveryPort(Protocol):
    def list_effective_decision_read_scopes(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> DecisionScopeOptions: ...


class DecisionInteractionCataloguePort(Protocol):
    def validate_decision_subject(
        self,
        *,
        subject: DecisionSubject,
        effective_time: datetime,
    ) -> DecisionSubjectCheck: ...


class DecisionInteractionDiscoveryPort(Protocol):
    def list_decision_subjects(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
    ) -> DecisionInteractionPage: ...


class ConnectivityDecisionRepository(Protocol):
    def get_by_id(self, decision_id: UUID) -> ConnectivityDecision | None: ...

    def find_current(
        self,
        *,
        subject: DecisionSubject,
        governance_scope: str,
        as_of: datetime,
    ) -> tuple[ConnectivityDecision, ...]: ...

    def find_current_for_subjects(
        self,
        *,
        subjects: tuple[DecisionSubject, ...],
        governance_scope: str,
        as_of: datetime,
    ) -> tuple[ConnectivityDecision, ...]: ...

    def list_by_governance_scopes(
        self,
        scopes: tuple[str, ...],
        *,
        offset: int,
        limit: int,
    ) -> tuple[ConnectivityDecision, ...]: ...

    def add(self, decision: ConnectivityDecision) -> None: ...

    def commit(self) -> None: ...
