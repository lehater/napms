from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from napms.contexts.application_communication_catalogue.domain.model import Application


class ApplicationSortField(str, Enum):
    NAME = "name"
    APPLICATION_REF = "applicationRef"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True)
class ApplicationCatalogueQuery:
    search: str | None = None
    component_ref: UUID | None = None
    sort_by: ApplicationSortField = ApplicationSortField.NAME
    sort_direction: SortDirection = SortDirection.ASC
    page: int = 1
    page_size: int = 25

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not 1 <= self.page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")


@dataclass(frozen=True)
class ApplicationCataloguePage:
    items: tuple[Application, ...]
    total: int
    page: int
    page_size: int
