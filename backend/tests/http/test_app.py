from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from napms.contexts.access_policy.application.queries import (
    AccessRequestCataloguePage,
    AccessRequestCatalogueQuery,
    AccessRequestSortField,
    SortDirection as AccessRequestSortDirection,
)
from napms.contexts.access_policy.application.submission import AccessRequestSubmissionRejected
from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    AccessSubject,
    PermissionDecision,
    RequestAuthorityEvidence,
)
from napms.contexts.application_communication_catalogue.application.queries import (
    ApplicationCataloguePage,
    ApplicationCatalogueQuery,
    ApplicationSortField,
    SortDirection as ApplicationSortDirection,
)
from napms.contexts.application_communication_catalogue.domain.model import Application
from napms.contexts.authority_management.application.service import AuthorityForbidden
from napms.contexts.authority_management.domain.model import Principal
from napms.contexts.resource_catalogue.application.queries import (
    ResourceCataloguePage,
    ResourceCatalogueQuery,
    ResourceSortField,
    SortDirection,
)
from napms.contexts.resource_catalogue.domain.model import Resource
from napms.platform.http.app import HttpDependencies, create_app
from napms.platform.security.oidc import AuthenticationRejected, IdentityDependencyUnavailable


@dataclass
class Identity:
    result: Principal | Exception

    def validate_bearer(self, token: str) -> Principal:
        assert token == "token"
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


@dataclass
class Submitter:
    result: AccessRequest | Exception
    principal: Principal | None = None

    def submit(self, *, principal: Principal, **kwargs) -> AccessRequest:
        self.principal = principal
        if isinstance(self.result, Exception):
            raise self.result
        return self.result


def request() -> AccessRequest:
    now = datetime.now(timezone.utc)
    return AccessRequest.submit(
        request_ref=uuid4(),
        access_subject=AccessSubject(uuid4(), uuid4(), uuid4()),
        initial_need_ref=uuid4(),
        validated_business_process_version=1,
        submitter_subject="subject:alice",
        submitted_at=now,
        authority_evidence=(
            RequestAuthorityEvidence(uuid4(), "scope:a", "access.request", None, None, now),
        ),
    )


def body() -> dict[str, str]:
    return {
        "sourceDeploymentRef": str(uuid4()),
        "destinationDeploymentRef": str(uuid4()),
        "interactionRevisionRef": str(uuid4()),
        "needRef": str(uuid4()),
    }


def client(identity, submitter) -> TestClient:
    return TestClient(create_app(HttpDependencies(identity=identity, access_requests=submitter)))


def test_submit_access_request_uses_authenticated_principal() -> None:
    principal = Principal("subject:alice", frozenset(), ())
    submitter = Submitter(request())
    response = client(Identity(principal), submitter).post(
        "/v1/access-requests",
        headers={"Authorization": "Bearer token", "Idempotency-Key": "key-1"},
        json=body(),
    )
    assert response.status_code == 201
    assert submitter.principal is principal


def test_authentication_status_mapping() -> None:
    submitter = Submitter(request())
    assert (
        client(Identity(AuthenticationRejected()), submitter)
        .post(
            "/v1/access-requests",
            headers={"Authorization": "Bearer token", "Idempotency-Key": "key-1"},
            json=body(),
        )
        .status_code
        == 401
    )
    assert (
        client(Identity(IdentityDependencyUnavailable()), submitter)
        .post(
            "/v1/access-requests",
            headers={"Authorization": "Bearer token", "Idempotency-Key": "key-1"},
            json=body(),
        )
        .status_code
        == 503
    )


def test_submission_status_mapping_and_required_idempotency_key() -> None:
    principal = Principal("subject:alice", frozenset(), ())
    assert (
        client(Identity(principal), Submitter(AuthorityForbidden()))
        .post(
            "/v1/access-requests",
            headers={"Authorization": "Bearer token", "Idempotency-Key": "key-1"},
            json=body(),
        )
        .status_code
        == 403
    )
    assert (
        client(Identity(principal), Submitter(AccessRequestSubmissionRejected()))
        .post(
            "/v1/access-requests",
            headers={"Authorization": "Bearer token", "Idempotency-Key": "key-1"},
            json=body(),
        )
        .status_code
        == 422
    )
    assert (
        client(Identity(principal), Submitter(request()))
        .post(
            "/v1/access-requests",
            headers={"Authorization": "Bearer token"},
            json=body(),
        )
        .status_code
        == 422
    )


def test_submit_access_request_rejects_noncanonical_snake_case_body() -> None:
    principal = Principal("subject:alice", frozenset(), ())
    canonical = body()
    snake_case = {
        "source_deployment_ref": canonical["sourceDeploymentRef"],
        "destination_deployment_ref": canonical["destinationDeploymentRef"],
        "interaction_revision_ref": canonical["interactionRevisionRef"],
        "need_ref": canonical["needRef"],
    }
    response = client(Identity(principal), Submitter(request())).post(
        "/v1/access-requests",
        headers={"Authorization": "Bearer token", "Idempotency-Key": "key-1"},
        json=snake_case,
    )
    assert response.status_code == 422


@dataclass
class AccessReader:
    items: tuple[AccessRequest, ...]
    received: AccessRequestCatalogueQuery | None = None

    def query_requests(
        self,
        query: AccessRequestCatalogueQuery,
    ) -> AccessRequestCataloguePage:
        self.received = query
        return AccessRequestCataloguePage(
            items=self.items,
            total=len(self.items),
            page=query.page,
            page_size=query.page_size,
        )

    def get_request(self, request_ref):
        return next((item for item in self.items if item.request_ref == request_ref), None)


