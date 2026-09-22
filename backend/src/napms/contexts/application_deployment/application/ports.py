from typing import Protocol
from uuid import UUID

from napms.contexts.application_deployment.application.queries import (
    DeploymentCataloguePage,
    DeploymentCatalogueQuery,
)
from napms.contexts.application_deployment.domain.model import ComponentDeployment


class DeploymentNotFound(Exception):
    pass


class ComponentDeploymentRepository(Protocol):
    def add(self, deployment: ComponentDeployment) -> None: ...

    def query_deployments(self, query: DeploymentCatalogueQuery) -> DeploymentCataloguePage: ...

    def resolve_deployment(self, deployment_ref: UUID) -> ComponentDeployment | None: ...


class ComponentDeploymentResolver(Protocol):
    def resolve_deployment(self, deployment_ref: UUID) -> ComponentDeployment | None: ...
