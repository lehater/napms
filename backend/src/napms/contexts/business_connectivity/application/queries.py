from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from napms.contexts.business_connectivity.domain.model import BusinessProcess


class BusinessProcessSortField(str, Enum):
    NAME = "name"
    PROCESS_REF = "processRef"
    CRITICALITY_LABEL = "criticalityLabel"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True)
class BusinessProcessCatalogueQuery:
    search: str | None = None
    criticality_label: str | None = None
    organization_external_reference: str | None = None
    sort_by: BusinessProcessSortField = BusinessProcessSortField.NAME
    sort_direction: SortDirection = SortDirection.ASC
    page: int = 1
    page_size: int = 25

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not 1 <= self.page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")


@dataclass(frozen=True)
class BusinessProcessCataloguePage:
    items: tuple[BusinessProcess, ...]
    total: int
    page: int
    page_size: int
