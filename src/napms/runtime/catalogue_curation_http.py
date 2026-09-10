from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from napms.application_catalogue.application.binding_curation import (
    CreateDeploymentResourceBindingCommand,
)
from napms.application_catalogue.application.curation import (
    CreateApplicationCommand,
)
from napms.application_catalogue.application.dcs_curation import (
    CreateDcsRevisionCommand,
)
from napms.application_catalogue.application.deployment_curation import (
    CreateComponentDeploymentCommand,
)
from napms.application_catalogue.application.structure_curation import (
    CreateComponentCommand,
)
from napms.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortConstraintKind,
    DcsPortRange,
)
from napms.resource_catalogue.application.curation import CreateResourceCommand
from napms.resource_catalogue.application.ports import ResourceCataloguePersistenceError
from napms.resource_catalogue.application.realization_curation import (
    CreateResourceRealizationCommand,
)
from napms.resource_catalogue.application.responsibility_curation import (
    CreateResponsibilityCommand,
)
from napms.resource_catalogue.application.scope_affiliation_curation import (
    CreateScopeAffiliationCommand,
)
from napms.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibilityRole,
)
from napms.runtime.auth import InMemorySessionStore
from napms.runtime.http_api import PublicApiError, SESSION_COOKIE_NAME


class CreateApplicationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    display_name: str = Field(alias="displayName", min_length=1, max_length=256)


class CreateComponentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    display_name: str = Field(alias="displayName", min_length=1, max_length=256)


class CreateComponentDeploymentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    display_name: str | None = Field(
        default=None,
        alias="displayName",
        min_length=1,
        max_length=256,
    )


class DcsPortRangeValue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    first: int = Field(ge=0, le=65535)
    last: int = Field(ge=0, le=65535)


class DcsPortConstraintValue(BaseModel):
    model_config = ConfigDict(extra="forbid")
    kind: DcsPortConstraintKind
    ranges: list[DcsPortRangeValue] = Field(default_factory=list)


