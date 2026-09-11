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
    RequirementInvariantError,
    RequirementLifecycleState,
)


class JustificationMutationOutcome(str, Enum):
    UPDATED = "Updated"
    ALREADY_IN_REQUESTED_VALUE = "AlreadyInRequestedValue"
    REQUIREMENT_NOT_FOUND = "RequirementNotFound"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    REQUIREMENT_RETIRED = "RequirementRetired"
    INPUT_INVALID = "InputInvalid"


@dataclass(frozen=True, slots=True)
class SetRequirementJustification:
    requirement_id: UUID
    justification: str
    actor_id: str
    effective_time: datetime


@dataclass(frozen=True, slots=True)
class JustificationMutationResult:
    outcome: JustificationMutationOutcome
    requirement: ConnectivityRequirement | None = None


class SetConnectivityRequirementJustification:
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
        command: SetRequirementJustification,
    ) -> JustificationMutationResult:
        requirement = self._requirements.get_by_id(command.requirement_id)
        if requirement is None:
            return JustificationMutationResult(
                JustificationMutationOutcome.REQUIREMENT_NOT_FOUND
            )

        authority = self._authority.check(
            actor_id=command.actor_id,
            action=RequirementAuthorityAction.SET_JUSTIFICATION,
            scope=requirement.governance_scope,
            effective_time=command.effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return JustificationMutationResult(
                JustificationMutationOutcome.AUTHORITY_DENIED
            )
        if (
            authority.outcome is not TernaryOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return JustificationMutationResult(
                JustificationMutationOutcome.AUTHORITY_UNKNOWN
            )
        if requirement.lifecycle_state is RequirementLifecycleState.RETIRED:
            return JustificationMutationResult(
                JustificationMutationOutcome.REQUIREMENT_RETIRED
            )

        normalized = command.justification.strip()
        if not normalized:
            return JustificationMutationResult(
                JustificationMutationOutcome.INPUT_INVALID
            )
        if requirement.justification == normalized:
            return JustificationMutationResult(
                JustificationMutationOutcome.ALREADY_IN_REQUESTED_VALUE,
                requirement=requirement,
            )

        try:
            updated = requirement.with_justification(
                justification=command.justification,
                actor_id=command.actor_id,
                effective_time=command.effective_time,
                authority_reference=authority.authority_reference,
            )
        except RequirementInvariantError:
            return JustificationMutationResult(
                JustificationMutationOutcome.INPUT_INVALID
            )
        self._requirements.save(
            updated,
            expected_version=requirement.version,
        )
        self._requirements.commit()
        return JustificationMutationResult(
            JustificationMutationOutcome.UPDATED,
            requirement=updated,
        )
