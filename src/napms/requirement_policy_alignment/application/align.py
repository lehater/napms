from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.requirement_policy_alignment.application.model import (
    AlignmentRequirementLifecycle,
    AlignmentSemanticIdentity,
    AlignmentStatus,
    require_aware,
)
from napms.requirement_policy_alignment.application.ports import (
    AuthorizedRequirementAlignmentPort,
    EffectivePolicyCoveragePort,
    PolicyCoverageOutcome,
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
