from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from fastapi import Depends, FastAPI, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict

from napms.contexts.access_policy.application.submission import AccessRequestSubmissionRejected
from napms.contexts.authority_management.application.service import AuthorityForbidden
from napms.contexts.authority_management.domain.model import Principal
from napms.platform.security.oidc import (
    AuthenticationRejected,
    IdentityDependencyUnavailable,
    OidcIdentityValidator,
)


class AccessRequestSubmitter(Protocol):
    def submit(
        self,
        *,
        principal: Principal,
        source_deployment_ref: UUID,
        destination_deployment_ref: UUID,
        interaction_revision_ref: UUID,
        need_ref: UUID,
    ): ...


class SubmitAccessRequestBody(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    source_deployment_ref: UUID
    destination_deployment_ref: UUID
    interaction_revision_ref: UUID
    need_ref: UUID


@dataclass(frozen=True)
class HttpDependencies:
    identity: OidcIdentityValidator
    access_requests: AccessRequestSubmitter


def create_app(dependencies: HttpDependencies) -> FastAPI:
    app = FastAPI(title="NAPMS", version="1.0")

    def principal(authorization: str | None = Header(default=None)) -> Principal:
        if authorization is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        scheme, separator, token = authorization.partition(" ")
        if separator != " " or scheme.lower() != "bearer" or not token.strip():
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        try:
            return dependencies.identity.validate_bearer(token)
        except AuthenticationRejected as exc:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED) from exc
        except IdentityDependencyUnavailable as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE) from exc

    @app.post("/v1/access-requests", status_code=status.HTTP_201_CREATED)
    def submit_access_request(
        body: SubmitAccessRequestBody,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1),
        caller: Principal = Depends(principal),
    ) -> dict[str, object]:
        # The key is transport-required by the canonical contract. Persistence-backed
        # replay/conflict semantics are a separate application concern.
        del idempotency_key
        try:
            request = dependencies.access_requests.submit(
                principal=caller,
                source_deployment_ref=body.source_deployment_ref,
                destination_deployment_ref=body.destination_deployment_ref,
                interaction_revision_ref=body.interaction_revision_ref,
                need_ref=body.need_ref,
            )
        except AuthorityForbidden as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN) from exc
        except AccessRequestSubmissionRejected as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        return {"requestRef": str(request.request_ref), "version": request.version}

    return app
