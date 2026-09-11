from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable

from fastapi import APIRouter, Header, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from napms.contexts.resource_catalogue.application.curation import CreateResourceCommand
from napms.contexts.resource_catalogue.application.ports import ResourceCataloguePersistenceError
from napms.contexts.resource_catalogue.application.realization_curation import (
    CreateResourceRealizationCommand,
)
from napms.contexts.resource_catalogue.application.responsibility_curation import (
    CreateResponsibilityCommand,
)
from napms.contexts.resource_catalogue.application.scope_affiliation_curation import (
    CreateScopeAffiliationCommand,
)
from napms.contexts.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibilityRole,
)
from napms.contexts.resource_catalogue.presentation.http.support import (
    mutation_response,
    require_aware,
    require_interval,
    require_mutation_success,
)
from napms.platform.auth.local import InMemorySessionStore
from napms.platform.http.support import (
    PublicApiError,
    require_actor,
)


class CreateResourceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    display_name: str | None = Field(
        default=None,
        alias="displayName",
        min_length=1,
        max_length=256,
    )


class CreateResourceRealizationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    technical_addresses: list[str] = Field(
        alias="technicalAddresses",
        min_length=1,
        max_length=256,
    )
    valid_from: datetime = Field(alias="validFrom")
    valid_to: datetime | None = Field(default=None, alias="validTo")


class CreateResourceScopeAffiliationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    responsibility_scope: str = Field(
        alias="responsibilityScope",
        min_length=1,
        max_length=512,
    )
    valid_from: datetime = Field(alias="validFrom")
    valid_to: datetime | None = Field(default=None, alias="validTo")


class CreateResourceResponsibilityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    party_reference: str = Field(alias="partyReference", min_length=1, max_length=512)
    party_kind: ResponsiblePartyKind = Field(alias="partyKind")
    role: ResourceResponsibilityRole
    display_name: str = Field(alias="displayName", min_length=1, max_length=256)
    contact: str | None = Field(default=None, min_length=1, max_length=1024)
    valid_from: datetime = Field(alias="validFrom")
    valid_to: datetime | None = Field(default=None, alias="validTo")


