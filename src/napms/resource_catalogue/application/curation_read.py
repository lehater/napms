from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from napms.resource_catalogue.application._temporal_curation import is_aware
from napms.resource_catalogue.domain.model import (
    Resource,
    ResourceCatalogueInvariantError,
    ResourceRealizationVersion,
    ResourceScopeAffiliation,
)
from napms.resource_catalogue.domain.responsibility import ResourceResponsibility


@dataclass(frozen=True, slots=True)
class ResourceCatalogueListItem:
    resource: Resource
    has_effective_realization: bool
    has_effective_scope_affiliation: bool
    has_effective_responsibility: bool
    has_effective_contact: bool


@dataclass(frozen=True, slots=True)
class ResourceCataloguePage:
    items: tuple[ResourceCatalogueListItem, ...]
    page: int
    page_size: int
    has_more: bool
    as_of: datetime
    responsibility_scope: str | None


@dataclass(frozen=True, slots=True)
class ResourceCatalogueDetail:
    resource: Resource
    effective_realizations: tuple[ResourceRealizationVersion, ...]
    effective_scope_affiliations: tuple[ResourceScopeAffiliation, ...]
    effective_responsibilities: tuple[ResourceResponsibility, ...]
    as_of: datetime


class ResourceCatalogueListReadPort(Protocol):
    def list_resources(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
        include_retired: bool,
        responsibility_scope: str | None,
        as_of: datetime,
    ) -> tuple[ResourceCatalogueListItem, ...]: ...


class ResourceCatalogueDetailReadPort(Protocol):
    def get_resource(self, resource_reference: str) -> Resource | None: ...

    def list_effective_realizations(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> tuple[ResourceRealizationVersion, ...]: ...

    def list_effective_scope_affiliations(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> tuple[ResourceScopeAffiliation, ...]: ...

    def list_effective_responsibilities(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> tuple[ResourceResponsibility, ...]: ...


class ListResourceCatalogue:
    def __init__(self, *, catalogue: ResourceCatalogueListReadPort) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        *,
        page: int,
        page_size: int,
        as_of: datetime,
        search: str | None = None,
        include_retired: bool = False,
        responsibility_scope: str | None = None,
    ) -> ResourceCataloguePage:
        if page < 1:
            raise ResourceCatalogueInvariantError("page must be >= 1")
        if page_size < 1 or page_size > 200:
            raise ResourceCatalogueInvariantError("page_size must be in [1, 200]")
        if not is_aware(as_of):
            raise ResourceCatalogueInvariantError("as_of must be offset-aware")

        normalized_search = search.strip() if search is not None else None
        if normalized_search == "":
            normalized_search = None
        normalized_scope = (
            responsibility_scope.strip()
            if responsibility_scope is not None
            else None
        )
        if normalized_scope == "":
            normalized_scope = None

        rows = self._catalogue.list_resources(
            offset=(page - 1) * page_size,
            limit=page_size + 1,
            search=normalized_search,
            include_retired=include_retired,
            responsibility_scope=normalized_scope,
            as_of=as_of,
        )
        return ResourceCataloguePage(
            items=rows[:page_size],
            page=page,
            page_size=page_size,
            has_more=len(rows) > page_size,
            as_of=as_of,
            responsibility_scope=normalized_scope,
        )


class ReadResourceCatalogueDetail:
    def __init__(self, *, catalogue: ResourceCatalogueDetailReadPort) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> ResourceCatalogueDetail | None:
        reference = resource_reference.strip() if resource_reference else ""
        if not reference:
            raise ResourceCatalogueInvariantError(
                "resource_reference must be non-empty"
            )
        if not is_aware(as_of):
            raise ResourceCatalogueInvariantError("as_of must be offset-aware")

        resource = self._catalogue.get_resource(reference)
        if resource is None:
            return None

        realizations = tuple(
            item
            for item in self._catalogue.list_effective_realizations(
                resource_reference=reference,
                as_of=as_of,
            )
            if item.is_effective_at(as_of)
        )
        affiliations = tuple(
            item
            for item in self._catalogue.list_effective_scope_affiliations(
                resource_reference=reference,
                as_of=as_of,
            )
            if item.is_effective_at(as_of)
        )
        responsibilities = tuple(
            item
            for item in self._catalogue.list_effective_responsibilities(
                resource_reference=reference,
                as_of=as_of,
            )
            if item.is_effective_at(as_of)
        )

        return ResourceCatalogueDetail(
            resource=resource,
            effective_realizations=tuple(
                sorted(realizations, key=lambda item: item.fact_reference)
            ),
            effective_scope_affiliations=tuple(
                sorted(
                    affiliations,
                    key=lambda item: (
                        item.responsibility_scope,
                        item.affiliation_reference,
                    ),
                )
            ),
            effective_responsibilities=tuple(
                sorted(
                    responsibilities,
                    key=lambda item: (
                        item.role.value,
                        item.display_name,
                        item.assignment_reference,
                    ),
                )
            ),
            as_of=as_of,
        )
