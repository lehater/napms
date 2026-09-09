from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.connectivity_requirements.application.inventory_summary import (
    ConnectivityRequirementInventorySnapshot,
)
from napms.connectivity_requirements.domain.model import (
    ConnectivityRequirement,
    RequiredSemanticInteraction,
    RequirementSemanticKey,
)


class RequirementAuthorityAction(str, Enum):
    DECLARE = "DeclareConnectivityRequirement"
    READ = "ReadConnectivityRequirement"
    SET_APPLICABILITY = "SetConnectivityRequirementApplicability"
    SET_JUSTIFICATION = "SetConnectivityRequirementJustification"
    RETIRE = "RetireConnectivityRequirement"


class TernaryOutcome(str, Enum):
    PERMITTED = "Permitted"
    DENIED = "Denied"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class RequirementAuthorityCheck:
    outcome: TernaryOutcome
    authority_reference: str | None = None


class InteractionOutcome(str, Enum):
    VALID = "Valid"
    INVALID = "Invalid"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class RequirementInteractionCheck:
    outcome: InteractionOutcome
    identity: RequiredSemanticInteraction | None = None
    provenance_reference: str | None = None


@dataclass(frozen=True, slots=True)
class RequirementScopeOptions:
    permitted_scopes: tuple[str, ...]
    ambiguous_scopes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class RequirementInteractionPage:
    interactions: tuple[RequiredSemanticInteraction, ...]
    page: int
    page_size: int
    has_more: bool


class RequirementPersistenceError(Exception):
    """Persistence failed without establishing application success."""


class RequirementCommitOutcomeUnknown(RequirementPersistenceError):
    """Commit acknowledgement failed; authoritative outcome is uncertain."""


class ActiveRequirementSemanticConflict(RequirementPersistenceError):
    """Another active Requirement won the semantic uniqueness race."""


class RequirementVersionConflict(RequirementPersistenceError):
    """The aggregate changed since the caller loaded its expected version."""


class RequirementAuthorityPort(Protocol):
    def check(
        self,
        *,
        actor_id: str,
        action: RequirementAuthorityAction,
        scope: str,
        effective_time: datetime,
    ) -> RequirementAuthorityCheck: ...


class RequirementDeclarationScopeDiscoveryPort(Protocol):
    def list_effective_declaration_scopes(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> RequirementScopeOptions: ...


class RequirementReadScopeDiscoveryPort(Protocol):
    def list_effective_read_scopes(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> RequirementScopeOptions: ...


class RequirementInteractionCataloguePort(Protocol):
    def validate_required_interaction(
        self,
        *,
        identity: RequiredSemanticInteraction,
        effective_time: datetime,
    ) -> RequirementInteractionCheck: ...


class RequirementInteractionDiscoveryPort(Protocol):
    def list_required_interactions(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
    ) -> RequirementInteractionPage: ...


class ConnectivityRequirementRepository(Protocol):
    def find_active_by_semantic_key(
        self,
        key: RequirementSemanticKey,
    ) -> ConnectivityRequirement | None: ...

    def get_by_id(
        self,
        requirement_id: UUID,
    ) -> ConnectivityRequirement | None: ...

    def list_by_governance_scopes(
        self,
        scopes: tuple[str, ...],
        *,
        offset: int,
        limit: int,
    ) -> tuple[ConnectivityRequirement, ...]: ...

    def list_inventory_summaries(
        self,
        *,
        governance_scope: str,
        interactions: tuple[RequiredSemanticInteraction, ...],
    ) -> tuple[ConnectivityRequirementInventorySnapshot, ...]: ...

    def add(self, requirement: ConnectivityRequirement) -> None: ...

    def save(
        self,
        requirement: ConnectivityRequirement,
        *,
        expected_version: int,
    ) -> None: ...

    def commit(self) -> None: ...
