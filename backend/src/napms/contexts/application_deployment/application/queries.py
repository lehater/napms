from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from uuid import UUID

from napms.contexts.application_deployment.domain.model import ComponentDeployment


class DeploymentSortField(str, Enum):
    DEPLOYMENT_REF = "deploymentRef"
    COMPONENT_REF = "componentRef"
    RESOURCE_REF = "resourceRef"


class SortDirection(str, Enum):
    ASC = "asc"
    DESC = "desc"


@dataclass(frozen=True)
class DeploymentCatalogueQuery:
    search: str | None = None
    component_ref: UUID | None = None
    resource_ref: UUID | None = None
    sort_by: DeploymentSortField = DeploymentSortField.DEPLOYMENT_REF
    sort_direction: SortDirection = SortDirection.ASC
    page: int = 1
    page_size: int = 25

    def __post_init__(self) -> None:
        if self.page < 1:
            raise ValueError("page must be >= 1")
        if not 1 <= self.page_size <= 100:
            raise ValueError("page_size must be between 1 and 100")


@dataclass(frozen=True)
class DeploymentCataloguePage:
    items: tuple[ComponentDeployment, ...]
    total: int
    page: int
    page_size: int
