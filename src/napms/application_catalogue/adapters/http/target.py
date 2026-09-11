from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from napms.application_catalogue.adapters.http.legacy_curation import (
    DcsTrafficAlternativeValue,
    _traffic_alternative,
)
from napms.application_catalogue.application.curation import CreateApplicationCommand
from napms.application_catalogue.application.target_binding_curation import (
    CreateDeploymentInteractionResourceBindingCommand,
    EndDeploymentInteractionResourceBindingCommand,
)
from napms.application_catalogue.application.target_curation import (
    CreateApplicationDeploymentCommand,
    CreateInteractionDefinitionCommand,
    SelectDeploymentInteractionCommand,
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
from napms.runtime.http_support import PublicApiError
from napms.runtime.http_support import require_actor as _require_actor
from napms.runtime.http_support import require_aware as _require_aware


_SUCCESS_OUTCOMES = {"Created", "Updated", "Resolved"}


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
    company_reference: str = Field(
        alias="companyReference", min_length=1, max_length=2048
    )
    environment: str = Field(min_length=1, max_length=256)
    scope_reference: str = Field(alias="scopeReference", min_length=1, max_length=2048)


class UpdateApplicationDeploymentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    company_reference: str = Field(
        alias="companyReference", min_length=1, max_length=2048
    )
    environment: str = Field(min_length=1, max_length=256)
    scope_reference: str = Field(alias="scopeReference", min_length=1, max_length=2048)
    expected_version: int = Field(alias="expectedVersion", ge=1)


class SelectDeploymentInteractionRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    interaction_definition_id: UUID = Field(alias="interactionDefinitionId")


class CreateInteractionResourceBindingRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    side: DeploymentInteractionSide
    resource_reference: str = Field(
        alias="resourceReference", min_length=1, max_length=2048
    )
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
            page_number=page,
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
            page_number=page,
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
            page_number=page,
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
            page_number=page,
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
            page_number=page,
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
            page_number=page,
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
            page_number=page,
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
            page_number=page,
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
            "definition": _definition_dto(_required_result(result.application)),
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
            "definition": _definition_dto(_required_result(result.subject)),
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
        return {
            "outcome": result.outcome.value,
            "component": _component_dto(_required_result(result.component)),
        }

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
        return {
            "outcome": result.outcome.value,
            "component": _component_dto(_required_result(result.subject)),
        }

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
            "interaction": _interaction_dto(
                _required_result(result.interaction_definition)
            ),
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
            "interaction": _interaction_dto(
                _required_result(result.interaction_definition)
            ),
        }

    @router.post("/api/v1/catalogues/interaction-definitions/{interaction_id}/traffic")
    def update_interaction_traffic(
        interaction_id: UUID,
        payload: UpdateInteractionTrafficRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.update_interaction_traffic.execute(
                UpdateInteractionDefinitionTrafficCommand(
                    interaction_definition_id=interaction_id,
                    traffic_alternatives=tuple(
                        _traffic_alternative(item) for item in payload.traffic_alternatives
                    ),
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        _require_target_success(result)
        return {
            "outcome": result.outcome.value,
            "interaction": _interaction_dto(
                _required_result(result.interaction_definition)
            ),
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
            "deployment": _deployment_dto(
                _required_result(result.application_deployment)
            ),
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
        return {
            "outcome": result.outcome.value,
            "deployment": _deployment_dto(_required_result(result.subject)),
        }

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
                _required_result(result.deployment_interaction)
            ),
        }

    @router.post(
        "/api/v1/catalogues/deployment-interactions/{interaction_id}/resource-bindings"
    )
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
        return {
            "outcome": result.outcome.value,
            "binding": _binding_dto(_required_result(result.binding)),
        }

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
        return {
            "outcome": result.outcome.value,
            "binding": _binding_dto(_required_result(result.binding)),
        }

    return router


def _page_response(page_info, *, page_number: int, items: list[dict]) -> dict:
    return {
        "items": items,
        "page": page_number,
        "pageSize": page_info.limit,
        "total": page_info.total,
    }


def _definition_dto(value) -> dict:
    return {
        "applicationId": str(value.application_id),
        "displayName": value.display_name,
        "description": value.description,
        "domain": value.domain,
        "ownerReference": value.owner_reference,
        "lifecycleState": value.lifecycle_state.value,
        "version": value.version,
    }


def _definition_summary_dto(value) -> dict:
    return {
        **_definition_dto(value.application),
        "componentCount": value.component_count,
        "interactionCount": value.interaction_count,
        "deploymentCount": value.deployment_count,
    }


def _component_dto(value) -> dict:
    return {
        "componentId": str(value.component_id),
        "applicationId": str(value.application_id),
        "displayName": value.display_name,
        "componentType": value.component_type,
        "description": value.description,
        "lifecycleState": value.lifecycle_state.value,
        "version": value.version,
    }


def _interaction_dto(value) -> dict:
    return {
        "interactionDefinitionId": str(value.interaction_definition_id),
        "applicationId": str(value.application_id),
        "sourceComponentId": str(value.source_component_id),
        "destinationComponentId": str(value.destination_component_id),
        "trafficAlternatives": [_traffic_dto(item) for item in value.traffic_alternatives],
        "lifecycleState": value.lifecycle_state.value,
        "version": value.version,
    }


def _interaction_summary_dto(value) -> dict:
    return {
        **_interaction_dto(value.interaction),
        "sourceComponentName": value.source_component_name,
        "destinationComponentName": value.destination_component_name,
        "activeDeploymentCount": value.active_deployment_count,
    }


def _deployment_dto(value) -> dict:
    return {
        "applicationDeploymentId": str(value.application_deployment_id),
        "applicationId": str(value.application_id),
        "companyReference": value.company_reference,
        "environment": value.environment,
        "scopeReference": value.scope_reference,
        "lifecycleState": value.lifecycle_state.value,
        "version": value.version,
    }


def _deployment_summary_dto(value) -> dict:
    return {
        **_deployment_dto(value.deployment),
        "applicationName": value.application_name,
        "selectedInteractionCount": value.selected_interaction_count,
        "definedInteractionCount": value.available_interaction_count,
    }


def _deployment_interaction_dto(value) -> dict:
    return {
        "deploymentInteractionId": str(value.deployment_interaction_id),
        "applicationDeploymentId": str(value.application_deployment_id),
        "interactionDefinitionId": str(value.interaction_definition_id),
        "lifecycleState": value.lifecycle_state.value,
        "version": value.version,
    }


def _connectivity_dto(value) -> dict:
    return {
        "deploymentInteractionId": str(value.deployment_interaction_id),
        "interactionDefinitionId": str(value.interaction_definition_id),
        "sourceComponent": {
            "componentId": str(value.source_component_id),
            "displayName": value.source_component_name,
            "resourceCount": value.source_resource_count,
        },
        "destinationComponent": {
            "componentId": str(value.destination_component_id),
            "displayName": value.destination_component_name,
            "resourceCount": value.destination_resource_count,
        },
        "trafficAlternatives": [_traffic_dto(item) for item in value.traffic_alternatives],
    }


def _resource_member_dto(value) -> dict:
    return {
        "bindingReference": value.binding_reference,
        "bindingVersion": value.binding_version,
        "resourceReference": value.resource_reference,
        "displayName": value.display_name,
        "scopeReferences": list(value.scope_references),
        "validFrom": value.valid_from.isoformat(),
        "validTo": value.valid_to.isoformat() if value.valid_to is not None else None,
    }


def _binding_dto(value) -> dict:
    return {
        "bindingReference": value.reference_id,
        "deploymentInteractionId": str(value.deployment_interaction_id),
        "side": value.side.value,
        "resourceReference": value.resource_reference,
        "validFrom": value.valid_from.isoformat(),
        "validTo": value.valid_to.isoformat() if value.valid_to is not None else None,
        "version": value.version,
    }


def _traffic_dto(value: AuthoredDcsTrafficAlternative) -> dict:
    return {
        "protocol": value.protocol,
        "sourcePorts": _constraint_dto(value.source_ports),
        "destinationPorts": _constraint_dto(value.destination_ports),
        "serviceReference": value.service_reference,
    }


def _constraint_dto(value: DcsPortConstraint) -> dict:
    result: dict[str, object] = {"kind": value.kind.value}
    if value.ranges:
        result["ranges"] = [
            {"first": item.first, "last": item.last} for item in value.ranges
        ]
    return result


def _required_result(value):
    if value is None:
        raise PublicApiError(
            status_code=503,
            code="CataloguePersistenceOutcomeUnknown",
            message="The catalogue result could not be resolved authoritatively.",
        )
    return value


def _not_found(subject: str) -> None:
    raise PublicApiError(
        status_code=404,
        code="CatalogueSubjectNotFound",
        message=f"The {subject} was not found.",
    )


def _require_target_success(result) -> None:
    outcome = result.outcome.value
    if outcome in _SUCCESS_OUTCOMES:
        return
    if outcome == "DependencyBlocked":
        raise PublicApiError(
            status_code=409,
            code="CatalogueDependencyBlocked",
            message="The catalogue mutation is blocked by active dependencies.",
            details={"dependencies": _dependency_details(result)},
        )
    mapping = {
        "AuthorityDenied": (
            403,
            "CatalogueAuthorityDenied",
            "The actor is not authorized to curate the Application Catalogue.",
        ),
        "AuthorityUnknown": (
            409,
            "CatalogueAuthorityUnknown",
            "Application Catalogue mutation authority could not be resolved.",
        ),
        "NotFound": (
            404,
            "CatalogueSubjectNotFound",
            "The catalogue subject was not found.",
        ),
        "ParentInactive": (
            409,
            "CatalogueParentInactive",
            "The required catalogue parent is not Active.",
        ),
        "AlreadyExists": (
            409,
            "CatalogueAlreadyExists",
            "The requested Active catalogue relation already exists.",
        ),
        "InputInvalid": (
            422,
            "CatalogueInputInvalid",
            "The request violates the Application Catalogue contract.",
        ),
        "ConcurrencyConflict": (
            409,
            "CatalogueConcurrencyConflict",
            "The catalogue subject changed since the supplied version.",
        ),
        "IdempotencyConflict": (
            409,
            "CatalogueIdempotencyConflict",
            "The idempotency key was already used for a different request.",
        ),
        "PersistenceUnknown": (
            503,
            "CataloguePersistenceOutcomeUnknown",
            "The catalogue persistence outcome could not be confirmed.",
        ),
    }
    status_code, code, message = mapping.get(
        outcome,
        (503, "CatalogueUnavailable", "The Application Catalogue operation failed."),
    )
    raise PublicApiError(
        status_code=status_code,
        code=code,
        message=message,
        dependency=(
            "AuthorityManagement"
            if code in {"AuthorityDenied", "AuthorityUnknown"}
            else (
                "ApplicationCommunicationCatalogue"
                if code == "CatalogueUnavailable"
                else None
            )
        ),
    )


def _dependency_details(result) -> list[dict]:
    details = []
    for group in getattr(result, "dependencies", ()):
        details.append(
            {
                "kind": group.kind.value,
                "count": group.count,
                "preview": [
                    {
                        "reference": item.reference,
                        "displayName": item.display_name,
                    }
                    for item in group.references
                ],
            }
        )
    return details
