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
    RequirementLifecycleState,
)


class RetirementOutcome(str, Enum):
    RETIRED = "Retired"
    ALREADY_RETIRED = "AlreadyRetired"
    REQUIREMENT_NOT_FOUND = "RequirementNotFound"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"


@dataclass(frozen=True, slots=True)
class RetireRequirement:
    requirement_id: UUID
    actor_id: str
    effective_time: datetime


@dataclass(frozen=True, slots=True)
class RetirementResult:
    outcome: RetirementOutcome
    requirement: ConnectivityRequirement | None = None


class RetireConnectivityRequirement:
    def __init__(
        self,
        *,
        authority: RequirementAuthorityPort,
        requirements: ConnectivityRequirementRepository,
    ) -> None:
        self._authority = authority
        self._requirements = requirements

    def execute(self, command: RetireRequirement) -> RetirementResult:
        requirement = self._requirements.get_by_id(command.requirement_id)
        if requirement is None:
            return RetirementResult(RetirementOutcome.REQUIREMENT_NOT_FOUND)

        authority = self._authority.check(
            actor_id=command.actor_id,
            action=RequirementAuthorityAction.RETIRE,
            scope=requirement.governance_scope,
            effective_time=command.effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return RetirementResult(RetirementOutcome.AUTHORITY_DENIED)
        if (
            authority.outcome is not TernaryOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return RetirementResult(RetirementOutcome.AUTHORITY_UNKNOWN)
        if requirement.lifecycle_state is RequirementLifecycleState.RETIRED:
            return RetirementResult(
                RetirementOutcome.ALREADY_RETIRED,
                requirement=requirement,
            )

        updated = requirement.retired(
            actor_id=command.actor_id,
            effective_time=command.effective_time,
            authority_reference=authority.authority_reference,
        )
        self._requirements.save(
            updated,
            expected_version=requirement.version,
        )
        self._requirements.commit()
        return RetirementResult(
            RetirementOutcome.RETIRED,
            requirement=updated,
        )