def create_resource_catalogue_curation_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager],
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()

    @router.get("/api/v1/catalogues/resources", name="ListCatalogueResources")
    def list_resources(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None, max_length=256),
        includeRetired: bool = Query(False),
    ):
        require_actor(sessions, request)
        try:
            with open_scope() as scope:
                result = scope.resources.list_resources.execute(
                    page=page,
                    page_size=pageSize,
                    search=search,
                    include_retired=includeRetired,
                )
        except ResourceCataloguePersistenceError as exc:
            raise resource_persistence_error() from exc
        return {
            "items": [resource_dto(item) for item in result.items],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
        }

    @router.get(
        "/api/v1/catalogues/resources/{resource_reference:path}",
        name="ReadCatalogueResource",
    )
    def read_resource(
        resource_reference: str,
        request: Request,
        asOf: datetime | None = Query(None),
    ):
        require_actor(sessions, request)
        as_of = asOf or clock()
        require_aware(as_of, "asOf")
        try:
            with open_scope() as scope:
                result = scope.resources.read_resource.execute(
                    resource_reference=resource_reference,
                    as_of=as_of,
                )
        except ResourceCataloguePersistenceError as exc:
            raise resource_persistence_error() from exc
        if result is None:
            raise PublicApiError(
                status_code=404,
                code="CatalogueResourceNotFound",
                message="The catalogue Resource was not found.",
            )
        return resource_detail_dto(result)

    @router.post("/api/v1/catalogues/resources", name="CreateCatalogueResource")
    def create_resource(
        payload: CreateResourceRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
        try:
            with open_scope() as scope:
                result = scope.resources.create_resource.execute(
                    CreateResourceCommand(
                        display_name=payload.display_name,
                        actor_id=actor_id,
                        effective_time=clock(),
                        idempotency_key=idempotency_key,
                    )
                )
        except ResourceCataloguePersistenceError as exc:
            raise resource_persistence_error() from exc
        require_mutation_success(result.outcome)
        return mutation_response(result.outcome, {"resource": resource_dto(result.resource)})

    @router.post(
        "/api/v1/catalogues/resources/{resource_reference:path}/realizations",
        name="CreateCatalogueResourceRealization",
    )
    def create_resource_realization(
        resource_reference: str,
        payload: CreateResourceRealizationRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
        require_interval(payload.valid_from, payload.valid_to)
        try:
            with open_scope() as scope:
                result = scope.resources.create_realization.execute(
                    CreateResourceRealizationCommand(
                        resource_reference=resource_reference,
                        technical_addresses=tuple(payload.technical_addresses),
                        valid_from=payload.valid_from,
                        valid_to=payload.valid_to,
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
            {"realization": realization_dto(result.realization)},
        )

    @router.post(
        "/api/v1/catalogues/resources/{resource_reference:path}/scope-affiliations",
        name="CreateCatalogueResourceScopeAffiliation",
    )
    def create_resource_scope_affiliation(
        resource_reference: str,
        payload: CreateResourceScopeAffiliationRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
        require_interval(payload.valid_from, payload.valid_to)
        try:
            with open_scope() as scope:
                result = scope.resources.create_scope_affiliation.execute(
                    CreateScopeAffiliationCommand(
                        resource_reference=resource_reference,
                        responsibility_scope=payload.responsibility_scope,
                        valid_from=payload.valid_from,
                        valid_to=payload.valid_to,
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
        "/api/v1/catalogues/resources/{resource_reference:path}/responsibilities",
        name="CreateCatalogueResourceResponsibility",
    )
    def create_resource_responsibility(
        resource_reference: str,
        payload: CreateResourceResponsibilityRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
        require_interval(payload.valid_from, payload.valid_to)
        try:
            with open_scope() as scope:
                result = scope.resources.create_responsibility.execute(
                    CreateResponsibilityCommand(
                        resource_reference=resource_reference,
                        party_reference=payload.party_reference,
                        party_kind=payload.party_kind,
                        role=payload.role,
                        display_name=payload.display_name,
                        contact=payload.contact,
                        valid_from=payload.valid_from,
                        valid_to=payload.valid_to,
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


def resource_persistence_error() -> PublicApiError:
    return PublicApiError(
        status_code=503,
        code="ResourceCatalogueUnavailable",
        message="Resource Catalogue persistence is unavailable.",
    )


def resource_dto(value):
    return {
        "resourceReference": value.resource_reference,
        "displayName": value.display_name,
        "lifecycle": value.lifecycle_state.value,
        "version": value.version,
        "provenanceReference": value.provenance_reference,
        "retirementProvenanceReference": value.retirement_provenance_reference,
    }


def realization_dto(value):
    return {
        "factReference": value.fact_reference,
        "resourceReference": value.resource_reference,
        "technicalAddresses": [
            {
                "endpointReference": item.endpoint_reference,
                "technicalAddress": item.technical_address,
            }
            for item in value.endpoint_realizations
        ],
        "validFrom": value.valid_from.isoformat(),
        "validTo": value.valid_to.isoformat() if value.valid_to else None,
        "version": value.version,
        "provenanceReference": value.provenance_reference,
        "endProvenanceReference": value.end_provenance_reference,
    }


def scope_affiliation_dto(value):
    return {
        "affiliationReference": value.affiliation_reference,
        "resourceReference": value.resource_reference,
        "responsibilityScope": value.responsibility_scope,
        "validFrom": value.valid_from.isoformat(),
        "validTo": value.valid_to.isoformat() if value.valid_to else None,
        "version": value.version,
        "provenanceReference": value.provenance_reference,
        "endProvenanceReference": value.end_provenance_reference,
    }


def responsibility_dto(value):
    return {
        "assignmentReference": value.assignment_reference,
        "resourceReference": value.resource_reference,
        "partyReference": value.party_reference,
        "partyKind": value.party_kind.value,
        "role": value.role.value,
        "displayName": value.display_name,
        "contact": value.contact,
        "validFrom": value.valid_from.isoformat(),
        "validTo": value.valid_to.isoformat() if value.valid_to else None,
        "version": value.version,
        "provenanceReference": value.provenance_reference,
        "endProvenanceReference": value.end_provenance_reference,
    }


def resource_detail_dto(value):
    return {
        "resource": resource_dto(value.resource),
        "asOf": value.as_of.isoformat(),
        "effectiveRealizations": [
            realization_dto(item) for item in value.effective_realizations
        ],
        "effectiveScopeAffiliations": [
            scope_affiliation_dto(item) for item in value.effective_scope_affiliations
        ],
        "effectiveResponsibilities": [
            responsibility_dto(item) for item in value.effective_responsibilities
        ],
    }


# Compatibility aliases used while adjacent HTTP adapters are migrated in I32 M2.
_resource_persistence_error = resource_persistence_error
_resource_dto = resource_dto
_realization_dto = realization_dto
_scope_affiliation_dto = scope_affiliation_dto
_responsibility_dto = responsibility_dto
_resource_detail_dto = resource_detail_dto
