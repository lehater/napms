from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.connectivity_requirements.application.ports import (
    ConnectivityRequirementRepository,
    RequirementAuthorityAction,
    RequirementAuthorityPort,
    RequirementReadScopeDiscoveryPort,
    TernaryOutcome,
)
from napms.connectivity_requirements.domain.model import ConnectivityRequirement


@dataclass(frozen=True, slots=True)
class RequirementListPage:
    requirements: tuple[ConnectivityRequirement, ...]
    page: int
    page_size: int
    has_more: bool
    ambiguous_scopes: tuple[str, ...]


class ListConnectivityRequirements:
    def __init__(
        self,
        *,
        read_scopes: RequirementReadScopeDiscoveryPort,
        requirements: ConnectivityRequirementRepository,
    ) -> None:
        self._read_scopes = read_scopes
        self._requirements = requirements

    def execute(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
        page: int = 1,
        page_size: int = 50,
    ) -> RequirementListPage:
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        scopes = self._read_scopes.list_effective_read_scopes(
            actor_id=actor_id,
            effective_time=effective_time,
        )
        rows = (
            self._requirements.list_by_governance_scopes(
                scopes.permitted_scopes,
                offset=(page - 1) * page_size,
                limit=page_size + 1,
            )
            if scopes.permitted_scopes
            else ()
        )
        return RequirementListPage(
            requirements=rows[:page_size],
            page=page,
            page_size=page_size,
            has_more=len(rows) > page_size,
            ambiguous_scopes=scopes.ambiguous_scopes,
        )


class RequirementDetailOutcome(str, Enum):
    FOUND = "Found"
    REQUIREMENT_NOT_FOUND = "RequirementNotFound"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"


@dataclass(frozen=True, slots=True)
class RequirementDetailResult:
    outcome: RequirementDetailOutcome
    requirement: ConnectivityRequirement | None = None
    read_authority_reference: str | None = None
    applicability_mutation_admission: TernaryOutcome | None = None
    justification_mutation_admission: TernaryOutcome | None = None
    retirement_admission: TernaryOutcome | None = None


class GetConnectivityRequirement:
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
        *,
        requirement_id: UUID,
        actor_id: str,
        effective_time: datetime,
    ) -> RequirementDetailResult:
        requirement = self._requirements.get_by_id(requirement_id)
        if requirement is None:
            return RequirementDetailResult(
                RequirementDetailOutcome.REQUIREMENT_NOT_FOUND
            )

        authority = self._authority.check(
            actor_id=actor_id,
            action=RequirementAuthorityAction.READ,
            scope=requirement.governance_scope,
            effective_time=effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return RequirementDetailResult(
                RequirementDetailOutcome.AUTHORITY_DENIED
            )
        if (
            authority.outcome is not TernaryOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return RequirementDetailResult(
                RequirementDetailOutcome.AUTHORITY_UNKNOWN
            )
        def admission(action: RequirementAuthorityAction) -> TernaryOutcome:
            result = self._authority.check(
                actor_id=actor_id,
                action=action,
                scope=requirement.governance_scope,
                effective_time=effective_time,
            )
            if (
                result.outcome is TernaryOutcome.PERMITTED
                and result.authority_reference is None
            ):
                return TernaryOutcome.UNKNOWN
            return result.outcome

        return RequirementDetailResult(
            RequirementDetailOutcome.FOUND,
            requirement=requirement,
            read_authority_reference=authority.authority_reference,
            applicability_mutation_admission=admission(
                RequirementAuthorityAction.SET_APPLICABILITY
            ),
            justification_mutation_admission=admission(
                RequirementAuthorityAction.SET_JUSTIFICATION
            ),
            retirement_admission=admission(
                RequirementAuthorityAction.RETIRE
            ),
        )
