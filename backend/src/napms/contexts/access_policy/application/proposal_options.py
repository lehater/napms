from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from napms.contexts.access_policy.application.ports import (
    AuthorityAction,
    AuthorityPort,
    ProposalAuthorityDiscoveryPort,
    ProposalInteractionCataloguePort,
    ProposalInteractionPage,
    ProposalScopeOptions,
    TernaryOutcome,
)


class ProposalInteractionDiscoveryOutcome(str, Enum):
    AVAILABLE = "Available"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"


@dataclass(frozen=True, slots=True)
class ProposalInteractionDiscoveryResult:
    outcome: ProposalInteractionDiscoveryOutcome
    page: ProposalInteractionPage | None = None


class DiscoverProposalScopes:
    def __init__(self, *, authority: ProposalAuthorityDiscoveryPort) -> None:
        self._authority = authority

    def execute(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> ProposalScopeOptions:
        return self._authority.list_effective_proposal_scopes(
            actor_id=actor_id,
            effective_time=effective_time,
        )


class DiscoverProposalInteractions:
    def __init__(
        self,
        *,
        authority: AuthorityPort,
        catalogue: ProposalInteractionCataloguePort,
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
    ) -> ProposalInteractionDiscoveryResult:
        authority = self._authority.check(
            actor_id=actor_id,
            action=AuthorityAction.PROPOSE_CONNECTIVITY,
            scope=scope,
            effective_time=effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return ProposalInteractionDiscoveryResult(
                ProposalInteractionDiscoveryOutcome.AUTHORITY_DENIED
            )
        if authority.outcome is TernaryOutcome.UNKNOWN or authority.authority_reference is None:
            return ProposalInteractionDiscoveryResult(
                ProposalInteractionDiscoveryOutcome.AUTHORITY_UNKNOWN
            )

        return ProposalInteractionDiscoveryResult(
            ProposalInteractionDiscoveryOutcome.AVAILABLE,
            self._catalogue.list_directed_interactions(
                page=page,
                page_size=page_size,
                search=search,
            ),
        )
