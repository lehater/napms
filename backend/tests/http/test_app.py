from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from napms.contexts.access_policy.application.submission import AccessRequestSubmissionRejected
from napms.contexts.access_policy.domain.model import (
    AccessRequest,
    AccessSubject,
    RequestAuthorityEvidence,
)
from napms.contexts.authority_management.application.service import AuthorityForbidden
from napms.contexts.authority_management.domain.model import Principal
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

    def list_requests(self) -> tuple[AccessRequest, ...]:
        return self.items

    def get_request(self, request_ref):
        return next((item for item in self.items if item.request_ref == request_ref), None)


def test_access_request_read_endpoints_preserve_subject_and_outcome() -> None:
    principal = Principal("subject:alice", frozenset({"access.read"}), ())
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
    assert catalogue.json()[0]["requestRef"] == str(item.request_ref)
    assert detail.json()["sourceDeploymentRef"] == str(item.access_subject.source_deployment_ref)
    assert detail.json()["decisionResult"] is None


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


