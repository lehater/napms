from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from napms.application_catalogue.application.curation import CreateApplicationCommand
from napms.application_catalogue.application.target_binding_curation import (
    CreateDeploymentInteractionResourceBindingCommand,
    EndDeploymentInteractionResourceBindingCommand,
)
from napms.application_catalogue.application.target_curation import (
    CreateApplicationDeploymentCommand,
    CreateInteractionDefinitionCommand,
    SelectDeploymentInteractionCommand,
    TargetMutationOutcome,
    UpdateInteractionDefinitionEndpointsCommand,
    UpdateInteractionDefinitionTrafficCommand,
)
from napms.application_catalogue.application.target_metadata_curation import (
    UpdateApplicationDefinitionMetadataCommand,
    UpdateApplicationDeploymentContextCommand,
    UpdateComponentMetadataCommand,
)
from napms.application_catalogue.application.target_structure_curation import (
    CreateTargetComponentCommand,
)
from napms.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
)
from napms.application_catalogue.domain.target_model import DeploymentInteractionSide
from napms.runtime.auth import InMemorySessionStore
from napms.runtime.catalogue_curation_http import (
    DcsTrafficAlternativeValue,
    _require_actor,
    _require_aware,
    _traffic_alternative,
)
from napms.runtime.http_api import PublicApiError


class CreateApplicationDefinitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    display_name: str = Field(alias="displayName", min_length=1, max_length=256)
    description: str | None = Field(default=None, min_length=1, max_length=4096)
    domain: str | None = Field(default=None, min_length=1, max_length=256)
    owner_reference: str | None = Field(
        default=None, alias="ownerReference", min_length=1, max_length=2048
    )


class UpdateApplicationDefinitionRequest(CreateApplicationDefinitionRequest):
    expected_version: int = Field(alias="expectedVersion", ge=1)


class CreateApplicationComponentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    display_name: str = Field(alias="displayName", min_length=1, max_length=256)
    component_type: str | None = Field(
        default=None, alias="componentType", min_length=1, max_length=256
    )
    description: str | None = Field(default=None, min_length=1, max_length=4096)


class UpdateApplicationComponentRequest(CreateApplicationComponentRequest):
    expected_version: int = Field(alias="expectedVersion", ge=1)


class CreateInteractionDefinitionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    source_component_id: UUID = Field(alias="sourceComponentId")
    destination_component_id: UUID = Field(alias="destinationComponentId")
    traffic_alternatives: list[DcsTrafficAlternativeValue] = Field(
        alias="trafficAlternatives", min_length=1
    )


class UpdateInteractionEndpointsRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    source_component_id: UUID = Field(alias="sourceComponentId")
    destination_component_id: UUID = Field(alias="destinationComponentId")
    expected_version: int = Field(alias="expectedVersion", ge=1)


class UpdateInteractionTrafficRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    traffic_alternatives: list[DcsTrafficAlternativeValue] = Field(
        alias="trafficAlternatives", min_length=1
    )
    expected_version: int = Field(alias="expectedVersion", ge=1)


class CreateApplicationDeploymentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    application_id: UUID = Field(alias="applicationId")
    company_reference: str = Field(alias="companyReference", min_length=1, max_length=2048)
    environment: str = Field(min_length=1, max_length=256)
    scope_reference: str = Field(alias="scopeReference", min_length=1, max_length=2048)


class UpdateApplicationDeploymentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    company_reference: str = Field(alias="companyReference", min_length=1, max_length=2048)
    environment: str = Field(min_length=1, max_length=256)
    scope_reference: str = Field(alias="scopeReference", min_length=1, max_length=2048)
    expected_version: int = Field(alias="expectedVersion", ge=1)


class SelectDeploymentInteractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    interaction_definition_id: UUID = Field(alias="interactionDefinitionId")


class CreateInteractionResourceBindingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    side: DeploymentInteractionSide
    resource_reference: str = Field(alias="resourceReference", min_length=1, max_length=2048)
    valid_from: datetime = Field(alias="validFrom")
    valid_to: datetime | None = Field(default=None, alias="validTo")


class EndInteractionResourceBindingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    side: DeploymentInteractionSide
    valid_to: datetime = Field(alias="validTo")
    expected_version: int = Field(alias="expectedVersion", ge=1)


