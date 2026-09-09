from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.access_policy.adapters.connectivity_decision import (
    ConnectivityDecisionConsumerAdapter,
)
from napms.access_policy.application.ports import DecisionOutcome
from napms.access_policy.domain.model import RuleSemanticIdentity
from napms.connectivity_decision.application.select import (
    SelectionOutcome,
    SelectionResult,
)
from napms.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionOutcome as DomainDecisionOutcome,
    DecisionProvenance,
    DecisionSubject,
    DecisionValidity,
)


SOURCE = UUID("00000000-0000-0000-0000-000000000001")
DESTINATION = UUID("00000000-0000-0000-0000-000000000002")
DCS = UUID("00000000-0000-0000-0000-000000000003")
DECISION_ID = UUID("00000000-0000-0000-0000-000000000004")
NOW = datetime(2026, 9, 9, 8, 0, tzinfo=timezone.utc)
SUBJECT = RuleSemanticIdentity(SOURCE, DESTINATION, DCS)


class FakeSelector:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def execute(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


def durable_decision(outcome=DomainDecisionOutcome.ALLOWED):
    return ConnectivityDecision(
        decision_id=DECISION_ID,
        subject=DecisionSubject(SOURCE, DESTINATION, DCS),
        governance_scope="scope-1",
        outcome=outcome,
        validity=DecisionValidity(
            valid_from=NOW - timedelta(minutes=5),
            valid_until=NOW + timedelta(minutes=5),
        ),
        reason_code="accepted",
        reason_text="Accepted for adapter test.",
        evidence_references=(),
        provenance=DecisionProvenance(
            actor_id="decider-1",
            decided_at=NOW - timedelta(minutes=10),
            authority_reference="authority-1",
        ),
    )


@pytest.mark.parametrize(
    "domain_outcome,consumer_outcome",
    [
        (DomainDecisionOutcome.ALLOWED, DecisionOutcome.ALLOWED),
        (DomainDecisionOutcome.NOT_ALLOWED, DecisionOutcome.NOT_ALLOWED),
    ],
)
def test_found_decision_projects_consumer_owned_contract(
    domain_outcome,
    consumer_outcome,
):
    decision = durable_decision(domain_outcome)
    selector = FakeSelector(SelectionResult(SelectionOutcome.FOUND, decision))
    adapter = ConnectivityDecisionConsumerAdapter(
        select_effective_decision=selector,
    )

    result = adapter.obtain(
        subject=SUBJECT,
        governance_scope="scope-1",
        as_of=NOW,
    )

    assert selector.calls == [
        {
            "subject": DecisionSubject(SOURCE, DESTINATION, DCS),
            "governance_scope": "scope-1",
            "as_of": NOW,
        }
    ]
    assert result.outcome is consumer_outcome
    assert result.subject == SUBJECT
    assert result.governance_scope == "scope-1"
    assert result.valid_from == decision.validity.valid_from
    assert result.valid_until == decision.validity.valid_until
    assert result.decision_reference == str(DECISION_ID)


@pytest.mark.parametrize(
    "selection_outcome",
    [SelectionOutcome.NOT_FOUND, SelectionOutcome.AMBIGUOUS],
)
def test_no_trustworthy_selection_maps_to_unknown_without_fabricating_decision(
    selection_outcome,
):
    selector = FakeSelector(SelectionResult(selection_outcome))
    adapter = ConnectivityDecisionConsumerAdapter(
        select_effective_decision=selector,
    )

    result = adapter.obtain(
        subject=SUBJECT,
        governance_scope="scope-1",
        as_of=NOW,
    )

    assert result.outcome is DecisionOutcome.UNKNOWN
    assert result.subject == SUBJECT
    assert result.governance_scope == "scope-1"
    assert result.valid_from is None
    assert result.valid_until is None
    assert result.decision_reference is None
