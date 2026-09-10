from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from napms.application_catalogue.domain.communication import AuthoredDcsTrafficAlternative
from napms.application_catalogue.domain.model import Application, CatalogueInvariantError, Component
from napms.application_catalogue.domain.target_model import (
    ApplicationDeployment,
    DeploymentInteractionSide,
    InteractionDefinition,
)


@dataclass(frozen=True, slots=True)
class TargetPage:
    offset: int
    limit: int
    total: int

    def __post_init__(self) -> None:
        if self.offset < 0:
            raise CatalogueInvariantError("offset must be >= 0")
        if not 1 <= self.limit <= 200:
            raise CatalogueInvariantError("limit must be within 1..200")
        if self.total < 0:
            raise CatalogueInvariantError("total must be >= 0")


@dataclass(frozen=True, slots=True)
class ApplicationDefinitionSummary:
    application: Application
    component_count: int
    interaction_count: int
    deployment_count: int


@dataclass(frozen=True, slots=True)
class InteractionDefinitionSummary:
    interaction: InteractionDefinition
    source_component_name: str
    destination_component_name: str
    active_deployment_count: int


@dataclass(frozen=True, slots=True)
class ApplicationDeploymentSummary:
    deployment: ApplicationDeployment
    application_name: str
    selected_interaction_count: int
    available_interaction_count: int


@dataclass(frozen=True, slots=True)
class DeploymentConnectivityRow:
    deployment_interaction_id: UUID
    interaction_definition_id: UUID
    source_component_id: UUID
    source_component_name: str
    source_resource_count: int
    destination_component_id: UUID
    destination_component_name: str
    destination_resource_count: int
    traffic_alternatives: tuple[AuthoredDcsTrafficAlternative, ...]


@dataclass(frozen=True, slots=True)
class ResourceSetMember:
    resource_reference: str
    display_name: str | None = None
    scope_references: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DefinitionSummaryPage:
    items: tuple[ApplicationDefinitionSummary, ...]
    page: TargetPage


@dataclass(frozen=True, slots=True)
class ComponentPage:
    items: tuple[Component, ...]
    page: TargetPage


@dataclass(frozen=True, slots=True)
class InteractionDefinitionPage:
    items: tuple[InteractionDefinitionSummary, ...]
    page: TargetPage


@dataclass(frozen=True, slots=True)
class ApplicationDeploymentPage:
    items: tuple[ApplicationDeploymentSummary, ...]
    page: TargetPage


@dataclass(frozen=True, slots=True)
class DeploymentConnectivityPage:
    items: tuple[DeploymentConnectivityRow, ...]
    page: TargetPage
    as_of: datetime


@dataclass(frozen=True, slots=True)
class ResourceSetPage:
    items: tuple[ResourceSetMember, ...]
    page: TargetPage
    as_of: datetime


class TargetApplicationCatalogueReadPort(Protocol):
    def list_definitions(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
        domain: str | None,
        owner_reference: str | None,
        sort: str,
    ) -> DefinitionSummaryPage: ...

    def get_definition(self, *, application_id: UUID) -> Application | None: ...

    def list_components(
        self,
        *,
        application_id: UUID,
        offset: int,
        limit: int,
        search: str | None,
        component_type: str | None,
        sort: str,
    ) -> ComponentPage: ...

    def list_interaction_definitions(
        self,
        *,
        application_id: UUID,
        offset: int,
        limit: int,
        search: str | None,
        source_component_id: UUID | None,
        destination_component_id: UUID | None,
        protocol: str | None,
        sort: str,
    ) -> InteractionDefinitionPage: ...

    def list_application_deployments(
        self,
        *,
        application_id: UUID | None,
        offset: int,
        limit: int,
        search: str | None,
        company_reference: str | None,
        environment: str | None,
        scope_reference: str | None,
        sort: str,
    ) -> ApplicationDeploymentPage: ...

    def get_application_deployment(
        self,
        *,
        application_deployment_id: UUID,
    ) -> ApplicationDeployment | None: ...

    def list_available_interactions_for_deployment(
        self,
        *,
        application_deployment_id: UUID,
        offset: int,
        limit: int,
        search: str | None,
        source_component_id: UUID | None,
        destination_component_id: UUID | None,
        protocol: str | None,
        sort: str,
    ) -> InteractionDefinitionPage: ...

    def list_deployment_connectivity(
        self,
        *,
        application_deployment_id: UUID,
        as_of: datetime,
        offset: int,
        limit: int,
        search: str | None,
        source_component_id: UUID | None,
        destination_component_id: UUID | None,
        protocol: str | None,
        sort: str,
    ) -> DeploymentConnectivityPage: ...

    def list_resource_set(
        self,
        *,
        deployment_interaction_id: UUID,
        side: DeploymentInteractionSide,
        as_of: datetime,
        offset: int,
        limit: int,
        search: str | None,
        scope_reference: str | None,
        sort: str,
    ) -> ResourceSetPage: ...


_ALLOWED_SORTS = {
    "name",
    "domain",
    "owner",
    "type",
    "source",
    "destination",
    "application",
    "company",
    "environment",
    "scope",
    "traffic",
    "resource",
}


def normalize_bounded_query(
    *,
    offset: int,
    limit: int,
    search: str | None,
    sort: str,
) -> tuple[int, int, str | None, str]:
    if offset < 0:
        raise CatalogueInvariantError("offset must be >= 0")
    if not 1 <= limit <= 200:
        raise CatalogueInvariantError("limit must be within 1..200")
    normalized_search = search.strip() if search and search.strip() else None
    normalized_sort = sort.strip().lower() if sort else ""
    descending = normalized_sort.startswith("-")
    sort_key = normalized_sort[1:] if descending else normalized_sort
    if sort_key not in _ALLOWED_SORTS:
        raise CatalogueInvariantError("unsupported target catalogue sort")
    return offset, limit, normalized_search, ("-" if descending else "") + sort_key


def require_as_of(as_of: datetime) -> datetime:
    if as_of.tzinfo is None or as_of.utcoffset() is None:
        raise CatalogueInvariantError("as_of must be offset-aware")
    return as_of
