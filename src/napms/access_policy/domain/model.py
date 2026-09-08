from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from uuid import UUID


class DomainInvariantError(Exception):
    """Raised when constructing or applying an impossible Access Policy state."""


def _require_offset_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise DomainInvariantError(f"{field_name} must be an offset-aware datetime")


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
class EffectiveWindow:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        _require_offset_aware(self.start, field_name="EffectiveWindow.start")
        _require_offset_aware(self.end, field_name="EffectiveWindow.end")
        if self.start >= self.end:
            raise DomainInvariantError("EffectiveWindow requires start < end")

    def contains(self, as_of: datetime) -> bool:
        _require_offset_aware(as_of, field_name="as_of")
        return self.start <= as_of < self.end


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
class EffectiveWindowChange:
    rule_id: UUID
    previous_window: EffectiveWindow | None
    new_window: EffectiveWindow | None
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
    effective_window: EffectiveWindow | None = None
    effective_window_history: tuple[EffectiveWindowChange, ...] = ()

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

    def with_effective_window(
        self,
        *,
        window: EffectiveWindow | None,
        actor_id: str,
        effective_time: datetime,
        authority_reference: str,
    ) -> "AccessRule":
        if window == self.effective_window:
            raise DomainInvariantError("EffectiveWindow change requires a different value")

        change = EffectiveWindowChange(
            rule_id=self.rule_id,
            previous_window=self.effective_window,
            new_window=window,
            actor_id=actor_id,
            effective_time=effective_time,
            governance_scope=self.governance_scope,
            authority_reference=authority_reference,
        )
        return replace(
            self,
            effective_window=window,
            effective_window_history=self.effective_window_history + (change,),
        )

    def contributes_effect_at(self, as_of: datetime) -> bool:
        _require_offset_aware(as_of, field_name="as_of")
        if self.operational_state is not OperationalState.ACTIVE:
            return False
        return self.effective_window is None or self.effective_window.contains(as_of)