def create_catalogue_target_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager],
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()

    @router.get("/api/v1/catalogues/application-definitions")
    def list_definitions(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None),
        domain: str | None = Query(None),
        ownerReference: str | None = Query(None),
        sort: str = Query("name"),
    ):
        _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.read.list_definitions(
                offset=(page - 1) * pageSize,
                limit=pageSize,
                search=search,
                domain=domain,
                owner_reference=ownerReference,
                sort=sort,
            )
        return _page_response(
            result.page,
            page=page,
            items=[_definition_summary_dto(item) for item in result.items],
        )

    @router.get("/api/v1/catalogues/application-definitions/{application_id}")
    def read_definition(application_id: UUID, request: Request):
        _require_actor(sessions, request)
        with open_scope() as scope:
            value = scope.applications.read.get_definition(application_id=application_id)
        if value is None:
            _not_found("Application Definition")
        return {"definition": _definition_dto(value)}

    @router.get("/api/v1/catalogues/application-definitions/{application_id}/components")
    def list_components(
        application_id: UUID,
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None),
        componentType: str | None = Query(None),
        sort: str = Query("name"),
    ):
        _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.read.list_components(
                application_id=application_id,
                offset=(page - 1) * pageSize,
                limit=pageSize,
                search=search,
                component_type=componentType,
                sort=sort,
            )
        return _page_response(
            result.page,
            page=page,
            items=[_component_dto(item) for item in result.items],
        )

    @router.get("/api/v1/catalogues/application-definitions/{application_id}/interactions")
    def list_interactions(
        application_id: UUID,
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None),
        sourceComponentId: UUID | None = Query(None),
        destinationComponentId: UUID | None = Query(None),
        protocol: str | None = Query(None),
        sort: str = Query("source"),
    ):
        _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.read.list_interaction_definitions(
                application_id=application_id,
                offset=(page - 1) * pageSize,
                limit=pageSize,
                search=search,
                source_component_id=sourceComponentId,
                destination_component_id=destinationComponentId,
                protocol=protocol,
                sort=sort,
            )
        return _page_response(
            result.page,
            page=page,
            items=[_interaction_summary_dto(item) for item in result.items],
        )

    @router.get("/api/v1/catalogues/application-definitions/{application_id}/deployments")
    def list_definition_deployments(
        application_id: UUID,
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None),
        companyReference: str | None = Query(None),
        environment: str | None = Query(None),
        scopeReference: str | None = Query(None),
        sort: str = Query("company"),
    ):
        _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.read.list_application_deployments(
                application_id=application_id,
                offset=(page - 1) * pageSize,
                limit=pageSize,
                search=search,
                company_reference=companyReference,
                environment=environment,
                scope_reference=scopeReference,
                sort=sort,
            )
        return _page_response(
            result.page,
            page=page,
            items=[_deployment_summary_dto(item) for item in result.items],
        )

    @router.get("/api/v1/catalogues/application-deployments")
    def list_deployments(
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None),
        applicationId: UUID | None = Query(None),
        companyReference: str | None = Query(None),
        environment: str | None = Query(None),
        scopeReference: str | None = Query(None),
        sort: str = Query("application"),
    ):
        _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.read.list_application_deployments(
                application_id=applicationId,
                offset=(page - 1) * pageSize,
                limit=pageSize,
                search=search,
                company_reference=companyReference,
                environment=environment,
                scope_reference=scopeReference,
                sort=sort,
            )
        return _page_response(
            result.page,
            page=page,
            items=[_deployment_summary_dto(item) for item in result.items],
        )

    @router.get("/api/v1/catalogues/application-deployments/{deployment_id}")
    def read_deployment(deployment_id: UUID, request: Request):
        _require_actor(sessions, request)
        with open_scope() as scope:
            deployment = scope.applications.read.get_application_deployment(
                application_deployment_id=deployment_id
            )
            definition = (
                scope.applications.read.get_definition(application_id=deployment.application_id)
                if deployment is not None
                else None
            )
        if deployment is None:
            _not_found("Application Deployment")
        return {
            "deployment": _deployment_dto(deployment),
            "applicationName": definition.display_name if definition is not None else None,
        }

    @router.get(
        "/api/v1/catalogues/application-deployments/{deployment_id}/available-interactions"
    )
    def list_available_interactions(
        deployment_id: UUID,
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None),
        sourceComponentId: UUID | None = Query(None),
        destinationComponentId: UUID | None = Query(None),
        protocol: str | None = Query(None),
        sort: str = Query("source"),
    ):
        _require_actor(sessions, request)
        with open_scope() as scope:
            deployment = scope.applications.read.get_application_deployment(
                application_deployment_id=deployment_id
            )
            if deployment is None:
                _not_found("Application Deployment")
            result = scope.applications.read.list_available_interactions_for_deployment(
                application_deployment_id=deployment_id,
                offset=(page - 1) * pageSize,
                limit=pageSize,
                search=search,
                source_component_id=sourceComponentId,
                destination_component_id=destinationComponentId,
                protocol=protocol,
                sort=sort,
            )
        return _page_response(
            result.page,
            page=page,
            items=[_interaction_summary_dto(item) for item in result.items],
        )

    @router.get("/api/v1/catalogues/application-deployments/{deployment_id}/connectivity")
    def list_connectivity(
        deployment_id: UUID,
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None),
        sourceComponentId: UUID | None = Query(None),
        destinationComponentId: UUID | None = Query(None),
        protocol: str | None = Query(None),
        sort: str = Query("source"),
        asOf: datetime | None = Query(None),
    ):
        _require_actor(sessions, request)
        as_of = asOf or clock()
        _require_aware(as_of, "asOf")
        with open_scope() as scope:
            deployment = scope.applications.read.get_application_deployment(
                application_deployment_id=deployment_id
            )
            if deployment is None:
                _not_found("Application Deployment")
            result = scope.applications.read.list_deployment_connectivity(
                application_deployment_id=deployment_id,
                as_of=as_of,
                offset=(page - 1) * pageSize,
                limit=pageSize,
                search=search,
                source_component_id=sourceComponentId,
                destination_component_id=destinationComponentId,
                protocol=protocol,
                sort=sort,
            )
        response = _page_response(
            result.page,
            page=page,
            items=[_connectivity_dto(item) for item in result.items],
        )
        response["asOf"] = result.as_of.isoformat()
        return response

    @router.get(
        "/api/v1/catalogues/deployment-interactions/{deployment_interaction_id}/resources/{side}"
    )
    def list_resource_set(
        deployment_interaction_id: UUID,
        side: DeploymentInteractionSide,
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        search: str | None = Query(None),
        scopeReference: str | None = Query(None),
        sort: str = Query("resource"),
        asOf: datetime | None = Query(None),
    ):
        _require_actor(sessions, request)
        as_of = asOf or clock()
        _require_aware(as_of, "asOf")
        with open_scope() as scope:
            result = scope.applications.read.list_resource_set(
                deployment_interaction_id=deployment_interaction_id,
                side=side,
                as_of=as_of,
                offset=(page - 1) * pageSize,
                limit=pageSize,
                search=search,
                scope_reference=scopeReference,
                sort=sort,
            )
        response = _page_response(
            result.page,
            page=page,
            items=[_resource_member_dto(item) for item in result.items],
        )
        response["asOf"] = result.as_of.isoformat()
        return response

    @router.post("/api/v1/catalogues/application-definitions")
    def create_definition(
        payload: CreateApplicationDefinitionRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.create_definition.execute(
                CreateApplicationCommand(
                    display_name=payload.display_name,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                    description=payload.description,
                    domain=payload.domain,
                    owner_reference=payload.owner_reference,
                )
            )
        _require_target_success(result)
        return {
            "outcome": result.outcome.value,
            "definition": _definition_dto(result.application),
        }

    @router.post("/api/v1/catalogues/application-definitions/{application_id}/metadata")
    def update_definition(
        application_id: UUID,
        payload: UpdateApplicationDefinitionRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.update_definition_metadata.execute(
                UpdateApplicationDefinitionMetadataCommand(
                    application_id=application_id,
                    display_name=payload.display_name,
                    description=payload.description,
                    domain=payload.domain,
                    owner_reference=payload.owner_reference,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {
            "outcome": result.outcome.value,
            "definition": _definition_dto(result.subject),
        }

    @router.post("/api/v1/catalogues/application-definitions/{application_id}/components")
    def create_component(
        application_id: UUID,
        payload: CreateApplicationComponentRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.create_component.execute(
                CreateTargetComponentCommand(
                    application_id=application_id,
                    display_name=payload.display_name,
                    component_type=payload.component_type,
                    description=payload.description,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {"outcome": result.outcome.value, "component": _component_dto(result.component)}

    @router.post("/api/v1/catalogues/application-components/{component_id}/metadata")
    def update_component(
        component_id: UUID,
        payload: UpdateApplicationComponentRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.update_component_metadata.execute(
                UpdateComponentMetadataCommand(
                    component_id=component_id,
                    display_name=payload.display_name,
                    component_type=payload.component_type,
                    description=payload.description,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {"outcome": result.outcome.value, "component": _component_dto(result.subject)}

    @router.post("/api/v1/catalogues/application-definitions/{application_id}/interactions")
    def create_interaction(
        application_id: UUID,
        payload: CreateInteractionDefinitionRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.create_interaction_definition.execute(
                CreateInteractionDefinitionCommand(
                    application_id=application_id,
                    source_component_id=payload.source_component_id,
                    destination_component_id=payload.destination_component_id,
                    traffic_alternatives=tuple(
                        _traffic_alternative(item) for item in payload.traffic_alternatives
                    ),
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {
            "outcome": result.outcome.value,
            "interaction": _interaction_dto(result.interaction_definition),
        }

    @router.post("/api/v1/catalogues/interaction-definitions/{interaction_id}/endpoints")
    def update_interaction_endpoints(
        interaction_id: UUID,
        payload: UpdateInteractionEndpointsRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.update_interaction_endpoints.execute(
                UpdateInteractionDefinitionEndpointsCommand(
                    interaction_definition_id=interaction_id,
                    source_component_id=payload.source_component_id,
                    destination_component_id=payload.destination_component_id,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {
            "outcome": result.outcome.value,
            "interaction": _interaction_dto(result.interaction_definition),
        }

    @router.post("/api/v1/catalogues/interaction-definitions/{interaction_id}/traffic")
    def update_interaction_traffic(
        interaction_id: UUID,
        payload: UpdateInteractionTrafficRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        effective_time = clock()
        with open_scope() as scope:
            result = scope.applications.update_interaction_traffic.execute(
                UpdateInteractionDefinitionTrafficCommand(
                    interaction_definition_id=interaction_id,
                    traffic_alternatives=tuple(
                        _traffic_alternative(item) for item in payload.traffic_alternatives
                    ),
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=effective_time,
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {
            "outcome": result.outcome.value,
            "interaction": _interaction_dto(result.interaction_definition),
        }

    @router.post("/api/v1/catalogues/application-deployments")
    def create_deployment(
        payload: CreateApplicationDeploymentRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.create_application_deployment.execute(
                CreateApplicationDeploymentCommand(
                    application_id=payload.application_id,
                    company_reference=payload.company_reference,
                    environment=payload.environment,
                    scope_reference=payload.scope_reference,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {
            "outcome": result.outcome.value,
            "deployment": _deployment_dto(result.application_deployment),
        }

    @router.post("/api/v1/catalogues/application-deployments/{deployment_id}/context")
    def update_deployment(
        deployment_id: UUID,
        payload: UpdateApplicationDeploymentRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.update_application_deployment_context.execute(
                UpdateApplicationDeploymentContextCommand(
                    application_deployment_id=deployment_id,
                    company_reference=payload.company_reference,
                    environment=payload.environment,
                    scope_reference=payload.scope_reference,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {"outcome": result.outcome.value, "deployment": _deployment_dto(result.subject)}

    @router.post("/api/v1/catalogues/application-deployments/{deployment_id}/interactions")
    def select_interaction(
        deployment_id: UUID,
        payload: SelectDeploymentInteractionRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.select_deployment_interaction.execute(
                SelectDeploymentInteractionCommand(
                    application_deployment_id=deployment_id,
                    interaction_definition_id=payload.interaction_definition_id,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {
            "outcome": result.outcome.value,
            "deploymentInteraction": _deployment_interaction_dto(
                result.deployment_interaction
            ),
        }

    @router.post("/api/v1/catalogues/deployment-interactions/{interaction_id}/resource-bindings")
    def create_resource_binding(
        interaction_id: UUID,
        payload: CreateInteractionResourceBindingRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        _require_aware(payload.valid_from, "validFrom")
        if payload.valid_to is not None:
            _require_aware(payload.valid_to, "validTo")
        with open_scope() as scope:
            result = scope.applications.create_resource_binding.execute(
                CreateDeploymentInteractionResourceBindingCommand(
                    deployment_interaction_id=interaction_id,
                    side=payload.side,
                    resource_reference=payload.resource_reference,
                    valid_from=payload.valid_from,
                    valid_to=payload.valid_to,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {"outcome": result.outcome.value, "binding": _binding_dto(result.binding)}

    @router.post(
        "/api/v1/catalogues/deployment-interactions/{interaction_id}/resource-bindings/{binding_reference:path}/end"
    )
    def end_resource_binding(
        interaction_id: UUID,
        binding_reference: str,
        payload: EndInteractionResourceBindingRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        _require_aware(payload.valid_to, "validTo")
        with open_scope() as scope:
            result = scope.applications.end_resource_binding.execute(
                EndDeploymentInteractionResourceBindingCommand(
                    deployment_interaction_id=interaction_id,
                    side=payload.side,
                    binding_reference=binding_reference,
                    valid_to=payload.valid_to,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {"outcome": result.outcome.value, "binding": _binding_dto(result.binding)}

    return router


def _page_response(page, *, page: int, items: list[dict]) -> dict:
    return {
        "items": items,
        "page": page,
        "pageSize": page.limit,
        "total": page.total,
    }
