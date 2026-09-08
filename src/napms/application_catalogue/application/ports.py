from datetime import datetime
from typing import Protocol
from uuid import UUID

from napms.application_catalogue.domain.model import (
    ComponentDeployment,
    DcsRevision,
    DeploymentResourceBinding,
)


class CataloguePersistenceError(Exception):
    """Catalogue persistence failed without a trustworthy semantic result."""


class ApplicationCatalogueRepository(Protocol):
    def get_dcs_revision(self, revision_id: UUID) -> DcsRevision | None: ...

    def get_dcs_revisions(
        self,
        revision_ids: tuple[UUID, ...],
    ) -> tuple[DcsRevision, ...]: ...

    def get_component_deployments(
        self,
        deployment_ids: tuple[UUID, ...],
    ) -> tuple[ComponentDeployment, ...]: ...

    def list_dcs_revisions(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> tuple[DcsRevision, ...]: ...

    def find_effective_bindings(
        self,
        *,
        component_deployment_id: UUID,
        as_of: datetime,
    ) -> tuple[DeploymentResourceBinding, ...]: ...
