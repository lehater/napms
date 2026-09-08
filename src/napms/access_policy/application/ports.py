from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.access_policy.domain.model import AccessRule, RuleSemanticIdentity


class AuthorityAction(str, Enum):
    PROPOSE_CONNECTIVITY = "ProposeConnectivity"


class TernaryOutcome(str, Enum):
    PERMITTED = "Permitted"
    DENIED = "Denied"
    UNKNOWN = "Unknown"


class InteractionOutcome(str, Enum):
    VALID = "Valid"
    INVALID = "Invalid"
    UNKNOWN = "Unknown"


class DecisionOutcome(str, Enum):
    ALLOWED = "Allowed"
    NOT_ALLOWED = "NotAllowed"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class AuthorityCheck:
    outcome: TernaryOutcome
    authority_reference: str | None = None


@dataclass(frozen=True, slots=True)
class InteractionCheck:
    outcome: InteractionOutcome
    identity: RuleSemanticIdentity | None = None
    provenance_reference: str | None = None


@dataclass(frozen=True, slots=True)
class ConnectivityDecision:
    outcome: DecisionOutcome
    subject: RuleSemanticIdentity
    decision_reference: str | None = None


class AccessRulePersistenceError(Exception):
    """Persistence execution failed without establishing application success."""


class AccessRuleCommitOutcomeUnknown(AccessRulePersistenceError):
    """Commit acknowledgement failed, so the authoritative outcome is uncertain."""


class RuleSemanticIdentityConflict(AccessRulePersistenceError):
    """The authoritative uniqueness boundary selected another Rule for this identity."""


class AuthorityPort(Protocol):
    def check(
        self,
        *,
        actor_id: str,
        action: AuthorityAction,
        scope: str,
        effective_time: datetime,
    ) -> AuthorityCheck: ...


class CommunicationCataloguePort(Protocol):
    def resolve_directed_interaction(
        self, *, identity: RuleSemanticIdentity, effective_time: datetime
    ) -> InteractionCheck: ...


class ConnectivityDecisionPort(Protocol):
    def obtain(self, *, subject: RuleSemanticIdentity) -> ConnectivityDecision: ...


class AccessRuleRepository(Protocol):
    def find_by_identity(self, identity: RuleSemanticIdentity) -> AccessRule | None: ...
    def get_by_id(self, rule_id: UUID) -> AccessRule | None: ...
    def add(self, rule: AccessRule) -> None: ...
    def commit(self) -> None: ...
