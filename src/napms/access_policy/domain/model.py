from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class DomainInvariantError(Exception):
    """Raised when constructing an impossible Access Policy domain state."""


@dataclass(frozen=True, slots=True)
class RuleSemanticIdentity:
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    dcs_contract_revision_id: UUID


class OperationalState(str, Enum):
    ACTIVE = "Active"
    INACTIVE = "Inactive"


class ConnectivityDecisionResult(str, Enum):
    ALLOWED = "Allowed"
    NOT_ALLOWED = "NotAllowed"


@dataclass(frozen=True, slots=True)
class DecisionReference:
    subject: RuleSemanticIdentity
    result: ConnectivityDecisionResult
    decision_id: str | None = None


@dataclass(frozen=True, slots=True)
class ProposalProvenance:
    actor_id: str
    authority_scope: str
    effective_time: datetime
    authority_reference: str
    catalogue_reference: str


@dataclass(frozen=True, slots=True)
class AccessRule:
    rule_id: UUID
    semantic_identity: RuleSemanticIdentity
    operational_state: OperationalState
    decision: DecisionReference
    proposal_provenance: ProposalProvenance

    @classmethod
    def materialized_from_allowed_decision(
        cls,
        *,
        rule_id: UUID,
        semantic_identity: RuleSemanticIdentity,
        decision: DecisionReference,
        proposal_provenance: ProposalProvenance,
    ) -> "AccessRule":
        if decision.subject != semantic_identity:
            raise DomainInvariantError("decision subject does not match rule semantic identity")
        if decision.result is not ConnectivityDecisionResult.ALLOWED:
            raise DomainInvariantError("access rule requires an Allowed connectivity decision")
        return cls(
            rule_id=rule_id,
            semantic_identity=semantic_identity,
            operational_state=OperationalState.ACTIVE,
            decision=decision,
            proposal_provenance=proposal_provenance,
        )
