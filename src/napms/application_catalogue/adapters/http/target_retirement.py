from contextlib import AbstractContextManager
from datetime import datetime
from enum import Enum
from typing import Callable
from uuid import UUID

from fastapi import APIRouter, Header, Query, Request
from pydantic import BaseModel, ConfigDict, Field

from napms.application_catalogue.application.target_lifecycle import (
    RetireApplicationDefinitionCommand,
    RetireApplicationDeploymentCommand,
    RetireComponentTargetCommand,
    RetireDeploymentInteractionCommand,
    RetireInteractionDefinitionCommand,
    RetirementDependencyKind,
)
from napms.application_catalogue.application.target_retirement import RetirementSubjectKind
from napms.application_catalogue.adapters.http.target import (
    _dependency_details,
    _require_target_success,
)
from napms.runtime.auth import InMemorySessionStore
from napms.runtime.http_support import (
    PublicApiError,
    require_actor as _require_actor,
    require_aware as _require_aware,
)


class RetirementSubjectPath(str, Enum):
    APPLICATION_DEFINITION = "application-definition"
    COMPONENT = "component"
    INTERACTION_DEFINITION = "interaction-definition"
    APPLICATION_DEPLOYMENT = "application-deployment"
    DEPLOYMENT_INTERACTION = "deployment-interaction"


class RetireTargetRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    expected_version: int = Field(alias="expectedVersion", ge=1)


