from dataclasses import dataclass
from datetime import datetime, timezone
from uuid import UUID, uuid4

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
        "source_deployment_ref": str(uuid4()),
        "destination_deployment_ref": str(uuid4()),
        "interaction_revision_ref": str(uuid4()),
        "need_ref": str(uuid4()),
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
    assert client(Identity(principal), Submitter(AuthorityForbidden())).post(
        "/v1/access-requests",
        headers={"Authorization": "Bearer token", "Idempotency-Key": "key-1"},
        json=body(),
    ).status_code == 403
    assert client(Identity(principal), Submitter(AccessRequestSubmissionRejected())).post(
        "/v1/access-requests",
        headers={"Authorization": "Bearer token", "Idempotency-Key": "key-1"},
        json=body(),
    ).status_code == 422
    assert client(Identity(principal), Submitter(request())).post(
        "/v1/access-requests",
        headers={"Authorization": "Bearer token"},
        json=body(),
    ).status_code == 422
