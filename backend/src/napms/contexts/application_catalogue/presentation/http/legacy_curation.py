from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from napms.contexts.application_catalogue.application.curation.bindings import (
    CreateDeploymentResourceBindingCommand,
)
from napms.contexts.application_catalogue.application.curation.create_application import CreateApplicationCommand
from napms.contexts.application_catalogue.application.curation.dcs import CreateDcsRevisionCommand
from napms.contexts.application_catalogue.application.curation.deployments import (
    CreateComponentDeploymentCommand,
)
from napms.contexts.application_catalogue.application.curation.structure import CreateComponentCommand
from napms.contexts.application_catalogue.presentation.http.support import (
    mutation_response,
    require_aware,
    require_interval,
    require_mutation_success,
)
from napms.contexts.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortConstraintKind,
    DcsPortRange,
)
from napms.platform.auth.local import InMemorySessionStore
from napms.platform.http.support import (
    PublicApiError,
    require_actor,
)


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


def create_application_catalogue_curation_router(
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
        require_actor(sessions, request)
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
        require_actor(sessions, request)
        as_of = asOf or clock()
        require_aware(as_of, "asOf")
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
        actor_id = require_actor(sessions, request)
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
        require_mutation_success(result.outcome)
        return mutation_response(
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
        actor_id = require_actor(sessions, request)
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
        require_mutation_success(result.outcome)
        return mutation_response(
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
        actor_id = require_actor(sessions, request)
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
        require_mutation_success(result.outcome)
        return mutation_response(
            result.outcome,
            {"deployment": _deployment_dto(result.deployment)},
        )

    @router.post("/api/v1/catalogues/dcs-revisions", name="CreateCatalogueDcsRevision")
    def create_dcs_revision(
        payload: CreateDcsRevisionRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
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
        require_mutation_success(result.outcome)
        return mutation_response(
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
        actor_id = require_actor(sessions, request)
        require_interval(payload.valid_from, payload.valid_to)
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
        require_mutation_success(result.outcome)
        return mutation_response(
            result.outcome,
            {"binding": _binding_dto(result.binding)},
        )

    return router


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


# Compatibility aliases used while adjacent HTTP adapters are migrated in I32 M2.
_require_actor = require_actor
_require_aware = require_aware
_require_interval = require_interval
_require_success = require_mutation_success
_mutation_response = mutation_response
