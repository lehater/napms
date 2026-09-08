from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from napms.access_policy.domain.model import AccessRule, RuleSemanticIdentity


class AuthorityAction(str, Enum):\n    PROPOSE_CONNECTIVITY = "ProposeConnectivity"\n\n\nclass TernaryOutcome(str, Enum):
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
    provenance_reference: str | None = None


@dataclass(frozen=True, slots=True)
class ConnectivityDecision:
    outcome: DecisionOutcome
    subject: RuleSemanticIdentity
    decision_reference: str | None = None


class AuthorityPort(Protocol):
    def check(\n        self,\n        *,\n        actor_id: str,\n        action: AuthorityAction,\n        scope: str,\n        effective_time: datetime,\n    ) -> AuthorityCheck: ...


class CommunicationCataloguePort(Protocol):
    def resolve_directed_interaction(
        self, *, identity: RuleSemanticIdentity, effective_time: datetime
    ) -> InteractionCheck: ...


class ConnectivityDecisionPort(Protocol):
    def obtain(self, *, subject: RuleSemanticIdentity) -> ConnectivityDecision: ...


class AccessRuleRepository(Protocol):
    def find_by_identity(self, identity: RuleSemanticIdentity) -> AccessRule | None: ...
    def add(self, rule: AccessRule) -> None: ...
