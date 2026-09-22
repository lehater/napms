from uuid import UUID

import pytest

from napms.contexts.application_communication_catalogue.domain.model import Component
from napms.contexts.application_deployment.application.ports import DeploymentNotFound
from napms.contexts.application_deployment.application.queries import (
    DeploymentCataloguePage,
    DeploymentCatalogueQuery,
    DeploymentSortField,
    SortDirection,
)
from napms.contexts.application_deployment.application.service import ApplicationDeploymentService
from napms.contexts.application_deployment.domain.model import ComponentDeployment
from napms.contexts.resource_catalogue.domain.model import Resource


class Components:
    def __init__(self, component: Component | None) -> None:
        self.component = component

    def resolve(self, component_ref: UUID) -> Component | None:
        if self.component is not None and self.component.component_ref == component_ref:
            return self.component
        return None


class Resources:
    def __init__(self, resource: Resource | None) -> None:
        self.resource = resource

    def resolve_resource(self, resource_ref: UUID) -> Resource | None:
        if self.resource is not None and self.resource.resource_ref == resource_ref:
            return self.resource
        return None


class Deployments:
    def __init__(self) -> None:
        self.values: dict[UUID, ComponentDeployment] = {}
        self.received_query: DeploymentCatalogueQuery | None = None

    def add(self, deployment: ComponentDeployment) -> None:
        self.values[deployment.deployment_ref] = deployment

    def query_deployments(
        self,
        query: DeploymentCatalogueQuery,
    ) -> DeploymentCataloguePage:
        self.received_query = query
        values = tuple(self.values.values())
        return DeploymentCataloguePage(values, len(values), query.page, query.page_size)

    def resolve_deployment(self, deployment_ref: UUID) -> ComponentDeployment | None:
        return self.values.get(deployment_ref)


def test_deployment_identity_is_independent_from_resource_address() -> None:
    component = Component(component_ref=UUID(int=1), name="API")
    resource = Resource.register(
        resource_ref=UUID(int=2),
        display_name="node-a",
        authority_scope_ref="scope:a",
    )
    service = ApplicationDeploymentService(
        deployments=Deployments(),
        components=Components(component),
        resources=Resources(resource),
        new_ref=lambda: UUID(int=3),
    )

    deployment = service.register_component_deployment(
        component_ref=component.component_ref,
        resource_ref=resource.resource_ref,
    )

    assert deployment.deployment_ref == UUID(int=3)
    assert deployment.component_ref == UUID(int=1)
    assert deployment.resource_ref == UUID(int=2)


def test_missing_owner_reference_is_rejected_before_persistence() -> None:
    service = ApplicationDeploymentService(
        deployments=Deployments(),
        components=Components(None),
        resources=Resources(None),
        new_ref=lambda: UUID(int=3),
    )

    with pytest.raises(DeploymentNotFound):
        service.register_component_deployment(
            component_ref=UUID(int=1),
            resource_ref=UUID(int=2),
        )


def test_deployment_catalogue_query_is_delegated_without_reinterpretation() -> None:
    deployments = Deployments()
    deployment = ComponentDeployment(
        deployment_ref=UUID(int=3),
        component_ref=UUID(int=1),
        resource_ref=UUID(int=2),
    )
    deployments.add(deployment)
    service = ApplicationDeploymentService(
        deployments=deployments,
        components=Components(None),
        resources=Resources(None),
    )
    query = DeploymentCatalogueQuery(
        search="0003",
        component_ref=UUID(int=1),
        resource_ref=UUID(int=2),
        sort_by=DeploymentSortField.RESOURCE_REF,
        sort_direction=SortDirection.DESC,
        page=2,
        page_size=10,
    )

    result = service.list_component_deployments(query)

    assert deployments.received_query == query
    assert result.items == (deployment,)
    assert result.total == 1
    assert result.page == 2
    assert result.page_size == 10
