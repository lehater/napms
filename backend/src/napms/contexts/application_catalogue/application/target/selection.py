from dataclasses import dataclass
from uuid import UUID

from napms.contexts.application_catalogue.application.target.ports import (
    TargetApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.domain.target_model import DeploymentInteraction


@dataclass(slots=True)
class ReadDeploymentInteraction:
    """Resolve current Deployment Interaction state for lifecycle commands."""

    catalogue: TargetApplicationCatalogueRepository

    def get(self, deployment_interaction_id: UUID) -> DeploymentInteraction | None:
        return self.catalogue.get_deployment_interaction(deployment_interaction_id)
