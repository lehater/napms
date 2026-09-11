from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.connectivity_decision.adapters.scoped_connectivity_inventory import (
    ConnectivityDecisionScopedConnectivityAdapter,
)
from napms.connectivity_decision.application.ports import DecisionPersistenceError
from napms.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionOutcome,
    DecisionProvenance,
    DecisionSubject,
    DecisionValidity,
)
from napms.scoped_connectivity_inventory.application.model import (
    DecisionSummaryState,
    InteractionIdentity,
)
from napms.scoped_connectivity_inventory.application.ports import (
    DependencyAvailability,
)


NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
SOURCE = UUID(int=7201)
DESTINATION = UUID(int=7202)
DCS = UUID(int=7203)
IDENTITY = InteractionIdentity(SOURCE, DESTINATION, DCS)
SUBJECT = DecisionSubject(SOURCE, DESTINATION, DCS)


def decision(
    *,
    decision_id=UUID(int=7204),
    outcome=DecisionOutcome.ALLOWED,
    scope="scope-a",
):
    return ConnectivityDecision(
        decision_id=decision_id,
        subject=SUBJECT,
        governance_scope=scope,
        outcome=outcome,
        validity=DecisionValidity(
            NOW - timedelta(hours=1),
            NOW + timedelta(hours=1),
        ),
        reason_code="PROTECTED_REASON",
        reason_text="Protected detail must not cross the inventory boundary.",
        evidence_references=(),
        provenance=DecisionProvenance(
            actor_id="protected-decider",
            decided_at=NOW - timedelta(hours=2),
            authority_reference="protected-authority",
        ),
    )


class FakeDecisions:
    def __init__(self, rows=(), error=None):
        self.rows = tuple(rows)
        self.error = error
        self.calls = []

    def find_current_for_subjects(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.rows


def summarize(repo, identities=(IDENTITY,), scope="scope-a"):
    return ConnectivityDecisionScopedConnectivityAdapter(
        decisions=repo
    ).summarize_decisions(
        responsibility_scope=scope,
        identities=identities,
        as_of=NOW,
    )


def test_found_allowed_and_not_allowed_project_only_coarse_state():
    for outcome, expected in (
        (DecisionOutcome.ALLOWED, DecisionSummaryState.ALLOWED),
        (DecisionOutcome.NOT_ALLOWED, DecisionSummaryState.NOT_ALLOWED),
    ):
        repo = FakeDecisions((decision(outcome=outcome),))
        result = summarize(repo)

        assert result.availability is DependencyAvailability.AVAILABLE
        assert result.items == (result.items[0],)
        assert result.items[0].identity == IDENTITY
        assert result.items[0].state is expected
        assert set(result.items[0].__dataclass_fields__) == {"identity", "state"}
        assert repo.calls == [
            {
                "subjects": (SUBJECT,),
                "governance_scope": "scope-a",
                "as_of": NOW,
            }
        ]


def test_absence_is_no_final_decision_not_unknown():
    result = summarize(FakeDecisions())

    assert result.availability is DependencyAvailability.AVAILABLE
    assert result.items[0].state is DecisionSummaryState.NO_FINAL_DECISION


def test_ambiguous_effective_decisions_are_unknown():
    result = summarize(
        FakeDecisions(
            (
                decision(decision_id=UUID(int=7204)),
                decision(decision_id=UUID(int=7205)),
            )
        )
    )

    assert result.availability is DependencyAvailability.AVAILABLE
    assert result.items[0].state is DecisionSummaryState.UNKNOWN


def test_persistence_failure_makes_only_decision_dimension_unavailable():
    result = summarize(FakeDecisions(error=DecisionPersistenceError()))

    assert result.availability is DependencyAvailability.UNAVAILABLE
    assert result.items == ()


def test_unexpected_cross_scope_row_fails_closed():
    result = summarize(FakeDecisions((decision(scope="scope-b"),)))

    assert result.availability is DependencyAvailability.UNAVAILABLE
    assert result.items == ()


def test_duplicate_input_is_batched_once_and_preserves_one_summary():
    repo = FakeDecisions((decision(),))
    result = summarize(repo, identities=(IDENTITY, IDENTITY))

    assert result.items[0].state is DecisionSummaryState.ALLOWED
    assert len(result.items) == 1
    assert repo.calls[0]["subjects"] == (SUBJECT,)
