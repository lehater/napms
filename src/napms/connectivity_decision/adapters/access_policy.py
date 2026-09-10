from contextlib import AbstractContextManager
from typing import Callable

from napms.access_policy.application.ports import (
    ConnectivityDecision as AccessPolicyDecision,
    DecisionOutcome as AccessPolicyDecisionOutcome,
    RuleSemanticIdentity,
)
from napms.connectivity_decision.application.ports import (
    ConnectivityDecisionRepository,
    DecisionPersistenceError,
)
from napms.connectivity_decision.domain.model import (
    DecisionOutcome,
    DecisionSubject,
)


class ConnectivityDecisionAccessPolicyAdapter:
    """Expose final Connectivity Decision truth through the Access Policy port."""

    def __init__(
        self,
        *,
        open_repository: Callable[
            [], AbstractContextManager[ConnectivityDecisionRepository]
        ],
    ) -> None:
        self._open_repository = open_repository

    def obtain(self, *, subject, governance_scope, as_of) -> AccessPolicyDecision:
        durable_subject = DecisionSubject(
            source_component_deployment_id=subject.source_component_deployment_id,
            destination_component_deployment_id=subject.destination_component_deployment_id,
            dcs_contract_revision_id=subject.dcs_contract_revision_id,
        )
        try:
            with self._open_repository() as repository:
                matches = repository.find_current(
                    subject=durable_subject,
                    governance_scope=governance_scope,
                    as_of=as_of,
                )
        except DecisionPersistenceError:
            return self._unknown(subject, governance_scope)

        if len(matches) != 1:
            return self._unknown(subject, governance_scope)

        decision = matches[0]
        if (
            decision.subject != durable_subject
            or decision.governance_scope != governance_scope
            or not decision.is_effective_at(as_of)
        ):
            return self._unknown(subject, governance_scope)

        outcome = (
            AccessPolicyDecisionOutcome.ALLOWED
            if decision.outcome is DecisionOutcome.ALLOWED
            else AccessPolicyDecisionOutcome.NOT_ALLOWED
        )
        return AccessPolicyDecision(
            outcome=outcome,
            subject=subject,
            governance_scope=governance_scope,
            valid_from=decision.validity.valid_from,
            valid_until=decision.validity.valid_until,
            decision_reference=str(decision.decision_id),
        )

    @staticmethod
    def _unknown(
        subject: RuleSemanticIdentity,
        governance_scope: str,
    ) -> AccessPolicyDecision:
        return AccessPolicyDecision(
            outcome=AccessPolicyDecisionOutcome.UNKNOWN,
            subject=subject,
            governance_scope=governance_scope,
            valid_from=None,
        )
