from datetime import datetime
from typing import Protocol
from uuid import UUID

from napms.application_catalogue.domain.model import (
    DcsRevision,
    DeploymentResourceBinding,
)


class CataloguePersistenceError(Exception):
    """Catalogue persistence failed without a trustworthy semantic result."""


class ApplicationCatalogueRepository(Protocol):
    def get_dcs_revision(self, revision_id: UUID) -> DcsRevision | None: ...

    def list_dcs_revisions(
        self,
        *,
        offset: int,
        limit: int,
    ) -> tuple[DcsRevision, ...]: ...

    def find_effective_bindings(
        self,
        *,
        component_deployment_id: UUID,
        as_of: datetime,
    ) -> tuple[DeploymentResourceBinding, ...]: ...