class DcsTrafficAlternativeValue(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    protocol: str = Field(min_length=1, max_length=32)
    source_ports: DcsPortConstraintValue = Field(alias="sourcePorts")
    destination_ports: DcsPortConstraintValue = Field(alias="destinationPorts")
    service_reference: str | None = Field(
        default=None,
        alias="serviceReference",
        min_length=1,
        max_length=256,
    )


class CreateDcsRevisionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    source_component_deployment_id: UUID = Field(alias="sourceComponentDeploymentId")
    destination_component_deployment_id: UUID = Field(
        alias="destinationComponentDeploymentId"
    )
    display_name: str | None = Field(
        default=None,
        alias="displayName",
        min_length=1,
        max_length=256,
    )
    traffic_alternatives: list[DcsTrafficAlternativeValue] = Field(
        alias="trafficAlternatives",
        min_length=1,
        max_length=100,
    )


class CreateDeploymentResourceBindingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    resource_reference: str = Field(alias="resourceReference", min_length=1, max_length=512)
    valid_from: datetime = Field(alias="validFrom")
    valid_to: datetime | None = Field(default=None, alias="validTo")


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


def create_catalogue_curation_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager],
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()

    @router.get("/api/v1/catalogues/applications", name="ListCatalogueApplications")
    def list_applications(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None, max_length=256),
        includeRetired: bool = Query(False),
    ):
        _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.list_applications.execute(
                page=page,
                page_size=pageSize,
                search=search,
                include_retired=includeRetired,
            )
        return {
            "items": [_application_dto(item) for item in result.items],
            "page": result.page,
            "pageSize": result.page_size,
            "hasMore": result.has_more,
        }

    @router.get(
        "/api/v1/catalogues/applications/{application_id}",
        name="ReadCatalogueApplication",
    )
    def read_application(
        application_id: UUID,
        request: Request,
        asOf: datetime | None = Query(None),
        includeRetiredComponents: bool = Query(False),
        includeRetiredDeployments: bool = Query(False),
    ):
        _require_actor(sessions, request)
        as_of = asOf or clock()
        _require_aware(as_of, "asOf")
        with open_scope() as scope:
            result = scope.applications.read_application_tree.execute(
                application_id=application_id,
                as_of=as_of,
                include_retired_components=includeRetiredComponents,
                include_retired_deployments=includeRetiredDeployments,
            )
        if result is None:
            raise PublicApiError(
                status_code=404,
                code="CatalogueApplicationNotFound",
                message="The catalogue Application was not found.",
            )
        return _application_tree_dto(result)

    @router.post("/api/v1/catalogues/applications", name="CreateCatalogueApplication")
    def create_application(
        payload: CreateApplicationRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        action_time = clock()
        with open_scope() as scope:
            result = scope.applications.create_application.execute(
                CreateApplicationCommand(
                    display_name=payload.display_name,
                    actor_id=actor_id,
                    effective_time=action_time,
                    idempotency_key=idempotency_key,
                )
            )
        _require_success(result.outcome)
        return _mutation_response(
            result.outcome,
            {"application": _application_dto(result.application)},
        )

    @router.post(
        "/api/v1/catalogues/applications/{application_id}/components",
        name="CreateCatalogueComponent",
    )
    def create_component(
        application_id: UUID,
        payload: CreateComponentRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.create_component.execute(
                CreateComponentCommand(
                    application_id=application_id,
                    display_name=payload.display_name,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_success(result.outcome)
        return _mutation_response(
            result.outcome,
            {"component": _component_dto(result.component)},
        )

    @router.post(
        "/api/v1/catalogues/components/{component_id}/deployments",
        name="CreateCatalogueComponentDeployment",
    )
    def create_component_deployment(
        component_id: UUID,
        payload: CreateComponentDeploymentRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.create_component_deployment.execute(
                CreateComponentDeploymentCommand(
                    component_id=component_id,
                    display_name=payload.display_name,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_success(result.outcome)
        return _mutation_response(
            result.outcome,
            {"deployment": _deployment_dto(result.deployment)},
        )

    @router.post("/api/v1/catalogues/dcs-revisions", name="CreateCatalogueDcsRevision")
    def create_dcs_revision(
        payload: CreateDcsRevisionRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        alternatives = tuple(_traffic_alternative(value) for value in payload.traffic_alternatives)
        with open_scope() as scope:
            result = scope.applications.create_dcs_revision.execute(
                CreateDcsRevisionCommand(
                    source_component_deployment_id=payload.source_component_deployment_id,
                    destination_component_deployment_id=payload.destination_component_deployment_id,
                    display_name=payload.display_name,
                    traffic_alternatives=alternatives,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_success(result.outcome)
        return _mutation_response(
            result.outcome,
            {"dcsRevision": _dcs_revision_dto(result.revision)},
        )

    @router.post(
        "/api/v1/catalogues/deployments/{deployment_id}/resource-bindings",
        name="CreateCatalogueDeploymentResourceBinding",
    )
    def create_deployment_resource_binding(
        deployment_id: UUID,
        payload: CreateDeploymentResourceBindingRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        _require_interval(payload.valid_from, payload.valid_to)
        with open_scope() as scope:
            result = scope.applications.create_deployment_resource_binding.execute(
                CreateDeploymentResourceBindingCommand(
                    component_deployment_id=deployment_id,
                    resource_reference=payload.resource_reference,
                    valid_from=payload.valid_from,
                    valid_to=payload.valid_to,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_success(result.outcome)
        return _mutation_response(
            result.outcome,
            {"binding": _binding_dto(result.binding)},
        )

    @router.get("/api/v1/catalogues/resources", name="ListCatalogueResources")
    def list_resources(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None, max_length=256),
        includeRetired: bool = Query(False),
    ):
        _require_actor(sessions, request)
        try:
            with open_scope() as scope:
                result = scope.resources.list_resources.execute(
                    page=page,
                    page_size=pageSize,
                    search=search,
                    include_retired=includeRetired,
                )
        except ResourceCataloguePersistenceError as exc:
            raise _resource_persistence_error() from exc
        return {
            "items": [_resource_dto(item) for item in result.items],
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
        _require_actor(sessions, request)
        as_of = asOf or clock()
        _require_aware(as_of, "asOf")
        try:
            with open_scope() as scope:
                result = scope.resources.read_resource.execute(
                    resource_reference=resource_reference,
                    as_of=as_of,
                )
        except ResourceCataloguePersistenceError as exc:
            raise _resource_persistence_error() from exc
        if result is None:
            raise PublicApiError(
                status_code=404,
                code="CatalogueResourceNotFound",
                message="The catalogue Resource was not found.",
            )
        return _resource_detail_dto(result)

    @router.post("/api/v1/catalogues/resources", name="CreateCatalogueResource")
    def create_resource(
        payload: CreateResourceRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
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
            raise _resource_persistence_error() from exc
        _require_success(result.outcome)
        return _mutation_response(
            result.outcome,
            {"resource": _resource_dto(result.resource)},
        )

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
        actor_id = _require_actor(sessions, request)
        _require_interval(payload.valid_from, payload.valid_to)
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
            raise _resource_persistence_error() from exc
        _require_success(result.outcome)
        return _mutation_response(
            result.outcome,
            {"realization": _realization_dto(result.realization)},
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
        actor_id = _require_actor(sessions, request)
        _require_interval(payload.valid_from, payload.valid_to)
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
            raise _resource_persistence_error() from exc
        _require_success(result.outcome)
        return _mutation_response(
            result.outcome,
            {"scopeAffiliation": _scope_affiliation_dto(result.affiliation)},
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
        actor_id = _require_actor(sessions, request)
        _require_interval(payload.valid_from, payload.valid_to)
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
            raise _resource_persistence_error() from exc
        _require_success(result.outcome)
        return _mutation_response(
            result.outcome,
            {"responsibility": _responsibility_dto(result.responsibility)},
        )

    return router


def _require_actor(sessions: InMemorySessionStore, request: Request) -> str:
    actor = sessions.get(request.cookies.get(SESSION_COOKIE_NAME))
    if actor is None:
        raise PublicApiError(
            status_code=401,
            code="AuthenticationRequired",
            message="Authentication is required.",
        )
    request.state.actor_id = actor.actor_id
    return actor.actor_id


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise PublicApiError(
            status_code=422,
            code="InvalidCatalogueTime",
            message=f"{field_name} must include an explicit timezone offset.",
        )


def _require_interval(valid_from: datetime, valid_to: datetime | None) -> None:
    _require_aware(valid_from, "validFrom")
    if valid_to is not None:
        _require_aware(valid_to, "validTo")
        if valid_from >= valid_to:
            raise PublicApiError(
                status_code=422,
                code="InvalidCatalogueInterval",
                message="validFrom must be before validTo.",
            )


def _port_constraint(value: DcsPortConstraintValue) -> DcsPortConstraint:
    ranges = tuple(DcsPortRange(item.first, item.last) for item in value.ranges)
    if value.kind is DcsPortConstraintKind.ANY:
        if ranges:
            raise PublicApiError(
                status_code=422,
                code="InvalidDcsPortConstraint",
                message="Any port constraint cannot contain ranges.",
            )
        return DcsPortConstraint.any()
    if value.kind is DcsPortConstraintKind.NOT_APPLICABLE:
        if ranges:
            raise PublicApiError(
                status_code=422,
                code="InvalidDcsPortConstraint",
                message="NotApplicable port constraint cannot contain ranges.",
            )
        return DcsPortConstraint.not_applicable()
    if not ranges:
        raise PublicApiError(
            status_code=422,
            code="InvalidDcsPortConstraint",
            message="Ranges port constraint requires at least one range.",
        )
    return DcsPortConstraint.ranged(*ranges)


def _traffic_alternative(value: DcsTrafficAlternativeValue) -> AuthoredDcsTrafficAlternative:
    return AuthoredDcsTrafficAlternative(
        protocol=value.protocol,
        source_ports=_port_constraint(value.source_ports),
        destination_ports=_port_constraint(value.destination_ports),
        service_reference=value.service_reference,
    )


def _require_success(outcome) -> None:
    value = getattr(outcome, "value", str(outcome))
    if value in {"Created", "Updated", "Resolved"}:
        return
    mapping = {
        "AuthorityDenied": (403, "CatalogueAuthorityDenied", "Catalogue curation is not permitted."),
        "AuthorityUnknown": (409, "CatalogueAuthorityUnknown", "Catalogue curation authority is unknown."),
        "NotFound": (404, "CatalogueSubjectNotFound", "The catalogue subject was not found."),
        "ParentInactive": (409, "CatalogueParentInactive", "The parent catalogue entity is not Active."),
        "ResourceInactive": (409, "CatalogueResourceInactive", "The Resource is not Active."),
        "RetirementBlocked": (409, "CatalogueRetirementBlocked", "Catalogue retirement is blocked by active dependants."),
        "InputInvalid": (422, "CatalogueInputInvalid", "The catalogue mutation input is invalid."),
        "OverlapConflict": (409, "CatalogueOverlapConflict", "The catalogue temporal fact overlaps authoritative state."),
        "ConcurrencyConflict": (409, "CatalogueConcurrencyConflict", "The catalogue entity changed concurrently."),
        "IdempotencyConflict": (409, "CatalogueIdempotencyConflict", "The Idempotency-Key was already used for a different command."),
        "PersistenceUnknown": (503, "CataloguePersistenceOutcomeUnknown", "The catalogue persistence outcome is unknown."),
    }
    status_code, code, message = mapping.get(
        value,
        (500, "CatalogueMutationFailed", "The catalogue mutation could not be completed."),
    )
    raise PublicApiError(status_code=status_code, code=code, message=message)


def _mutation_response(outcome, content: dict) -> JSONResponse:
    status_code = 201 if getattr(outcome, "value", str(outcome)) == "Created" else 200
    return JSONResponse(status_code=status_code, content=content)


def _resource_persistence_error() -> PublicApiError:
    return PublicApiError(
        status_code=503,
        code="ResourceCatalogueUnavailable",
        message="Resource Catalogue persistence is unavailable.",
    )


def _application_dto(value):
    return {
        "applicationId": str(value.application_id),
        "displayName": value.display_name,
        "lifecycle": value.lifecycle_state.value,
        "version": value.version,
        "provenanceReference": value.provenance_reference,
        "retirementProvenanceReference": value.retirement_provenance_reference,
    }


def _component_dto(value):
    return {
        "componentId": str(value.component_id),
        "applicationId": str(value.application_id),
        "displayName": value.display_name,
        "lifecycle": value.lifecycle_state.value,
        "version": value.version,
        "provenanceReference": value.provenance_reference,
        "retirementProvenanceReference": value.retirement_provenance_reference,
    }


def _deployment_dto(value):
    return {
        "componentDeploymentId": str(value.deployment_id),
        "componentId": str(value.component_id),
        "displayName": value.display_name,
        "lifecycle": value.lifecycle_state.value,
        "version": value.version,
        "provenanceReference": value.provenance_reference,
        "retirementProvenanceReference": value.retirement_provenance_reference,
    }


def _dcs_revision_dto(value):
    return {
        "revisionId": str(value.revision_id),
        "sourceComponentDeploymentId": str(value.source_component_deployment_id),
        "destinationComponentDeploymentId": str(value.destination_component_deployment_id),
        "displayName": value.display_name,
        "provenanceReference": value.provenance_reference,
    }


def _binding_dto(value):
    return {
        "bindingReference": value.reference_id,
        "componentDeploymentId": str(value.component_deployment_id),
        "resourceReference": value.resource_reference,
        "validFrom": value.valid_from.isoformat(),
        "validTo": value.valid_to.isoformat() if value.valid_to else None,
        "version": value.version,
        "provenanceReference": value.provenance_reference,
        "endProvenanceReference": value.end_provenance_reference,
    }


def _application_tree_dto(value):
    return {
        "application": _application_dto(value.application),
        "asOf": value.as_of.isoformat(),
        "components": [
            {
                **_component_dto(component.component),
                "deployments": [
                    {
                        **_deployment_dto(deployment.deployment),
                        "effectiveResourceBindings": [
                            _binding_dto(binding)
                            for binding in deployment.effective_resource_bindings
                        ],
                        "dcsRevisions": [
                            {
                                "revisionId": str(revision.revision_id),
                                "sourceComponentDeploymentId": str(
                                    revision.source_component_deployment_id
                                ),
                                "destinationComponentDeploymentId": str(
                                    revision.destination_component_deployment_id
                                ),
                                "displayName": revision.display_name,
                                "provenanceReference": revision.provenance_reference,
                            }
                            for revision in deployment.dcs_revisions
                        ],
                    }
                    for deployment in component.deployments
                ],
            }
            for component in value.components
        ],
    }


def _resource_dto(value):
    return {
        "resourceReference": value.resource_reference,
        "displayName": value.display_name,
        "lifecycle": value.lifecycle_state.value,
        "version": value.version,
        "provenanceReference": value.provenance_reference,
        "retirementProvenanceReference": value.retirement_provenance_reference,
    }


def _realization_dto(value):
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


def _scope_affiliation_dto(value):
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


def _responsibility_dto(value):
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


def _resource_detail_dto(value):
    return {
        "resource": _resource_dto(value.resource),
        "asOf": value.as_of.isoformat(),
        "effectiveRealizations": [
            _realization_dto(item) for item in value.effective_realizations
        ],
        "effectiveScopeAffiliations": [
            _scope_affiliation_dto(item)
            for item in value.effective_scope_affiliations
        ],
        "effectiveResponsibilities": [
            _responsibility_dto(item)
            for item in value.effective_responsibilities
        ],
    }
