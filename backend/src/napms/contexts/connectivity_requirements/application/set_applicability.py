from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.contexts.connectivity_requirements.application.ports import (
    ConnectivityRequirementRepository,
    RequirementAuthorityAction,
    RequirementAuthorityPort,
    TernaryOutcome,
)
from napms.contexts.connectivity_requirements.domain.model import (
    ConnectivityRequirement,
    RequirementApplicability,
    RequirementLifecycleState,
)


class ApplicabilityMutationOutcome(str, Enum):
    UPDATED = "Updated"
    ALREADY_IN_REQUESTED_VALUE = "AlreadyInRequestedValue"
    REQUIREMENT_NOT_FOUND = "RequirementNotFound"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    REQUIREMENT_RETIRED = "RequirementRetired"


@dataclass(frozen=True, slots=True)
class SetRequirementApplicability:
    requirement_id: UUID
    applicability: RequirementApplicability
    actor_id: str
    effective_time: datetime


@dataclass(frozen=True, slots=True)
class ApplicabilityMutationResult:
    outcome: ApplicabilityMutationOutcome
    requirement: ConnectivityRequirement | None = None


class SetConnectivityRequirementApplicability:
    def __init__(
        self,
        *,
        authority: RequirementAuthorityPort,
        requirements: ConnectivityRequirementRepository,
    ) -> None:
        self._authority = authority
        self._requirements = requirements

    def execute(
        self,
        command: SetRequirementApplicability,
    ) -> ApplicabilityMutationResult:
        requirement = self._requirements.get_by_id(command.requirement_id)
        if requirement is None:
            return ApplicabilityMutationResult(
                ApplicabilityMutationOutcome.REQUIREMENT_NOT_FOUND
            )

        authority = self._authority.check(
            actor_id=command.actor_id,
            action=RequirementAuthorityAction.SET_APPLICABILITY,
            scope=requirement.governance_scope,
            effective_time=command.effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return ApplicabilityMutationResult(
                ApplicabilityMutationOutcome.AUTHORITY_DENIED
            )
        if (
            authority.outcome is not TernaryOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return ApplicabilityMutationResult(
                ApplicabilityMutationOutcome.AUTHORITY_UNKNOWN
            )
        if requirement.lifecycle_state is RequirementLifecycleState.RETIRED:
            return ApplicabilityMutationResult(
                ApplicabilityMutationOutcome.REQUIREMENT_RETIRED
            )
        if requirement.applicability == command.applicability:
            return ApplicabilityMutationResult(
                ApplicabilityMutationOutcome.ALREADY_IN_REQUESTED_VALUE,
                requirement=requirement,
            )

        updated = requirement.with_applicability(
            applicability=command.applicability,
            actor_id=command.actor_id,
            effective_time=command.effective_time,
            authority_reference=authority.authority_reference,
        )
        self._requirements.save(
            updated,
            expected_version=requirement.version,
        )
        self._requirements.commit()
        return ApplicabilityMutationResult(
            ApplicabilityMutationOutcome.UPDATED,
            requirement=updated,
        )
