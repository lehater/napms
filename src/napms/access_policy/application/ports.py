from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.access_policy.application.inventory_summary import (
    AccessRuleInventorySnapshot,
)
from napms.access_policy.domain.model import AccessRule, RuleSemanticIdentity


class AuthorityAction(str, Enum):
    PROPOSE_CONNECTIVITY = "ProposeConnectivity"
    SET_RULE_OPERATIONAL_STATE = "SetRuleOperationalState"
    SET_RULE_EFFECTIVE_WINDOW = "SetRuleEffectiveWindow"
    READ_ACCESS_RULE = "ReadAccessRule"
    READ_EFFECTIVE_DESIRED_POLICY = "ReadEffectiveDesiredPolicy"


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
    governance_scope: str
    valid_from: datetime | None
    valid_until: datetime | None = None
    decision_reference: str | None = None


class AccessRulePersistenceError(Exception):
    """Persistence execution failed without establishing application success."""


class AccessRuleCommitOutcomeUnknown(AccessRulePersistenceError):
    """Commit acknowledgement failed, so the authoritative outcome is uncertain."""


class RuleSemanticIdentityConflict(AccessRulePersistenceError):
    """The authoritative uniqueness boundary selected another Rule for this identity."""


@dataclass(frozen=True, slots=True)
class ProposalScopeOptions:
    permitted_scopes: tuple[str, ...]
    ambiguous_scopes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ProposalInteractionPage:
    identities: tuple[RuleSemanticIdentity, ...]
    page: int
    page_size: int
    has_more: bool


class ProposalAuthorityDiscoveryPort(Protocol):
    def list_effective_proposal_scopes(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> ProposalScopeOptions: ...


@dataclass(frozen=True, slots=True)
class AccessRuleReadScopeOptions:
    permitted_scopes: tuple[str, ...]
    ambiguous_scopes: tuple[str, ...]


class AccessRuleReadAuthorityDiscoveryPort(Protocol):
    def list_effective_read_rule_scopes(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> AccessRuleReadScopeOptions: ...


@dataclass(frozen=True, slots=True)
class EffectivePolicyReadScopeOptions:
    permitted_scopes: tuple[str, ...]
    ambiguous_scopes: tuple[str, ...]


class EffectivePolicyReadAuthorityDiscoveryPort(Protocol):
    def list_effective_policy_read_scopes(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> EffectivePolicyReadScopeOptions: ...


class ProposalInteractionCataloguePort(Protocol):
    def list_directed_interactions(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
    ) -> ProposalInteractionPage: ...


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
    def obtain(
        self,
        *,
        subject: RuleSemanticIdentity,
        governance_scope: str,
        as_of: datetime,
    ) -> ConnectivityDecision: ...


class AccessRuleRepository(Protocol):
    def find_by_identity(self, identity: RuleSemanticIdentity) -> AccessRule | None: ...
    def find_inventory_summaries(
        self,
        identities: tuple[RuleSemanticIdentity, ...],
    ) -> tuple[AccessRuleInventorySnapshot, ...]: ...
    def get_by_id(self, rule_id: UUID) -> AccessRule | None: ...
    def list_by_governance_scope(self, scope: str) -> tuple[AccessRule, ...]: ...
    def list_by_governance_scopes(
        self,
        scopes: tuple[str, ...],
        *,
        offset: int,
        limit: int,
    ) -> tuple[AccessRule, ...]: ...
    def add(self, rule: AccessRule) -> None: ...
    def save(self, rule: AccessRule) -> None: ...
    def commit(self) -> None: ...
