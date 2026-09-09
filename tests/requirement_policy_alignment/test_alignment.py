from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.requirement_policy_alignment.application.align import (
    AlignConnectivityRequirementToPolicy,
    AlignmentQueryOutcome,
)
from napms.requirement_policy_alignment.application.model import (
    AlignmentApplicability,
    AlignmentApplicabilityKind,
    AlignmentInvariantError,
    AlignmentRequirementLifecycle,
    AlignmentSemanticIdentity,
    AlignmentStatus,
    RequirementAlignmentSnapshot,
)
from napms.requirement_policy_alignment.application.ports import (
    PolicyCoverageOutcome,
    RequirementAlignmentReadOutcome,
    RequirementAlignmentReadResult,
)


NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
REQ_ID = UUID(int=1)
IDENTITY = AlignmentSemanticIdentity(UUID(int=10), UUID(int=20), UUID(int=30))


class FakeRequirements:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def get_for_alignment(self, **kwargs):
        self.calls.append(kwargs)
        return self.result


class FakePolicy:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = []

    def check_exact_coverage(self, **kwargs):
        self.calls.append(kwargs)
        return self.outcome


def found(
    *,
    lifecycle=AlignmentRequirementLifecycle.ACTIVE,
    applicability=None,
    reference="requirement-read-1",
):
    return RequirementAlignmentReadResult(
        RequirementAlignmentReadOutcome.FOUND,
        snapshot=RequirementAlignmentSnapshot(
            requirement_id=REQ_ID,
            semantic_identity=IDENTITY,
            lifecycle=lifecycle,
            applicability=applicability
            or AlignmentApplicability(AlignmentApplicabilityKind.ONGOING),
        ),
        read_authority_reference=reference,
    )


@pytest.mark.parametrize(
    "coverage,status",
    [
        (PolicyCoverageOutcome.COVERED, AlignmentStatus.COVERED),
        (PolicyCoverageOutcome.UNCOVERED, AlignmentStatus.UNCOVERED),
        (PolicyCoverageOutcome.UNKNOWN, AlignmentStatus.UNKNOWN),
    ],
)
def test_current_requirement_maps_exact_policy_coverage(coverage, status):
    requirements = FakeRequirements(found())
    policy = FakePolicy(coverage)

    result = AlignConnectivityRequirementToPolicy(
        requirements=requirements,
        policy=policy,
    ).execute(
        requirement_id=REQ_ID,
        actor_id="owner",
        as_of=NOW,
    )

    assert result.outcome is AlignmentQueryOutcome.ALIGNED
    assert result.status is status
    assert result.semantic_identity == IDENTITY
    assert result.requirement_read_authority_reference == "requirement-read-1"
    assert policy.calls == [
        {"semantic_identity": IDENTITY, "as_of": NOW}
    ]


def test_retired_requirement_is_not_current_and_skips_policy():
    policy = FakePolicy(PolicyCoverageOutcome.COVERED)

    result = AlignConnectivityRequirementToPolicy(
        requirements=FakeRequirements(
            found(lifecycle=AlignmentRequirementLifecycle.RETIRED)
        ),
        policy=policy,
    ).execute(
        requirement_id=REQ_ID,
        actor_id="owner",
        as_of=NOW,
    )

    assert result.status is AlignmentStatus.NOT_CURRENT
    assert policy.calls == []


def test_requirement_outside_absolute_window_is_not_current():
    applicability = AlignmentApplicability(
        AlignmentApplicabilityKind.ABSOLUTE_WINDOW,
        start=NOW + timedelta(hours=1),
        end=NOW + timedelta(hours=2),
    )
    policy = FakePolicy(PolicyCoverageOutcome.COVERED)

    result = AlignConnectivityRequirementToPolicy(
        requirements=FakeRequirements(
            found(applicability=applicability)
        ),
        policy=policy,
    ).execute(
        requirement_id=REQ_ID,
        actor_id="owner",
        as_of=NOW,
    )

    assert result.status is AlignmentStatus.NOT_CURRENT
    assert policy.calls == []


def test_requirement_absolute_window_is_half_open():
    applicability = AlignmentApplicability(
        AlignmentApplicabilityKind.ABSOLUTE_WINDOW,
        start=NOW,
        end=NOW + timedelta(hours=1),
    )

    assert applicability.applies_at(NOW)
    assert applicability.applies_at(NOW + timedelta(minutes=30))
    assert not applicability.applies_at(NOW + timedelta(hours=1))


@pytest.mark.parametrize(
    "read_outcome,query_outcome",
    [
        (
            RequirementAlignmentReadOutcome.NOT_FOUND,
            AlignmentQueryOutcome.REQUIREMENT_NOT_FOUND,
        ),
        (
            RequirementAlignmentReadOutcome.AUTHORITY_DENIED,
            AlignmentQueryOutcome.AUTHORITY_DENIED,
        ),
        (
            RequirementAlignmentReadOutcome.AUTHORITY_UNKNOWN,
            AlignmentQueryOutcome.AUTHORITY_UNKNOWN,
        ),
        (
            RequirementAlignmentReadOutcome.UNAVAILABLE,
            AlignmentQueryOutcome.UNAVAILABLE,
        ),
    ],
)
def test_requirement_failure_short_circuits_policy(read_outcome, query_outcome):
    policy = FakePolicy(PolicyCoverageOutcome.COVERED)

    result = AlignConnectivityRequirementToPolicy(
        requirements=FakeRequirements(
            RequirementAlignmentReadResult(read_outcome)
        ),
        policy=policy,
    ).execute(
        requirement_id=REQ_ID,
        actor_id="owner",
        as_of=NOW,
    )

    assert result.outcome is query_outcome
    assert result.status is None
    assert result.semantic_identity is None
    assert policy.calls == []


def test_found_without_read_provenance_fails_closed_before_policy():
    policy = FakePolicy(PolicyCoverageOutcome.COVERED)

    result = AlignConnectivityRequirementToPolicy(
        requirements=FakeRequirements(found(reference=None)),
        policy=policy,
    ).execute(
        requirement_id=REQ_ID,
        actor_id="owner",
        as_of=NOW,
    )

    assert result.outcome is AlignmentQueryOutcome.AUTHORITY_UNKNOWN
    assert policy.calls == []


def test_naive_as_of_is_rejected_before_any_port_call():
    requirements = FakeRequirements(found())
    policy = FakePolicy(PolicyCoverageOutcome.COVERED)

    with pytest.raises(AlignmentInvariantError):
        AlignConnectivityRequirementToPolicy(
            requirements=requirements,
            policy=policy,
        ).execute(
            requirement_id=REQ_ID,
            actor_id="owner",
            as_of=NOW.replace(tzinfo=None),
        )

    assert requirements.calls == []
    assert policy.calls == []
