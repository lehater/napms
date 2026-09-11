from collections import defaultdict

from napms.contexts.connectivity_decision.application.ports import (
    ConnectivityDecisionRepository,
    DecisionPersistenceError,
)
from napms.contexts.connectivity_decision.domain.model import (
    DecisionOutcome,
    DecisionSubject,
)
from napms.workflows.scoped_connectivity_inventory.application.model import (
    DecisionSummary,
    DecisionSummaryState,
    InteractionIdentity,
)
from napms.workflows.scoped_connectivity_inventory.application.ports import (
    DecisionSummaryReadResult,
    DependencyAvailability,
)


def _to_subject(identity: InteractionIdentity) -> DecisionSubject:
    return DecisionSubject(
        source_component_deployment_id=identity.source_component_deployment_id,
        destination_component_deployment_id=identity.destination_component_deployment_id,
        dcs_contract_revision_id=identity.dcs_contract_revision_id,
    )


def _to_inventory(subject: DecisionSubject) -> InteractionIdentity:
    return InteractionIdentity(
        subject.source_component_deployment_id,
        subject.destination_component_deployment_id,
        subject.dcs_contract_revision_id,
    )


class ConnectivityDecisionScopedConnectivityAdapter:
    """Project final Decision truth into the coarse Scoped Connectivity contract."""

    def __init__(self, *, decisions: ConnectivityDecisionRepository) -> None:
        self._decisions = decisions

    def summarize_decisions(
        self,
        *,
        responsibility_scope,
        identities,
        as_of,
    ) -> DecisionSummaryReadResult:
        unique = tuple(dict.fromkeys(identities))
        if not unique:
            return DecisionSummaryReadResult(
                DependencyAvailability.AVAILABLE,
                (),
            )

        requested = set(unique)
        try:
            rows = self._decisions.find_current_for_subjects(
                subjects=tuple(_to_subject(identity) for identity in unique),
                governance_scope=responsibility_scope,
                as_of=as_of,
            )
        except DecisionPersistenceError:
            return DecisionSummaryReadResult(
                DependencyAvailability.UNAVAILABLE
            )

        grouped: dict[InteractionIdentity, list] = defaultdict(list)
        for decision in rows:
            identity = _to_inventory(decision.subject)
            if (
                decision.governance_scope != responsibility_scope
                or identity not in requested
                or not decision.is_effective_at(as_of)
            ):
                return DecisionSummaryReadResult(
                    DependencyAvailability.UNAVAILABLE
                )
            grouped[identity].append(decision)

        items = []
        for identity in unique:
            matches = grouped.get(identity, ())
            if len(matches) == 0:
                state = DecisionSummaryState.NO_FINAL_DECISION
            elif len(matches) != 1:
                state = DecisionSummaryState.UNKNOWN
            else:
                state = (
                    DecisionSummaryState.ALLOWED
                    if matches[0].outcome is DecisionOutcome.ALLOWED
                    else DecisionSummaryState.NOT_ALLOWED
                )
            items.append(DecisionSummary(identity=identity, state=state))

        return DecisionSummaryReadResult(
            DependencyAvailability.AVAILABLE,
            tuple(items),
        )
