from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.access_policy.domain.model import AccessRule, RuleSemanticIdentity


class AuthorityAction(str, Enum):
    PROPOSE_CONNECTIVITY = "ProposeConnectivity"
    SET_RULE_OPERATIONAL_STATE = "SetRuleOperationalState"
    SET_RULE_EFFECTIVE_WINDOW = "SetRuleEffectiveWindow"
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


class ApplicationProjectionOutcome(str, Enum):
    RESOLVED = "Resolved"
    MISSING = "Missing"
    INVALID = "Invalid"
    UNKNOWN = "Unknown"


class ResourceRealizationOutcome(str, Enum):
    RESOLVED = "Resolved"
    MISSING = "Missing"
    STALE = "Stale"
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


@dataclass(frozen=True, slots=True)
class ResourceReference:
    value: str


@dataclass(frozen=True, slots=True)
class EndpointRealization:
    endpoint_reference: str
    technical_address: str


@dataclass(frozen=True, slots=True)
class ApplicationProjectionFact:
    outcome: ApplicationProjectionOutcome
    subject: RuleSemanticIdentity | None = None
    as_of: datetime | None = None
    source_resource_references: tuple[ResourceReference, ...] = ()
    destination_resource_references: tuple[ResourceReference, ...] = ()
    dcs_projection_payload: bytes | None = None
    fact_reference: str | None = None
    validity_reference: str | None = None
    provenance_reference: str | None = None


@dataclass(frozen=True, slots=True)
class ResourceRealizationFact:
    outcome: ResourceRealizationOutcome
    resource_reference: ResourceReference | None = None
    as_of: datetime | None = None
    endpoint_realizations: tuple[EndpointRealization, ...] = ()
    fact_reference: str | None = None
    validity_reference: str | None = None
    provenance_reference: str | None = None


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


class ApplicationCommunicationProjectionPort(Protocol):
    def resolve_projection(
        self,
        *,
        subject: RuleSemanticIdentity,
        as_of: datetime,
    ) -> ApplicationProjectionFact: ...


class ResourceCatalogueProjectionPort(Protocol):
    def resolve_realization(
        self,
        *,
        resource_reference: ResourceReference,
        as_of: datetime,
    ) -> ResourceRealizationFact: ...


class ConnectivityDecisionPort(Protocol):
    def obtain(self, *, subject: RuleSemanticIdentity) -> ConnectivityDecision: ...


class AccessRuleRepository(Protocol):
    def find_by_identity(self, identity: RuleSemanticIdentity) -> AccessRule | None: ...
    def get_by_id(self, rule_id: UUID) -> AccessRule | None: ...
    def list_by_governance_scope(self, scope: str) -> tuple[AccessRule, ...]: ...
    def add(self, rule: AccessRule) -> None: ...
    def save(self, rule: AccessRule) -> None: ...
    def commit(self) -> None: ...
