from datetime import datetime
from uuid import UUID

from napms.application_catalogue.adapters.postgres.curation_repository import (
    PostgresApplicationCatalogueCurationRepository,
)
from napms.application_catalogue.adapters.postgres.repository import (
    PostgresApplicationCatalogueRepository,
)
from napms.application_catalogue.domain.model import (
    Application,
    Component,
    ComponentDeployment,
    DcsRevision,
    DeploymentResourceBinding,
)


class PostgresApplicationCatalogueDetailRepository:
    """ACC-owned read projection composed from curation and semantic readers."""

    def __init__(
        self,
        *,
        curation: PostgresApplicationCatalogueCurationRepository,
        semantic: PostgresApplicationCatalogueRepository,
    ) -> None:
        self._curation = curation
        self._semantic = semantic

    def get_application(self, application_id: UUID) -> Application | None:
        return self._curation.get_application(application_id)

    def list_components(
        self,
        *,
        application_id: UUID,
        include_retired: bool,
    ) -> tuple[Component, ...]:
        return self._curation.list_components(
            application_id=application_id,
            include_retired=include_retired,
        )

    def list_component_deployments(
        self,
        *,
        component_id: UUID,
        include_retired: bool,
    ) -> tuple[ComponentDeployment, ...]:
        return self._curation.list_component_deployments(
            component_id=component_id,
            include_retired=include_retired,
        )

    def list_effective_bindings_for_deployments(
        self,
        *,
        deployment_ids: tuple[UUID, ...],
        as_of: datetime,
    ) -> tuple[DeploymentResourceBinding, ...]:
        return self._semantic.find_effective_bindings_for_components(
            component_deployment_ids=deployment_ids,
            as_of=as_of,
        )

    def list_dcs_revisions_for_deployments(
        self,
        *,
        deployment_ids: tuple[UUID, ...],
    ) -> tuple[DcsRevision, ...]:
        return self._semantic.list_dcs_revisions_for_components(
            component_deployment_ids=deployment_ids,
        )
