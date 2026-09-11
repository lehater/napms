from contextlib import AbstractContextManager
from datetime import datetime
from typing import Callable
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from napms.application_catalogue.adapters.dcs_json_codec import JsonDcsProjectionCodec
from napms.application_catalogue.adapters.http.legacy_curation import (
    _application_dto,
    _binding_dto,
    _component_dto,
    _deployment_dto,
)
from napms.application_catalogue.application.deployment_curation import (
    RenameComponentDeploymentCommand,
    RetireComponentDeploymentCommand,
)
from napms.application_catalogue.application.structure_curation import (
    RenameApplicationCommand,
    RenameComponentCommand,
    RetireApplicationCommand,
    RetireComponentCommand,
)
from napms.policy_export.application.normalization_ports import DcsProjectionDecodeError
from napms.runtime.auth import InMemorySessionStore
from napms.runtime.http_support import PublicApiError
from napms.runtime.http_support import (
    mutation_response,
    require_actor,
    require_aware,
    require_mutation_success,
)
from napms.policy_export.adapters.http_json import port_constraint_json


class RenameCatalogueEntityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    display_name: str = Field(alias="displayName", min_length=1, max_length=256)
    expected_version: int = Field(alias="expectedVersion", ge=1)


class RenameCatalogueDeploymentRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    display_name: str | None = Field(
        default=None,
        alias="displayName",
        min_length=1,
        max_length=256,
    )
    expected_version: int = Field(alias="expectedVersion", ge=1)


class RetireCatalogueEntityRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    expected_version: int = Field(alias="expectedVersion", ge=1)


def create_catalogue_application_workspace_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager],
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()
    decoder = JsonDcsProjectionCodec()

    @router.get(
        "/api/v1/catalogues/application-workspace/{application_id}",
        name="ReadCatalogueApplicationWorkspace",
    )
    def read_application_workspace(
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
        return _application_workspace_dto(result, decoder=decoder)

    @router.post(
        "/api/v1/catalogues/applications/{application_id}/rename",
        name="RenameCatalogueApplication",
    )
    def rename_application(
        application_id: UUID,
        payload: RenameCatalogueEntityRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.rename_application.execute(
                RenameApplicationCommand(
                    application_id=application_id,
                    display_name=payload.display_name,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        require_mutation_success(result.outcome)
        return mutation_response(
            result.outcome,
            {"application": _application_dto(result.application)},
        )

    @router.post(
        "/api/v1/catalogues/applications/{application_id}/retire",
        name="RetireCatalogueApplication",
    )
    def retire_application(
        application_id: UUID,
        payload: RetireCatalogueEntityRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.retire_application.execute(
                RetireApplicationCommand(
                    application_id=application_id,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        require_mutation_success(result.outcome)
        return mutation_response(
            result.outcome,
            {"application": _application_dto(result.application)},
        )

    @router.post(
        "/api/v1/catalogues/components/{component_id}/rename",
        name="RenameCatalogueComponent",
    )
    def rename_component(
        component_id: UUID,
        payload: RenameCatalogueEntityRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.rename_component.execute(
                RenameComponentCommand(
                    component_id=component_id,
                    display_name=payload.display_name,
                    expected_version=payload.expected_version,
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
        "/api/v1/catalogues/components/{component_id}/retire",
        name="RetireCatalogueComponent",
    )
    def retire_component(
        component_id: UUID,
        payload: RetireCatalogueEntityRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.retire_component.execute(
                RetireComponentCommand(
                    component_id=component_id,
                    expected_version=payload.expected_version,
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
        "/api/v1/catalogues/deployments/{deployment_id}/rename",
        name="RenameCatalogueComponentDeployment",
    )
    def rename_component_deployment(
        deployment_id: UUID,
        payload: RenameCatalogueDeploymentRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.rename_component_deployment.execute(
                RenameComponentDeploymentCommand(
                    deployment_id=deployment_id,
                    display_name=payload.display_name,
                    expected_version=payload.expected_version,
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

    @router.post(
        "/api/v1/catalogues/deployments/{deployment_id}/retire",
        name="RetireCatalogueComponentDeployment",
    )
    def retire_component_deployment(
        deployment_id: UUID,
        payload: RetireCatalogueEntityRequest,
        request: Request,
        idempotency_key: str = Header(alias="Idempotency-Key", min_length=1, max_length=256),
    ):
        actor_id = require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.retire_component_deployment.execute(
                RetireComponentDeploymentCommand(
                    deployment_id=deployment_id,
                    expected_version=payload.expected_version,
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

    return router


def _application_workspace_dto(value, *, decoder: JsonDcsProjectionCodec) -> dict:
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
                            _dcs_summary_dto(revision, decoder=decoder)
                            for revision in deployment.dcs_revisions
                        ],
                    }
                    for deployment in component.deployments
                ],
            }
            for component in value.components
        ],
    }


def _dcs_summary_dto(value, *, decoder: JsonDcsProjectionCodec) -> dict:
    try:
        alternatives = decoder.decode(value.projection_payload)
    except DcsProjectionDecodeError:
        alternatives = ()
    return {
        "revisionId": str(value.revision_id),
        "sourceComponentDeploymentId": str(value.source_component_deployment_id),
        "destinationComponentDeploymentId": str(value.destination_component_deployment_id),
        "displayName": value.display_name,
        "provenanceReference": value.provenance_reference,
        "trafficAlternatives": [
            {
                "protocol": alternative.protocol,
                "sourcePorts": port_constraint_json(alternative.source_ports),
                "destinationPorts": port_constraint_json(alternative.destination_ports),
                "serviceReference": alternative.service_reference,
            }
            for alternative in alternatives
        ],
    }
