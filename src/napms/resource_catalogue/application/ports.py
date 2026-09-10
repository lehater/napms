from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from napms.resource_catalogue.domain.model import (
    ResourceRealizationVersion,
    ResourceScopeAffiliation,
)


RESOURCE_CATALOGUE_CURATION_ACTION = "CurateResourceCatalogue"
RESOURCE_CATALOGUE_AUTHORITY_SCOPE = "resource-catalogue"


class ResourceCataloguePersistenceError(Exception):
    """Resource Catalogue persistence failed without a trustworthy result."""


class ResourceCatalogueAuthorityOutcome(str, Enum):
    PERMITTED = "Permitted"
    DENIED = "Denied"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class ResourceCatalogueAuthorityCheck:
    outcome: ResourceCatalogueAuthorityOutcome
    authority_reference: str | None = None


class ResourceCatalogueCurationAuthorityPort(Protocol):
    def check_curation(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> ResourceCatalogueAuthorityCheck: ...


class ResourceCatalogueRepository(Protocol):
    def find_effective_realizations(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> tuple[ResourceRealizationVersion, ...]: ...

    def has_realization_facts(self, *, resource_reference: str) -> bool: ...

    def find_effective_realizations_for_resources(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
    ) -> tuple[ResourceRealizationVersion, ...]: ...

    def find_resources_with_realization_facts(
        self,
        *,
        resource_references: tuple[str, ...],
    ) -> tuple[str, ...]: ...

    def find_effective_realizations_by_address(
        self,
        *,
        technical_address: str,
        as_of: datetime,
    ) -> tuple[ResourceRealizationVersion, ...]: ...

    def has_realization_facts_for_address(
        self,
        *,
        technical_address: str,
    ) -> bool: ...


class ResourceScopeAffiliationRepository(Protocol):
    def list_effective_for_scope(
        self,
        *,
        responsibility_scope: str,
        as_of: datetime,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> tuple[ResourceScopeAffiliation, ...]: ...
