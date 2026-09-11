from datetime import datetime, timedelta, timezone
from uuid import UUID

import pytest

from napms.workflows.requirement_policy_alignment.application.align import (
    AlignConnectivityRequirementToPolicy,
    AlignVisibleConnectivityRequirementsToPolicy,
    AlignmentQueryOutcome,
)
from napms.workflows.requirement_policy_alignment.application.model import (
    AlignmentApplicability,
    AlignmentApplicabilityKind,
    AlignmentInvariantError,
    AlignmentRequirementLifecycle,
    AlignmentSemanticIdentity,
    AlignmentStatus,
    RequirementAlignmentSnapshot,
)
from napms.workflows.requirement_policy_alignment.application.ports import (
    PolicyCoverageOutcome,
    RequirementAlignmentListOutcome,
    RequirementAlignmentListResult,
    RequirementAlignmentReadOutcome,
    RequirementAlignmentReadResult,
    RequirementAlignmentSnapshotPage,
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


class FakeRequirementList:
    def __init__(self, result):
        self.result = result
        self.calls = []

    def list_for_alignment(self, **kwargs):
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



def test_visible_requirement_page_aligns_each_item_without_persistence():
    current = RequirementAlignmentSnapshot(
        requirement_id=REQ_ID,
        semantic_identity=IDENTITY,
        lifecycle=AlignmentRequirementLifecycle.ACTIVE,
        applicability=AlignmentApplicability(AlignmentApplicabilityKind.ONGOING),
    )
    retired = RequirementAlignmentSnapshot(
        requirement_id=UUID(int=2),
        semantic_identity=AlignmentSemanticIdentity(
            UUID(int=11), UUID(int=21), UUID(int=31)
        ),
        lifecycle=AlignmentRequirementLifecycle.RETIRED,
        applicability=AlignmentApplicability(AlignmentApplicabilityKind.ONGOING),
    )
    requirements = FakeRequirementList(
        RequirementAlignmentListResult(
            RequirementAlignmentListOutcome.AVAILABLE,
            page=RequirementAlignmentSnapshotPage(
                snapshots=(current, retired),
                page=1,
                page_size=50,
                has_more=False,
                ambiguous_scopes=("hidden-scope",),
            ),
        )
    )
    policy = FakePolicy(PolicyCoverageOutcome.COVERED)

    result = AlignVisibleConnectivityRequirementsToPolicy(
        requirements=requirements,
        policy=policy,
    ).execute(
        actor_id="owner",
        as_of=NOW,
        page=1,
        page_size=50,
    )

    assert result.outcome is AlignmentQueryOutcome.ALIGNED
    assert tuple(item.status for item in result.items) == (
        AlignmentStatus.COVERED,
        AlignmentStatus.NOT_CURRENT,
    )
    assert result.ambiguous_scopes == ("hidden-scope",)
    assert policy.calls == [
        {"semantic_identity": IDENTITY, "as_of": NOW}
    ]


def test_visible_requirement_page_maps_policy_unknown_per_item():
    snapshot = RequirementAlignmentSnapshot(
        requirement_id=REQ_ID,
        semantic_identity=IDENTITY,
        lifecycle=AlignmentRequirementLifecycle.ACTIVE,
        applicability=AlignmentApplicability(AlignmentApplicabilityKind.ONGOING),
    )
    requirements = FakeRequirementList(
        RequirementAlignmentListResult(
            RequirementAlignmentListOutcome.AVAILABLE,
            page=RequirementAlignmentSnapshotPage(
                snapshots=(snapshot,),
                page=2,
                page_size=10,
                has_more=True,
            ),
        )
    )

    result = AlignVisibleConnectivityRequirementsToPolicy(
        requirements=requirements,
        policy=FakePolicy(PolicyCoverageOutcome.UNKNOWN),
    ).execute(
        actor_id="owner",
        as_of=NOW,
        page=2,
        page_size=10,
    )

    assert result.items[0].status is AlignmentStatus.UNKNOWN
    assert result.page == 2
    assert result.page_size == 10
    assert result.has_more


def test_visible_requirement_page_unavailable_is_fail_closed():
    policy = FakePolicy(PolicyCoverageOutcome.UNCOVERED)
    result = AlignVisibleConnectivityRequirementsToPolicy(
        requirements=FakeRequirementList(
            RequirementAlignmentListResult(
                RequirementAlignmentListOutcome.UNAVAILABLE
            )
        ),
        policy=policy,
    ).execute(
        actor_id="owner",
        as_of=NOW,
    )

    assert result.outcome is AlignmentQueryOutcome.UNAVAILABLE
    assert result.items == ()
    assert policy.calls == []
