from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from napms.access_policy.application.ports import (
    AccessRuleRepository,
    AuthorityAction,
    AuthorityPort,
    CommunicationCataloguePort,
    ConnectivityDecisionPort,
    DecisionOutcome,
    InteractionOutcome,
    RuleSemanticIdentityConflict,
    TernaryOutcome,
)
from napms.access_policy.domain.model import (
    AccessRule,
    ConnectivityDecisionResult,
    DecisionReference,
    ProposalProvenance,
    RuleSemanticIdentity,
)


class MaterializationOutcome(str, Enum):
    MATERIALIZED = "Materialized"
    RESOLVED = "Resolved"
    NOT_ALLOWED = "NotAllowed"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    INTERACTION_INVALID = "InteractionInvalid"
    INTERACTION_UNKNOWN = "InteractionUnknown"
    DECISION_UNKNOWN = "DecisionUnknown"
    DECISION_SUBJECT_MISMATCH = "DecisionSubjectMismatch"


@dataclass(frozen=True, slots=True)
class SubmitAccessRuleProposal:
    actor_id: str
    authority_scope: str
    effective_time: datetime
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    dcs_contract_revision_id: UUID

    @property
    def semantic_identity(self) -> RuleSemanticIdentity:
        return RuleSemanticIdentity(
            self.source_component_deployment_id,
            self.destination_component_deployment_id,
            self.dcs_contract_revision_id,
        )


@dataclass(frozen=True, slots=True)
class MaterializationResult:
    outcome: MaterializationOutcome
    rule: AccessRule | None = None
    created: bool | None = None


class MaterializeAllowedAccessRule:
    def __init__(
        self,
        *,
        authority: AuthorityPort,
        catalogue: CommunicationCataloguePort,
        decisions: ConnectivityDecisionPort,
        rules: AccessRuleRepository,
        new_rule_id=uuid4,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue
        self._decisions = decisions
        self._rules = rules
        self._new_rule_id = new_rule_id

    def execute(self, command: SubmitAccessRuleProposal) -> MaterializationResult:
        authority = self._authority.check(
            actor_id=command.actor_id,
            action=AuthorityAction.PROPOSE_CONNECTIVITY,
            scope=command.authority_scope,
            effective_time=command.effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return MaterializationResult(MaterializationOutcome.AUTHORITY_DENIED)
        if authority.outcome is TernaryOutcome.UNKNOWN or authority.authority_reference is None:
            return MaterializationResult(MaterializationOutcome.AUTHORITY_UNKNOWN)

        identity = command.semantic_identity
        interaction = self._catalogue.resolve_directed_interaction(
            identity=identity, effective_time=command.effective_time
        )
        if interaction.outcome is InteractionOutcome.INVALID:
            return MaterializationResult(MaterializationOutcome.INTERACTION_INVALID)
        if interaction.outcome is InteractionOutcome.UNKNOWN:
            return MaterializationResult(MaterializationOutcome.INTERACTION_UNKNOWN)
        if interaction.identity != identity:
            return MaterializationResult(MaterializationOutcome.INTERACTION_INVALID)
        if interaction.provenance_reference is None:
            return MaterializationResult(MaterializationOutcome.INTERACTION_UNKNOWN)

        decision = self._decisions.obtain(
            subject=identity,
            governance_scope=command.authority_scope,
            as_of=command.effective_time,
        )
        if (
            decision.subject != identity
            or decision.governance_scope != command.authority_scope
        ):
            return MaterializationResult(MaterializationOutcome.DECISION_SUBJECT_MISMATCH)
        if decision.outcome is DecisionOutcome.UNKNOWN:
            return MaterializationResult(MaterializationOutcome.DECISION_UNKNOWN)
        if not _decision_is_effective_at(decision, command.effective_time):
            return MaterializationResult(MaterializationOutcome.DECISION_UNKNOWN)
        if decision.outcome is DecisionOutcome.NOT_ALLOWED:
            return MaterializationResult(MaterializationOutcome.NOT_ALLOWED)

        existing = self._rules.find_by_identity(identity)
        if existing is not None:
            return MaterializationResult(MaterializationOutcome.RESOLVED, existing, False)

        rule = AccessRule.materialized_from_allowed_decision(
            rule_id=self._new_rule_id(),
            semantic_identity=identity,
            decision=DecisionReference(
                subject=identity,
                result=ConnectivityDecisionResult.ALLOWED,
                decision_id=decision.decision_reference,
            ),
            proposal_provenance=ProposalProvenance(
                actor_id=command.actor_id,
                authority_scope=command.authority_scope,
                effective_time=command.effective_time,
                authority_reference=authority.authority_reference,
                catalogue_reference=interaction.provenance_reference,
            ),
        )
        try:
            self._rules.add(rule)
            self._rules.commit()
        except RuleSemanticIdentityConflict:
            winner = self._rules.find_by_identity(identity)
            if winner is None:
                raise
            return MaterializationResult(MaterializationOutcome.RESOLVED, winner, False)
        return MaterializationResult(MaterializationOutcome.MATERIALIZED, rule, True)


def _decision_is_effective_at(decision, as_of: datetime) -> bool:
    if decision.valid_from is None:
        return False
    if decision.valid_from.tzinfo is None or decision.valid_from.utcoffset() is None:
        return False
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        return False
    if decision.valid_until is not None:
        if (
            decision.valid_until.tzinfo is None
            or decision.valid_until.utcoffset() is None
        ):
            return False
        return decision.valid_from <= as_of < decision.valid_until
    return decision.valid_from <= as_of
