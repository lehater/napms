from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from napms.contexts.connectivity_requirements.application.ports import (
    RequirementAuthorityAction,
    RequirementAuthorityPort,
    RequirementDeclarationScopeDiscoveryPort,
    RequirementInteractionDiscoveryPort,
    RequirementInteractionPage,
    RequirementScopeOptions,
    TernaryOutcome,
)


class DiscoverRequirementScopes:
    def __init__(
        self,
        *,
        discovery: RequirementDeclarationScopeDiscoveryPort,
    ) -> None:
        self._discovery = discovery

    def execute(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> RequirementScopeOptions:
        return self._discovery.list_effective_declaration_scopes(
            actor_id=actor_id,
            effective_time=effective_time,
        )


class RequiredInteractionDiscoveryOutcome(str, Enum):
    AVAILABLE = "Available"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"


@dataclass(frozen=True, slots=True)
class RequiredInteractionDiscoveryResult:
    outcome: RequiredInteractionDiscoveryOutcome
    page: RequirementInteractionPage | None = None


class DiscoverRequiredInteractions:
    def __init__(
        self,
        *,
        authority: RequirementAuthorityPort,
        catalogue: RequirementInteractionDiscoveryPort,
    ) -> None:
        self._authority = authority
        self._catalogue = catalogue

    def execute(
        self,
        *,
        actor_id: str,
        scope: str,
        effective_time: datetime,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
    ) -> RequiredInteractionDiscoveryResult:
        authority = self._authority.check(
            actor_id=actor_id,
            action=RequirementAuthorityAction.DECLARE,
            scope=scope,
            effective_time=effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return RequiredInteractionDiscoveryResult(
                RequiredInteractionDiscoveryOutcome.AUTHORITY_DENIED
            )
        if (
            authority.outcome is not TernaryOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return RequiredInteractionDiscoveryResult(
                RequiredInteractionDiscoveryOutcome.AUTHORITY_UNKNOWN
            )

        return RequiredInteractionDiscoveryResult(
            RequiredInteractionDiscoveryOutcome.AVAILABLE,
            page=self._catalogue.list_required_interactions(
                page=page,
                page_size=page_size,
                search=search,
            ),
        )
