from datetime import datetime, timedelta, timezone

import pytest

from napms.contexts.access_policy.application.ports import AuthorityAction, TernaryOutcome
from napms.contexts.authority_management.infrastructure.integrations.access_policy import (
    AccessPolicyAuthorityAdapter,
)
from napms.contexts.authority_management.application.check_authority import (
    AuthorityOutcome,
    CheckAuthority,
)
from napms.contexts.authority_management.domain.model import (
    AuthorityAssignment,
    AuthorityInvariantError,
)


START = datetime(2026, 9, 8, 8, 0, tzinfo=timezone.utc)
END = datetime(2026, 9, 9, 8, 0, tzinfo=timezone.utc)


def assignment(reference="auth-1", *, valid_from=START, valid_to=END):
    return AuthorityAssignment(
        reference_id=reference,
        actor_id="actor-1",
        action=AuthorityAction.SET_RULE_OPERATIONAL_STATE.value,
        scope="scope-1",
        valid_from=valid_from,
        valid_to=valid_to,
        provenance_reference=f"prov-{reference}",
    )


class FakeAssignments:
    def __init__(self, matches):
        self.matches = tuple(matches)
        self.calls = []

    def find_effective(self, **kwargs):
        self.calls.append(kwargs)
        return self.matches


def test_exact_effective_assignment_is_permitted():
    repo = FakeAssignments([assignment()])
    decision = CheckAuthority(assignments=repo).execute(
        actor_id="actor-1",
        action=AuthorityAction.SET_RULE_OPERATIONAL_STATE.value,
        scope="scope-1",
        effective_time=START,
    )

    assert decision.outcome is AuthorityOutcome.PERMITTED
    assert decision.authority_reference == "auth-1"
    assert decision.provenance_reference == "prov-auth-1"


def test_no_effective_assignment_is_denied():
    decision = CheckAuthority(assignments=FakeAssignments([])).execute(
        actor_id="actor-1",
        action=AuthorityAction.SET_RULE_OPERATIONAL_STATE.value,
        scope="scope-1",
        effective_time=START,
    )

    assert decision.outcome is AuthorityOutcome.DENIED
    assert decision.authority_reference is None


def test_ambiguous_overlapping_assignments_fail_closed_unknown():
    decision = CheckAuthority(
        assignments=FakeAssignments([assignment("auth-1"), assignment("auth-2")])
    ).execute(
        actor_id="actor-1",
        action=AuthorityAction.SET_RULE_OPERATIONAL_STATE.value,
        scope="scope-1",
        effective_time=START,
    )

    assert decision.outcome is AuthorityOutcome.UNKNOWN
    assert decision.authority_reference is None


@pytest.mark.parametrize(
    "effective_time,permitted",
    [
        (START, True),
        (END - timedelta(microseconds=1), True),
        (END, False),
    ],
)
def test_assignment_validity_is_half_open(effective_time, permitted):
    value = assignment()
    assert value.is_effective_at(effective_time) is permitted


def test_access_policy_adapter_preserves_action_scope_time_and_reference():
    repo = FakeAssignments([assignment()])
    adapter = AccessPolicyAuthorityAdapter(
        checker=CheckAuthority(assignments=repo)
    )

    result = adapter.check(
        actor_id="actor-1",
        action=AuthorityAction.SET_RULE_OPERATIONAL_STATE,
        scope="scope-1",
        effective_time=START,
    )

    assert result.outcome is TernaryOutcome.PERMITTED
    assert result.authority_reference == "auth-1"
    assert repo.calls == [
        {
            "actor_id": "actor-1",
            "action": "SetRuleOperationalState",
            "scope": "scope-1",
            "effective_time": START,
        }
    ]


@pytest.mark.parametrize(
    "valid_from,valid_to",
    [
        (START.replace(tzinfo=None), END),
        (START, END.replace(tzinfo=None)),
        (END, START),
        (START, START),
    ],
)
def test_invalid_assignment_validity_is_rejected(valid_from, valid_to):
    with pytest.raises(AuthorityInvariantError):
        assignment(valid_from=valid_from, valid_to=valid_to)
