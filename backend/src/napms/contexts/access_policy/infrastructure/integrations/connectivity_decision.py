from napms.contexts.access_policy.application.ports import (
    ConnectivityDecision as AccessPolicyConnectivityDecision,
)
from napms.contexts.access_policy.application.ports import DecisionOutcome as AccessPolicyDecisionOutcome
from napms.contexts.access_policy.domain.model import RuleSemanticIdentity
from napms.contexts.connectivity_decision.application.select import (
    SelectEffectiveConnectivityDecision,
    SelectionOutcome,
)
from napms.contexts.connectivity_decision.domain.model import (
    DecisionOutcome as DomainDecisionOutcome,
    DecisionSubject,
)


class ConnectivityDecisionConsumerAdapter:
    """Translate Decision BC selection into the Access Policy consumer-owned projection."""

    def __init__(
        self,
        *,
        select_effective_decision: SelectEffectiveConnectivityDecision,
    ) -> None:
        self._select_effective_decision = select_effective_decision

    def obtain(
        self,
        *,
        subject: RuleSemanticIdentity,
        governance_scope: str,
        as_of,
    ) -> AccessPolicyConnectivityDecision:
        decision_subject = DecisionSubject(
            source_component_deployment_id=subject.source_component_deployment_id,
            destination_component_deployment_id=subject.destination_component_deployment_id,
            dcs_contract_revision_id=subject.dcs_contract_revision_id,
        )
        result = self._select_effective_decision.execute(
            subject=decision_subject,
            governance_scope=governance_scope,
            as_of=as_of,
        )
        if result.outcome is not SelectionOutcome.FOUND or result.decision is None:
            return AccessPolicyConnectivityDecision(
                outcome=AccessPolicyDecisionOutcome.UNKNOWN,
                subject=subject,
                governance_scope=governance_scope,
                valid_from=None,
            )

        decision = result.decision
        projected_subject = RuleSemanticIdentity(
            source_component_deployment_id=decision.subject.source_component_deployment_id,
            destination_component_deployment_id=decision.subject.destination_component_deployment_id,
            dcs_contract_revision_id=decision.subject.dcs_contract_revision_id,
        )
        outcome = (
            AccessPolicyDecisionOutcome.ALLOWED
            if decision.outcome is DomainDecisionOutcome.ALLOWED
            else AccessPolicyDecisionOutcome.NOT_ALLOWED
        )
        return AccessPolicyConnectivityDecision(
            outcome=outcome,
            subject=projected_subject,
            governance_scope=decision.governance_scope,
            valid_from=decision.validity.valid_from,
            valid_until=decision.validity.valid_until,
            decision_reference=str(decision.decision_id),
        )
