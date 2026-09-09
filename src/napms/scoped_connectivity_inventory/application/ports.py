from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.scoped_connectivity_inventory.application.model import (
    BoundComponentSnapshot,
    ComponentResourceBindingSnapshot,
    DecisionSummary,
    InteractionIdentity,
    InteractionSnapshot,
    PolicySummary,
    RequirementSummary,
    ResourceSnapshot,
)


class DependencyAvailability(str, Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"


class ScopeAdmissionOutcome(str, Enum):
    PERMITTED = "Permitted"
    DENIED = "Denied"
    UNKNOWN = "Unknown"
    AMBIGUOUS = "Ambiguous"


@dataclass(frozen=True, slots=True)
class ScopeAdmissionResult:
    outcome: ScopeAdmissionOutcome
    authority_reference: str | None = None


@dataclass(frozen=True, slots=True)
class ScopeDiscoveryResult:
    availability: DependencyAvailability
    permitted_scopes: tuple[str, ...] = ()
    ambiguous_scopes: tuple[str, ...] = ()


class ScopedConnectivityAuthorityPort(Protocol):
    def discover_scopes(
        self,
        *,
        actor_id: str,
        as_of: datetime,
    ) -> ScopeDiscoveryResult: ...

    def check_scope(
        self,
        *,
        actor_id: str,
        scope: str,
        as_of: datetime,
    ) -> ScopeAdmissionResult: ...


@dataclass(frozen=True, slots=True)
class LocalResourcePage:
    resources: tuple[ResourceSnapshot, ...]
    page: int
    page_size: int
    has_more: bool


@dataclass(frozen=True, slots=True)
class LocalResourceReadResult:
    availability: DependencyAvailability
    page: LocalResourcePage | None = None


@dataclass(frozen=True, slots=True)
class ResourceResolutionResult:
    availability: DependencyAvailability
    resources: tuple[ResourceSnapshot, ...] = ()


class ScopedResourcePort(Protocol):
    def list_local_resources(
        self,
        *,
        responsibility_scope: str,
        as_of: datetime,
        page: int,
        page_size: int,
        search: str | None,
    ) -> LocalResourceReadResult: ...

    def resolve_resources(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
    ) -> ResourceResolutionResult: ...


@dataclass(frozen=True, slots=True)
class BoundComponentReadResult:
    availability: DependencyAvailability
    items: tuple[BoundComponentSnapshot, ...] = ()


@dataclass(frozen=True, slots=True)
class InteractionReadResult:
    availability: DependencyAvailability
    items: tuple[InteractionSnapshot, ...] = ()


@dataclass(frozen=True, slots=True)
class ComponentResourceBindingReadResult:
    availability: DependencyAvailability
    items: tuple[ComponentResourceBindingSnapshot, ...] = ()


class ScopedCataloguePort(Protocol):
    def list_bound_components(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
    ) -> BoundComponentReadResult: ...

    def list_interactions_for_components(
        self,
        *,
        component_deployment_ids: tuple[UUID, ...],
    ) -> InteractionReadResult: ...

    def list_resource_bindings_for_components(
        self,
        *,
        component_deployment_ids: tuple[UUID, ...],
        as_of: datetime,
    ) -> ComponentResourceBindingReadResult: ...


@dataclass(frozen=True, slots=True)
class RequirementSummaryReadResult:
    availability: DependencyAvailability
    items: tuple[RequirementSummary, ...] = ()


class RequirementSummaryPort(Protocol):
    def summarize_requirements(
        self,
        *,
        responsibility_scope: str,
        identities: tuple[InteractionIdentity, ...],
        as_of: datetime,
    ) -> RequirementSummaryReadResult: ...


@dataclass(frozen=True, slots=True)
class DecisionSummaryReadResult:
    availability: DependencyAvailability
    items: tuple[DecisionSummary, ...] = ()


class DecisionSummaryPort(Protocol):
    def summarize_decisions(
        self,
        *,
        responsibility_scope: str,
        identities: tuple[InteractionIdentity, ...],
        as_of: datetime,
    ) -> DecisionSummaryReadResult: ...


@dataclass(frozen=True, slots=True)
class PolicySummaryReadResult:
    availability: DependencyAvailability
    items: tuple[PolicySummary, ...] = ()


class PolicySummaryPort(Protocol):
    def summarize_policy(
        self,
        *,
        identities: tuple[InteractionIdentity, ...],
        as_of: datetime,
    ) -> PolicySummaryReadResult: ...
