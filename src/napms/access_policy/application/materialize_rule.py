from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from napms.access_policy.application.ports import (
    AccessRuleRepository,
    AuthorityPort,
    CommunicationCataloguePort,
    ConnectivityDecisionPort,
    DecisionOutcome,
    InteractionOutcome,
    TernaryOutcome,
)
from napms.access_policy.domain.model import AccessRule, DecisionReference, RuleSemanticIdentity


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
    proposal_reference: str

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
            scope=command.authority_scope,
            effective_time=command.effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return MaterializationResult(MaterializationOutcome.AUTHORITY_DENIED)
        if authority.outcome is TernaryOutcome.UNKNOWN:
            return MaterializationResult(MaterializationOutcome.AUTHORITY_UNKNOWN)

        identity = command.semantic_identity
        interaction = self._catalogue.resolve_directed_interaction(
            identity=identity, effective_time=command.effective_time
        )
        if interaction.outcome is InteractionOutcome.INVALID:
            return MaterializationResult(MaterializationOutcome.INTERACTION_INVALID)
        if interaction.outcome is InteractionOutcome.UNKNOWN:
            return MaterializationResult(MaterializationOutcome.INTERACTION_UNKNOWN)

        decision = self._decisions.obtain(subject=identity)
        if decision.subject != identity:
            return MaterializationResult(MaterializationOutcome.DECISION_SUBJECT_MISMATCH)
        if decision.outcome is DecisionOutcome.NOT_ALLOWED:
            return MaterializationResult(MaterializationOutcome.NOT_ALLOWED)
        if decision.outcome is DecisionOutcome.UNKNOWN:
            return MaterializationResult(MaterializationOutcome.DECISION_UNKNOWN)

        existing = self._rules.find_by_identity(identity)
        if existing is not None:
            return MaterializationResult(MaterializationOutcome.RESOLVED, existing)

        if authority.authority_reference is None:
            return MaterializationResult(MaterializationOutcome.AUTHORITY_UNKNOWN)

        rule = AccessRule.materialized_from_allowed_decision(
            rule_id=self._new_rule_id(),
            semantic_identity=identity,
            decision=DecisionReference(
                subject=identity,
                decision_id=decision.decision_reference,
            ),
            proposal_reference=command.proposal_reference,
            authority_reference=authority.authority_reference,
        )
        self._rules.add(rule)
        return MaterializationResult(MaterializationOutcome.MATERIALIZED, rule)
