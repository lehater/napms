from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Header, Request
from pydantic import BaseModel, ConfigDict, Field

from napms.contexts.resource_catalogue.application.ports import ResourceCataloguePersistenceError
from napms.contexts.resource_catalogue.application.realization_curation import (
    ReplaceResourceRealizationCommand,
)
from napms.contexts.resource_catalogue.application.responsibility_curation import (
    EndResponsibilityCommand,
)
from napms.contexts.resource_catalogue.application.scope_affiliation_curation import (
    EndScopeAffiliationCommand,
)
from napms.contexts.resource_catalogue.presentation.http.curation import (
    realization_dto,
    resource_persistence_error,
    responsibility_dto,
    scope_affiliation_dto,
)
from napms.contexts.resource_catalogue.presentation.http.support import (
    mutation_response,
    require_aware,
    require_interval,
    require_mutation_success,
)
from napms.runtime.auth import InMemorySessionStore
from napms.runtime.http_support import require_actor


class ReplaceResourceRealizationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    technical_addresses: list[str] = Field(
        alias="technicalAddresses",
        min_length=1,
        max_length=256,
    )
    valid_from: datetime = Field(alias="validFrom")
    valid_to: datetime | None = Field(default=None, alias="validTo")
    expected_version: int = Field(alias="expectedVersion", ge=1)


class EndTemporalRelationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    valid_to: datetime = Field(alias="validTo")
    expected_version: int = Field(alias="expectedVersion", ge=1)


def create_resource_catalogue_temporal_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager],
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()

    @router.post(
        "/api/v1/catalogues/resource-realizations/{fact_reference}/replacement",
        name="ReplaceCatalogueResourceRealization",
    )
    def replace_resource_realization(
        fact_reference: str,
        payload: ReplaceResourceRealizationRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=256,
        ),
    ):
        actor_id = require_actor(sessions, request)
        require_interval(payload.valid_from, payload.valid_to)
        try:
            with open_scope() as scope:
                result = scope.resources.replace_realization.execute(
                    ReplaceResourceRealizationCommand(
                        current_fact_reference=fact_reference,
                        technical_addresses=tuple(payload.technical_addresses),
                        valid_from=payload.valid_from,
                        valid_to=payload.valid_to,
                        expected_version=payload.expected_version,
                        actor_id=actor_id,
                        effective_time=clock(),
                        idempotency_key=idempotency_key,
                    )
                )
        except ResourceCataloguePersistenceError as exc:
            raise resource_persistence_error() from exc
        require_mutation_success(result.outcome)
        return mutation_response(
            result.outcome,
            {
                "realization": realization_dto(result.realization),
                "replacedFactReference": result.replaced_fact_reference,
            },
        )

    @router.post(
        "/api/v1/catalogues/resource-scope-affiliations/{affiliation_reference}/end",
        name="EndCatalogueResourceScopeAffiliation",
    )
    def end_resource_scope_affiliation(
        affiliation_reference: str,
        payload: EndTemporalRelationRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=256,
        ),
    ):
        actor_id = require_actor(sessions, request)
        require_aware(payload.valid_to, "validTo")
        try:
            with open_scope() as scope:
                result = scope.resources.end_scope_affiliation.execute(
                    EndScopeAffiliationCommand(
                        affiliation_reference=affiliation_reference,
                        valid_to=payload.valid_to,
                        expected_version=payload.expected_version,
                        actor_id=actor_id,
                        effective_time=clock(),
                        idempotency_key=idempotency_key,
                    )
                )
        except ResourceCataloguePersistenceError as exc:
            raise resource_persistence_error() from exc
        require_mutation_success(result.outcome)
        return mutation_response(
            result.outcome,
            {"scopeAffiliation": scope_affiliation_dto(result.affiliation)},
        )

    @router.post(
        "/api/v1/catalogues/resource-responsibilities/{assignment_reference}/end",
        name="EndCatalogueResourceResponsibility",
    )
    def end_resource_responsibility(
        assignment_reference: str,
        payload: EndTemporalRelationRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key",
            min_length=1,
            max_length=256,
        ),
    ):
        actor_id = require_actor(sessions, request)
        require_aware(payload.valid_to, "validTo")
        try:
            with open_scope() as scope:
                result = scope.resources.end_responsibility.execute(
                    EndResponsibilityCommand(
                        assignment_reference=assignment_reference,
                        valid_to=payload.valid_to,
                        expected_version=payload.expected_version,
                        actor_id=actor_id,
                        effective_time=clock(),
                        idempotency_key=idempotency_key,
                    )
                )
        except ResourceCataloguePersistenceError as exc:
            raise resource_persistence_error() from exc
        require_mutation_success(result.outcome)
        return mutation_response(
            result.outcome,
            {"responsibility": responsibility_dto(result.responsibility)},
        )

    return router