def test_access_request_read_endpoints_preserve_subject_and_outcome() -> None:
    principal = Principal("subject:alice", frozenset({"access.manage"}), ())
    item = request()
    app = create_app(
        HttpDependencies(
            identity=Identity(principal),
            access_requests=Submitter(item),
            access_request_reader=AccessReader((item,)),
        )
    )
    http = TestClient(app)
    headers = {"Authorization": "Bearer token"}
    catalogue = http.get("/v1/access-requests", headers=headers)
    detail = http.get(f"/v1/access-requests/{item.request_ref}", headers=headers)
    assert catalogue.status_code == 200
    assert detail.status_code == 200
    assert catalogue.json()["items"][0]["requestRef"] == str(item.request_ref)
    assert detail.json()["sourceDeploymentRef"] == str(item.access_subject.source_deployment_ref)
    assert detail.json()["decisionResult"] is None


def test_access_request_catalogue_query_maps_http_params_to_reader() -> None:
    principal = Principal("subject:alice", frozenset({"access.manage"}), ())
    item = request()
    reader = AccessReader((item,))
    app = create_app(
        HttpDependencies(
            identity=Identity(principal),
            access_requests=Submitter(item),
            access_request_reader=reader,
        )
    )
    http = TestClient(app)
    headers = {"Authorization": "Bearer token"}
    response = http.get(
        (
            "/v1/access-requests?search=%20request%20"
            f"&sourceDeploymentRef={item.access_subject.source_deployment_ref}"
            f"&destinationDeploymentRef={item.access_subject.destination_deployment_ref}"
            "&decisionResult=ALLOWED&sortBy=requestRef&sortDirection=desc"
            "&page=2&pageSize=10"
        ),
        headers=headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 1
    assert response.json()["page"] == 2
    assert response.json()["pageSize"] == 10
    assert reader.received == AccessRequestCatalogueQuery(
        search="request",
        source_deployment_ref=item.access_subject.source_deployment_ref,
        destination_deployment_ref=item.access_subject.destination_deployment_ref,
        decision_result=PermissionDecision.ALLOWED,
        sort_by=AccessRequestSortField.REQUEST_REF,
        sort_direction=AccessRequestSortDirection.DESC,
        page=2,
        page_size=10,
    )


def test_access_request_read_requires_read_permission() -> None:
    principal = Principal("subject:alice", frozenset(), ())
    item = request()
    app = create_app(
        HttpDependencies(
            identity=Identity(principal),
            access_requests=Submitter(item),
            access_request_reader=AccessReader((item,)),
        )
    )
    response = TestClient(app).get("/v1/access-requests", headers={"Authorization": "Bearer token"})
    assert response.status_code == 403


@dataclass
class ResourceReader:
    page: ResourceCataloguePage
    received: ResourceCatalogueQuery | None = None

    def list_resources(self, query: ResourceCatalogueQuery) -> ResourceCataloguePage:
        self.received = query
        return self.page


def test_resource_catalogue_query_maps_http_params_to_application_query() -> None:
    principal = Principal("subject:alice", frozenset({"resource.read"}), ())
    item = Resource.register(
        resource_ref=uuid4(),
        display_name="Edge",
        authority_scope_ref="scope:edge",
    )
    reader = ResourceReader(ResourceCataloguePage((item,), 1, 2, 10))
    http = TestClient(
        create_app(
            HttpDependencies(
                identity=Identity(principal),
                access_requests=Submitter(request()),
                resource_catalogue=reader,
            )
        )
    )
    site_ref = uuid4()
    response = http.get(
        (
            "/v1/resources?search=%20edge%20"
            f"&authorityScopeRef=scope%3Aedge&siteRef={site_ref}"
            "&sortBy=resourceRef&sortDirection=desc&page=2&pageSize=10"
        ),
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["resourceRef"] == str(item.resource_ref)
    assert response.json()["total"] == 1
    assert reader.received == ResourceCatalogueQuery(
        search="edge",
        authority_scope_ref="scope:edge",
        site_ref=site_ref,
        sort_by=ResourceSortField.RESOURCE_REF,
        sort_direction=SortDirection.DESC,
        page=2,
        page_size=10,
    )


@dataclass
class ApplicationReader:
    page: ApplicationCataloguePage
    received: ApplicationCatalogueQuery | None = None

    def list_applications(self, query: ApplicationCatalogueQuery) -> ApplicationCataloguePage:
        self.received = query
        return self.page


def test_application_catalogue_query_maps_http_params_to_application_query() -> None:
    principal = Principal("subject:alice", frozenset({"application.read"}), ())
    item = Application.create(application_ref=uuid4(), name="Payments")
    reader = ApplicationReader(ApplicationCataloguePage((item,), 1, 2, 10))
    http = TestClient(
        create_app(
            HttpDependencies(
                identity=Identity(principal),
                access_requests=Submitter(request()),
                application_catalogue=reader,
            )
        )
    )
    component_ref = uuid4()
    response = http.get(
        (
            "/v1/applications?search=%20payments%20"
            f"&componentRef={component_ref}"
            "&sortBy=applicationRef&sortDirection=desc&page=2&pageSize=10"
        ),
        headers={"Authorization": "Bearer token"},
    )

    assert response.status_code == 200
    assert response.json()["items"][0]["applicationRef"] == str(item.application_ref)
    assert response.json()["total"] == 1
    assert reader.received == ApplicationCatalogueQuery(
        search="payments",
        component_ref=component_ref,
        sort_by=ApplicationSortField.APPLICATION_REF,
        sort_direction=ApplicationSortDirection.DESC,
        page=2,
        page_size=10,
    )
