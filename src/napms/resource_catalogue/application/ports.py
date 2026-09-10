from datetime import datetime
from typing import Protocol

from napms.resource_catalogue.domain.model import (
    ResourceRealizationVersion,
    ResourceScopeAffiliation,
)


class ResourceCataloguePersistenceError(Exception):
    """Resource Catalogue persistence failed without a trustworthy result."""


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
