from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from napms.contexts.application_deployment.application.ports import DeploymentNotFound
from napms.contexts.application_deployment.application.queries import (
    DeploymentCataloguePage,
    DeploymentCatalogueQuery,
    DeploymentSortField,
    SortDirection,
)
from napms.contexts.application_deployment.domain.model import ComponentDeployment
from napms.contexts.authority_management.domain.model import Principal
from napms.platform.http.deployment_connectivity import router


class Deployments:
    def __init__(self, items: tuple[ComponentDeployment, ...]) -> None:
        self.items = items
        self.received: DeploymentCatalogueQuery | None = None

    def list_component_deployments(
        self,
        query: DeploymentCatalogueQuery,
    ) -> DeploymentCataloguePage:
        self.received = query
        return DeploymentCataloguePage(
            self.items,
            len(self.items),
            query.page,
            query.page_size,
        )

    def resolve_component_deployment(self, deployment_ref: UUID) -> ComponentDeployment:
        for item in self.items:
            if item.deployment_ref == deployment_ref:
                return item
        raise DeploymentNotFound(str(deployment_ref))


class Connectivity:
    pass


def client(deployments: Deployments) -> TestClient:
    app = FastAPI()
    app.include_router(
        router(
            deployments=deployments,
            connectivity=Connectivity(),
            identity=lambda: Principal(
                "subject:alice",
                frozenset({"deployment.read"}),
                (),
            ),
        )
    )
    return TestClient(app)


def test_deployment_catalogue_query_maps_http_params_to_application_query() -> None:
    item = ComponentDeployment(UUID(int=101), UUID(int=201), UUID(int=301))
    deployments = Deployments((item,))
    response = client(deployments).get(
        (
            "/v1/deployments?search=%200067%20"
            f"&componentRef={UUID(int=201)}&resourceRef={UUID(int=301)}"
            "&sortBy=resourceRef&sortDirection=desc&page=2&pageSize=10"
        )
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "deploymentRef": str(item.deployment_ref),
                "componentRef": str(item.component_ref),
                "resourceRef": str(item.resource_ref),
            }
        ],
        "total": 1,
        "page": 2,
        "pageSize": 10,
    }
    assert deployments.received == DeploymentCatalogueQuery(
        search="0067",
        component_ref=UUID(int=201),
        resource_ref=UUID(int=301),
        sort_by=DeploymentSortField.RESOURCE_REF,
        sort_direction=SortDirection.DESC,
        page=2,
        page_size=10,
    )


def test_deployment_detail_returns_entity_or_not_found() -> None:
    item = ComponentDeployment(UUID(int=101), UUID(int=201), UUID(int=301))
    http = client(Deployments((item,)))

    detail = http.get(f"/v1/deployments/{item.deployment_ref}")
    missing = http.get(f"/v1/deployments/{UUID(int=999)}")

    assert detail.status_code == 200
    assert detail.json()["componentRef"] == str(item.component_ref)
    assert detail.json()["resourceRef"] == str(item.resource_ref)
    assert missing.status_code == 404
