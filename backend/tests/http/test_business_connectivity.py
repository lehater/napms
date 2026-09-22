from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from napms.contexts.authority_management.domain.model import Principal
from napms.contexts.business_connectivity.application.ports import (
    BusinessConnectivityNotFound,
)
from napms.contexts.business_connectivity.application.queries import (
    BusinessProcessCataloguePage,
    BusinessProcessCatalogueQuery,
    BusinessProcessSortField,
    SortDirection,
)
from napms.contexts.business_connectivity.domain.model import BusinessProcess
from napms.platform.http.deployment_connectivity import router


class Deployments:
    pass


class Connectivity:
    def __init__(self, items: tuple[BusinessProcess, ...]) -> None:
        self.items = items
        self.received_query: BusinessProcessCatalogueQuery | None = None

    def list_business_processes(
        self,
        query: BusinessProcessCatalogueQuery,
    ) -> BusinessProcessCataloguePage:
        self.received_query = query
        return BusinessProcessCataloguePage(
            items=self.items,
            total=len(self.items),
            page=query.page,
            page_size=query.page_size,
        )

    def resolve_business_process(self, process_ref: UUID) -> BusinessProcess:
        for item in self.items:
            if item.process_ref == process_ref:
                return item
        raise BusinessConnectivityNotFound(str(process_ref))


def client(connectivity: Connectivity) -> TestClient:
    app = FastAPI()
    app.include_router(
        router(
            deployments=Deployments(),
            connectivity=connectivity,
            identity=lambda: Principal(
                "subject:alice",
                frozenset({"business.read"}),
                (),
            ),
        )
    )
    return TestClient(app)


def test_business_process_catalogue_query_maps_http_params_to_application_query() -> None:
    process = BusinessProcess.register(
        process_ref=UUID(int=101),
        name="Orders",
        criticality_label="HIGH",
    ).set_responsible_organization(
        external_reference="ORG-1",
        display_name="Operations",
    )
    connectivity = Connectivity((process,))
    response = client(connectivity).get(
        "/v1/processes?search=%20Orders%20&criticalityLabel=HIGH"
        "&organizationExternalReference=ORG-1&sortBy=criticalityLabel"
        "&sortDirection=desc&page=2&pageSize=10"
    )

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "processRef": str(process.process_ref),
                "name": "Orders",
                "description": None,
                "organizationExternalReference": "ORG-1",
                "organizationDisplayName": "Operations",
                "criticalityLabel": "HIGH",
                "version": 2,
                "needs": [],
            }
        ],
        "total": 1,
        "page": 2,
        "pageSize": 10,
    }
    assert connectivity.received_query == BusinessProcessCatalogueQuery(
        search="Orders",
        criticality_label="HIGH",
        organization_external_reference="ORG-1",
        sort_by=BusinessProcessSortField.CRITICALITY_LABEL,
        sort_direction=SortDirection.DESC,
        page=2,
        page_size=10,
    )


def test_business_process_detail_resolves_directly_or_returns_not_found() -> None:
    process = BusinessProcess.register(process_ref=UUID(int=101), name="Orders")
    http = client(Connectivity((process,)))

    detail = http.get(f"/v1/processes/{process.process_ref}")
    missing = http.get(f"/v1/processes/{UUID(int=999)}")

    assert detail.status_code == 200
    assert detail.json()["processRef"] == str(process.process_ref)
    assert detail.json()["name"] == "Orders"
    assert missing.status_code == 404
