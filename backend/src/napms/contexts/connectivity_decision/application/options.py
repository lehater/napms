from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from napms.contexts.connectivity_decision.application.ports import (
    DecisionAuthorityAction,
    DecisionAuthorityPort,
    DecisionInteractionDiscoveryPort,
    DecisionInteractionPage,
    DecisionScopeDiscoveryPort,
    TernaryOutcome,
)


class DecisionInteractionDiscoveryOutcome(str, Enum):
    AVAILABLE = "Available"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"


@dataclass(frozen=True, slots=True)
class DecisionInteractionDiscoveryResult:
    outcome: DecisionInteractionDiscoveryOutcome
    page: DecisionInteractionPage | None = None


class DiscoverDecisionScopes:
    def __init__(self, *, discovery: DecisionScopeDiscoveryPort) -> None:
        self._discovery = discovery

    def execute(self, *, actor_id: str, effective_time: datetime):
        return self._discovery.list_effective_decision_scopes(
            actor_id=actor_id,
            effective_time=effective_time,
        )


class DiscoverDecisionInteractions:
    def __init__(
        self,
        *,
        authority: DecisionAuthorityPort,
        catalogue: DecisionInteractionDiscoveryPort,
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
    ) -> DecisionInteractionDiscoveryResult:
        authority = self._authority.check(
            actor_id=actor_id,
            action=DecisionAuthorityAction.DECIDE,
            scope=scope,
            effective_time=effective_time,
        )
        if authority.outcome is TernaryOutcome.DENIED:
            return DecisionInteractionDiscoveryResult(
                DecisionInteractionDiscoveryOutcome.AUTHORITY_DENIED
            )
        if (
            authority.outcome is not TernaryOutcome.PERMITTED
            or authority.authority_reference is None
        ):
            return DecisionInteractionDiscoveryResult(
                DecisionInteractionDiscoveryOutcome.AUTHORITY_UNKNOWN
            )
        return DecisionInteractionDiscoveryResult(
            DecisionInteractionDiscoveryOutcome.AVAILABLE,
            page=self._catalogue.list_decision_subjects(
                page=page,
                page_size=page_size,
                search=search,
            ),
        )
