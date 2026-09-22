from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from napms.contexts.resource_catalogue.domain.model import Resource


class ResourceSortField(str, Enum):
    DISPLAY_NAME = "displayName"
    RESOURCE_REF = "resourceRef"
    AUTHORITY_SCOPE_REF = "authorityScopeRef"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True)
class ResourceCatalogueQuery:
    search: str | None = None
    authority_scope_ref: str | None = None
    site_ref: UUID | None = None
    sort_by: ResourceSortField = ResourceSortField.DISPLAY_NAME
    sort_direction: SortDirection = SortDirection.ASC
    page: int = 1
    page_size: int = 25

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not 1 <= self.page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")


@dataclass(frozen=True)
class ResourceCataloguePage:
    items: tuple[Resource, ...]
    total: int
    page: int
    page_size: int
