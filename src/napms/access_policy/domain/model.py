from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from uuid import UUID


class DomainInvariantError(Exception):
    """Raised when constructing or applying an impossible Access Policy state."""


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
class OperationalStateTransition:
    rule_id: UUID
    from_state: OperationalState
    to_state: OperationalState
    actor_id: str
    effective_time: datetime
    governance_scope: str
    authority_reference: str


@dataclass(frozen=True, slots=True)
class AccessRule:
    rule_id: UUID
    semantic_identity: RuleSemanticIdentity
    operational_state: OperationalState
    decision: DecisionReference
    proposal_provenance: ProposalProvenance
    operational_state_history: tuple[OperationalStateTransition, ...] = ()

    @property
    def governance_scope(self) -> str:
        """Stable Rule governance scope established by accepted proposal authority."""
        return self.proposal_provenance.authority_scope

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

    def with_operational_state(
        self,
        *,
        target_state: OperationalState,
        actor_id: str,
        effective_time: datetime,
        authority_reference: str,
    ) -> "AccessRule":
        if target_state is self.operational_state:
            raise DomainInvariantError("operational state transition requires a different target state")

        transition = OperationalStateTransition(
            rule_id=self.rule_id,
            from_state=self.operational_state,
            to_state=target_state,
            actor_id=actor_id,
            effective_time=effective_time,
            governance_scope=self.governance_scope,
            authority_reference=authority_reference,
        )
        return replace(
            self,
            operational_state=target_state,
            operational_state_history=self.operational_state_history + (transition,),
        )
