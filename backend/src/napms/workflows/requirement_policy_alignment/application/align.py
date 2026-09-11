from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.workflows.requirement_policy_alignment.application.model import (
    AlignmentRequirementLifecycle,
    AlignmentSemanticIdentity,
    AlignmentStatus,
    require_aware,
)
from napms.workflows.requirement_policy_alignment.application.ports import (
    AuthorizedRequirementAlignmentListPort,
    AuthorizedRequirementAlignmentPort,
    EffectivePolicyCoveragePort,
    PolicyCoverageOutcome,
    RequirementAlignmentListOutcome,
    RequirementAlignmentReadOutcome,
)


class AlignmentQueryOutcome(str, Enum):
    ALIGNED = "Aligned"
    REQUIREMENT_NOT_FOUND = "RequirementNotFound"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    UNAVAILABLE = "Unavailable"


@dataclass(frozen=True, slots=True)
class AlignmentResult:
    outcome: AlignmentQueryOutcome
    requirement_id: UUID
    as_of: datetime
    status: AlignmentStatus | None = None
    semantic_identity: AlignmentSemanticIdentity | None = None
    requirement_read_authority_reference: str | None = None


class AlignConnectivityRequirementToPolicy:
    def __init__(
        self,
        *,
        requirements: AuthorizedRequirementAlignmentPort,
        policy: EffectivePolicyCoveragePort,
    ) -> None:
        self._requirements = requirements
        self._policy = policy

    def execute(
        self,
        *,
        requirement_id: UUID,
        actor_id: str,
        as_of: datetime,
    ) -> AlignmentResult:
        require_aware(as_of, field_name="as_of")
        requirement = self._requirements.get_for_alignment(
            requirement_id=requirement_id,
            actor_id=actor_id,
            as_of=as_of,
        )

        mapping = {
            RequirementAlignmentReadOutcome.NOT_FOUND: (
                AlignmentQueryOutcome.REQUIREMENT_NOT_FOUND
            ),
            RequirementAlignmentReadOutcome.AUTHORITY_DENIED: (
                AlignmentQueryOutcome.AUTHORITY_DENIED
            ),
            RequirementAlignmentReadOutcome.AUTHORITY_UNKNOWN: (
                AlignmentQueryOutcome.AUTHORITY_UNKNOWN
            ),
            RequirementAlignmentReadOutcome.UNAVAILABLE: (
                AlignmentQueryOutcome.UNAVAILABLE
            ),
        }
        if requirement.outcome is not RequirementAlignmentReadOutcome.FOUND:
            return AlignmentResult(
                outcome=mapping[requirement.outcome],
                requirement_id=requirement_id,
                as_of=as_of,
            )

        if (
            requirement.snapshot is None
            or requirement.read_authority_reference is None
        ):
            return AlignmentResult(
                outcome=AlignmentQueryOutcome.AUTHORITY_UNKNOWN,
                requirement_id=requirement_id,
                as_of=as_of,
            )

        snapshot = requirement.snapshot
        if (
            snapshot.lifecycle is AlignmentRequirementLifecycle.RETIRED
            or not snapshot.applicability.applies_at(as_of)
        ):
            return AlignmentResult(
                outcome=AlignmentQueryOutcome.ALIGNED,
                requirement_id=requirement_id,
                as_of=as_of,
                status=AlignmentStatus.NOT_CURRENT,
                semantic_identity=snapshot.semantic_identity,
                requirement_read_authority_reference=(
                    requirement.read_authority_reference
                ),
            )

        coverage = self._policy.check_exact_coverage(
            semantic_identity=snapshot.semantic_identity,
            as_of=as_of,
        )
        status = {
            PolicyCoverageOutcome.COVERED: AlignmentStatus.COVERED,
            PolicyCoverageOutcome.UNCOVERED: AlignmentStatus.UNCOVERED,
            PolicyCoverageOutcome.UNKNOWN: AlignmentStatus.UNKNOWN,
        }[coverage]
        return AlignmentResult(
            outcome=AlignmentQueryOutcome.ALIGNED,
            requirement_id=requirement_id,
            as_of=as_of,
            status=status,
            semantic_identity=snapshot.semantic_identity,
            requirement_read_authority_reference=(
                requirement.read_authority_reference
            ),
        )



@dataclass(frozen=True, slots=True)
class AlignmentPageItem:
    requirement_id: UUID
    as_of: datetime
    status: AlignmentStatus
    semantic_identity: AlignmentSemanticIdentity


@dataclass(frozen=True, slots=True)
class AlignmentPageResult:
    outcome: AlignmentQueryOutcome
    items: tuple[AlignmentPageItem, ...]
    page: int
    page_size: int
    has_more: bool
    ambiguous_scopes: tuple[str, ...] = ()


class AlignVisibleConnectivityRequirementsToPolicy:
    def __init__(
        self,
        *,
        requirements: AuthorizedRequirementAlignmentListPort,
        policy: EffectivePolicyCoveragePort,
    ) -> None:
        self._requirements = requirements
        self._policy = policy

    def execute(
        self,
        *,
        actor_id: str,
        as_of: datetime,
        page: int = 1,
        page_size: int = 50,
    ) -> AlignmentPageResult:
        require_aware(as_of, field_name="as_of")
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        listed = self._requirements.list_for_alignment(
            actor_id=actor_id,
            as_of=as_of,
            page=page,
            page_size=page_size,
        )
        if (
            listed.outcome is RequirementAlignmentListOutcome.UNAVAILABLE
            or listed.page is None
        ):
            return AlignmentPageResult(
                outcome=AlignmentQueryOutcome.UNAVAILABLE,
                items=(),
                page=page,
                page_size=page_size,
                has_more=False,
            )

        items = []
        for snapshot in listed.page.snapshots:
            if (
                snapshot.lifecycle is AlignmentRequirementLifecycle.RETIRED
                or not snapshot.applicability.applies_at(as_of)
            ):
                status = AlignmentStatus.NOT_CURRENT
            else:
                coverage = self._policy.check_exact_coverage(
                    semantic_identity=snapshot.semantic_identity,
                    as_of=as_of,
                )
                status = {
                    PolicyCoverageOutcome.COVERED: AlignmentStatus.COVERED,
                    PolicyCoverageOutcome.UNCOVERED: AlignmentStatus.UNCOVERED,
                    PolicyCoverageOutcome.UNKNOWN: AlignmentStatus.UNKNOWN,
                }[coverage]
            items.append(
                AlignmentPageItem(
                    requirement_id=snapshot.requirement_id,
                    as_of=as_of,
                    status=status,
                    semantic_identity=snapshot.semantic_identity,
                )
            )

        return AlignmentPageResult(
            outcome=AlignmentQueryOutcome.ALIGNED,
            items=tuple(items),
            page=listed.page.page,
            page_size=listed.page.page_size,
            has_more=listed.page.has_more,
            ambiguous_scopes=listed.page.ambiguous_scopes,
        )
