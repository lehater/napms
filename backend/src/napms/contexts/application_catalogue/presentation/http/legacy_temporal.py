from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, ConfigDict, Field

from napms.contexts.application_catalogue.application.curation.bindings import (
    EndDeploymentResourceBindingCommand,
)
from napms.contexts.application_catalogue.presentation.http.legacy_curation import _binding_dto
from napms.contexts.application_catalogue.presentation.http.support import (
    mutation_response,
    require_aware,
    require_mutation_success,
)
from napms.platform.auth.local import InMemorySessionStore
from napms.platform.http.support import require_actor


class EndDeploymentResourceBindingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    valid_to: datetime = Field(alias="validTo")
    expected_version: int = Field(alias="expectedVersion", ge=1)


def create_application_catalogue_temporal_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager],
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/api/v1/catalogues/deployment-resource-bindings/{binding_reference}/end",
        name="EndCatalogueDeploymentResourceBinding",
    )
    def end_deployment_resource_binding(
        binding_reference: str,
        payload: EndDeploymentResourceBindingRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=256,
        ),
    ):
        actor_id = require_actor(sessions, request)
        require_aware(payload.valid_to, "validTo")
        with open_scope() as scope:
            result = scope.applications.end_deployment_resource_binding.execute(
                EndDeploymentResourceBindingCommand(
                    binding_reference=binding_reference,
                    valid_to=payload.valid_to,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        require_mutation_success(result.outcome)
        return mutation_response(
            result.outcome,
            {"binding": _binding_dto(result.binding)},
        )

    return router
