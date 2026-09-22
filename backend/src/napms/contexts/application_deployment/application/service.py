from collections.abc import Callable
from uuid import UUID, uuid4

from napms.contexts.application_communication_catalogue.application.ports import ComponentResolver
from napms.contexts.application_deployment.application.ports import (
    ComponentDeploymentRepository,
    DeploymentNotFound,
)
from napms.contexts.application_deployment.application.queries import (
    DeploymentCataloguePage,
    DeploymentCatalogueQuery,
)
from napms.contexts.application_deployment.domain.model import ComponentDeployment
from napms.contexts.resource_catalogue.application.ports import ResourceResolver


class ApplicationDeploymentService:
    def __init__(
        self,
        *,
        deployments: ComponentDeploymentRepository,
        components: ComponentResolver,
        resources: ResourceResolver,
        new_ref: Callable[[], UUID] = uuid4,
    ) -> None:
        self._deployments = deployments
        self._components = components
        self._resources = resources
        self._new_ref = new_ref

    def list_component_deployments(
        self,
        query: DeploymentCatalogueQuery,
    ) -> DeploymentCataloguePage:
        return self._deployments.query_deployments(query)

    def register_component_deployment(
        self,
        *,
        component_ref: UUID,
        resource_ref: UUID,
    ) -> ComponentDeployment:
        if self._components.resolve(component_ref) is None:
            raise DeploymentNotFound(str(component_ref))
        if self._resources.resolve_resource(resource_ref) is None:
            raise DeploymentNotFound(str(resource_ref))
        deployment = ComponentDeployment(
            deployment_ref=self._new_ref(),
            component_ref=component_ref,
            resource_ref=resource_ref,
        )
        self._deployments.add(deployment)
        return deployment

    def resolve_component_deployment(
        self,
        deployment_ref: UUID,
    ) -> ComponentDeployment:
        deployment = self._deployments.resolve_deployment(deployment_ref)
        if deployment is None:
            raise DeploymentNotFound(str(deployment_ref))
        return deployment