def create_catalogue_target_retirement_router(
    *,
    sessions: InMemorySessionStore,
    open_scope: Callable[[], AbstractContextManager],
    clock: Callable[[], datetime],
) -> APIRouter:
    router = APIRouter()

    @router.get("/api/v1/catalogues/deployment-interactions/{subject_id}")
    def read_deployment_interaction(subject_id: UUID, request: Request):
        _require_actor(sessions, request)
        with open_scope() as scope:
            value = scope.applications.deployment_interaction_read.get(subject_id)
        if value is None:
            _not_found()
        return {
            "deploymentInteraction": {
                "deploymentInteractionId": str(value.deployment_interaction_id),
                "applicationDeploymentId": str(value.application_deployment_id),
                "interactionDefinitionId": str(value.interaction_definition_id),
                "lifecycleState": value.lifecycle_state.value,
                "version": value.version,
            }
        }

    @router.get(
        "/api/v1/catalogues/retirement-dependencies/{subject_kind}/{subject_id}"
    )
    def summarize_dependencies(
        subject_kind: RetirementSubjectPath,
        subject_id: UUID,
        request: Request,
        asOf: datetime | None = Query(None),
    ):
        _require_actor(sessions, request)
        as_of = asOf or clock()
        _require_aware(as_of, "asOf")
        with open_scope() as scope:
            groups = scope.applications.retirement_dependencies.summarize(
                subject_kind=_subject_kind(subject_kind),
                subject_id=subject_id,
                as_of=as_of,
            )
        if groups is None:
            _not_found()
        return {
            "asOf": as_of.isoformat(),
            "dependencies": _groups_dto(groups),
        }

    @router.get(
        "/api/v1/catalogues/retirement-dependencies/{subject_kind}/{subject_id}/{dependency_kind}"
    )
    def page_dependencies(
        subject_kind: RetirementSubjectPath,
        subject_id: UUID,
        dependency_kind: RetirementDependencyKind,
        request: Request,
        page: int = Query(1, ge=1),
        pageSize: int = Query(50, ge=1, le=200),
        asOf: datetime | None = Query(None),
    ):
        _require_actor(sessions, request)
        as_of = asOf or clock()
        _require_aware(as_of, "asOf")
        try:
            with open_scope() as scope:
                group = scope.applications.retirement_dependencies.page(
                    subject_kind=_subject_kind(subject_kind),
                    subject_id=subject_id,
                    dependency_kind=dependency_kind,
                    as_of=as_of,
                    offset=(page - 1) * pageSize,
                    limit=pageSize,
                )
        except LookupError:
            _not_found()
        return {
            "items": [_reference_dto(item) for item in group.references],
            "page": page,
            "pageSize": pageSize,
            "total": group.total,
            "kind": group.kind.value,
            "asOf": as_of.isoformat(),
        }

    @router.post("/api/v1/catalogues/application-definitions/{subject_id}/retire")
    def retire_definition(
        subject_id: UUID,
        payload: RetireTargetRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key", min_length=1, max_length=256
        ),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.retire_definition.execute(
                RetireApplicationDefinitionCommand(
                    application_id=subject_id,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        return _retirement_response(result, RetirementSubjectKind.APPLICATION_DEFINITION)

    @router.post("/api/v1/catalogues/application-components/{subject_id}/retire")
    def retire_component(
        subject_id: UUID,
        payload: RetireTargetRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key", min_length=1, max_length=256
        ),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.retire_component.execute(
                RetireComponentTargetCommand(
                    component_id=subject_id,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        return _retirement_response(result, RetirementSubjectKind.COMPONENT)

    @router.post("/api/v1/catalogues/interaction-definitions/{subject_id}/retire")
    def retire_interaction_definition(
        subject_id: UUID,
        payload: RetireTargetRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key", min_length=1, max_length=256
        ),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.retire_interaction_definition.execute(
                RetireInteractionDefinitionCommand(
                    interaction_definition_id=subject_id,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        return _retirement_response(result, RetirementSubjectKind.INTERACTION_DEFINITION)

    @router.post("/api/v1/catalogues/application-deployments/{subject_id}/retire")
    def retire_application_deployment(
        subject_id: UUID,
        payload: RetireTargetRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key", min_length=1, max_length=256
        ),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.retire_application_deployment.execute(
                RetireApplicationDeploymentCommand(
                    application_deployment_id=subject_id,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        return _retirement_response(result, RetirementSubjectKind.APPLICATION_DEPLOYMENT)

    @router.post("/api/v1/catalogues/deployment-interactions/{subject_id}/retire")
    def retire_deployment_interaction(
        subject_id: UUID,
        payload: RetireTargetRequest,
        request: Request,
        idempotency_key: str = Header(
            alias="Idempotency-Key", min_length=1, max_length=256
        ),
    ):
        actor_id = _require_actor(sessions, request)
        with open_scope() as scope:
            result = scope.applications.retire_deployment_interaction.execute(
                RetireDeploymentInteractionCommand(
                    deployment_interaction_id=subject_id,
                    expected_version=payload.expected_version,
                    actor_id=actor_id,
                    effective_time=clock(),
                    idempotency_key=idempotency_key,
                )
            )
        return _retirement_response(result, RetirementSubjectKind.DEPLOYMENT_INTERACTION)

    return router


def _subject_kind(value: RetirementSubjectPath) -> RetirementSubjectKind:
    return {
        RetirementSubjectPath.APPLICATION_DEFINITION: RetirementSubjectKind.APPLICATION_DEFINITION,
        RetirementSubjectPath.COMPONENT: RetirementSubjectKind.COMPONENT,
        RetirementSubjectPath.INTERACTION_DEFINITION: RetirementSubjectKind.INTERACTION_DEFINITION,
        RetirementSubjectPath.APPLICATION_DEPLOYMENT: RetirementSubjectKind.APPLICATION_DEPLOYMENT,
        RetirementSubjectPath.DEPLOYMENT_INTERACTION: RetirementSubjectKind.DEPLOYMENT_INTERACTION,
    }[value]


def _retirement_response(result, subject_kind: RetirementSubjectKind) -> dict:
    _require_target_success(result)
    subject = result.subject
    if subject is None:
        raise PublicApiError(
            status_code=503,
            code="CataloguePersistenceOutcomeUnknown",
            message="The retired catalogue subject could not be resolved authoritatively.",
        )
    return {
        "outcome": result.outcome.value,
        "subject": {
            "kind": subject_kind.value,
            "reference": str(_subject_reference(subject_kind, subject)),
            "lifecycleState": subject.lifecycle_state.value,
            "version": subject.version,
        },
    }


def _subject_reference(subject_kind: RetirementSubjectKind, subject) -> UUID:
    attribute = {
        RetirementSubjectKind.APPLICATION_DEFINITION: "application_id",
        RetirementSubjectKind.COMPONENT: "component_id",
        RetirementSubjectKind.INTERACTION_DEFINITION: "interaction_definition_id",
        RetirementSubjectKind.APPLICATION_DEPLOYMENT: "application_deployment_id",
        RetirementSubjectKind.DEPLOYMENT_INTERACTION: "deployment_interaction_id",
    }[subject_kind]
    return getattr(subject, attribute)


def _groups_dto(groups) -> list[dict]:
    return [
        {
            "kind": group.kind.value,
            "count": group.count,
            "preview": [_reference_dto(item) for item in group.references],
        }
        for group in groups
    ]


def _reference_dto(value) -> dict:
    return {
        "reference": value.reference,
        "displayName": value.display_name,
    }


def _not_found() -> None:
    raise PublicApiError(
        status_code=404,
        code="CatalogueSubjectNotFound",
        message="The catalogue retirement subject was not found.",
    )
