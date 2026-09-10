from contextlib import contextmanager
from datetime import datetime, timezone
from uuid import UUID

from napms.access_policy.application.ports import DecisionOutcome as AccessPolicyOutcome
from napms.access_policy.domain.model import RuleSemanticIdentity
from napms.connectivity_decision.adapters.access_policy import (
    ConnectivityDecisionAccessPolicyAdapter,
)
from napms.connectivity_decision.application.ports import DecisionPersistenceError
from napms.connectivity_decision.domain.model import (
    ConnectivityDecision,
    DecisionOutcome,
    DecisionProvenance,
    DecisionSubject,
    DecisionValidity,
)


NOW = datetime(2026, 9, 10, 17, 0, tzinfo=timezone.utc)
SOURCE = UUID("00000000-0000-0000-0000-000000000101")
DESTINATION = UUID("00000000-0000-0000-0000-000000000102")
DCS = UUID("00000000-0000-0000-0000-000000000103")
DECISION = UUID("00000000-0000-0000-0000-000000000201")


class Repository:
    def __init__(self, matches=(), error=None):
        self.matches = matches
        self.error = error
        self.calls = []

    def find_current(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.matches


def _subject() -> RuleSemanticIdentity:
    return RuleSemanticIdentity(SOURCE, DESTINATION, DCS)


def _decision(outcome: DecisionOutcome) -> ConnectivityDecision:
    return ConnectivityDecision(
        decision_id=DECISION,
        subject=DecisionSubject(SOURCE, DESTINATION, DCS),
        governance_scope="local-demo",
        outcome=outcome,
        validity=DecisionValidity(valid_from=NOW),
        reason_code="approved",
        reason_text="Reviewed and approved.",
        evidence_references=(),
        provenance=DecisionProvenance(
            actor_id="decision-maker",
            decided_at=NOW,
            authority_reference="authority:decision",
        ),
    )


def _adapter(repository: Repository) -> ConnectivityDecisionAccessPolicyAdapter:
    @contextmanager
    def open_repository():
        yield repository

    return ConnectivityDecisionAccessPolicyAdapter(open_repository=open_repository)


def test_maps_one_effective_allowed_decision() -> None:
    repository = Repository((_decision(DecisionOutcome.ALLOWED),))

    result = _adapter(repository).obtain(
        subject=_subject(), governance_scope="local-demo", as_of=NOW
    )

    assert result.outcome is AccessPolicyOutcome.ALLOWED
    assert result.decision_reference == str(DECISION)
    assert result.valid_from == NOW
    assert repository.calls[0]["governance_scope"] == "local-demo"


def test_maps_one_effective_not_allowed_decision() -> None:
    repository = Repository((_decision(DecisionOutcome.NOT_ALLOWED),))

    result = _adapter(repository).obtain(
        subject=_subject(), governance_scope="local-demo", as_of=NOW
    )

    assert result.outcome is AccessPolicyOutcome.NOT_ALLOWED
    assert result.decision_reference == str(DECISION)


def test_no_or_ambiguous_final_decision_is_unknown_not_permission() -> None:
    no_decision = _adapter(Repository()).obtain(
        subject=_subject(), governance_scope="local-demo", as_of=NOW
    )
    ambiguous = _adapter(
        Repository(
            (
                _decision(DecisionOutcome.ALLOWED),
                _decision(DecisionOutcome.NOT_ALLOWED),
            )
        )
    ).obtain(subject=_subject(), governance_scope="local-demo", as_of=NOW)

    assert no_decision.outcome is AccessPolicyOutcome.UNKNOWN
    assert ambiguous.outcome is AccessPolicyOutcome.UNKNOWN


def test_persistence_failure_is_unknown_not_permission() -> None:
    result = _adapter(Repository(error=DecisionPersistenceError())).obtain(
        subject=_subject(), governance_scope="local-demo", as_of=NOW
    )

    assert result.outcome is AccessPolicyOutcome.UNKNOWN
