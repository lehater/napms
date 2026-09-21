from __future__ import annotations

from typing import Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict

from napms.contexts.application_deployment.application.ports import DeploymentNotFound
from napms.contexts.application_deployment.application.service import ApplicationDeploymentService
from napms.contexts.authority_management.domain.model import Principal
from napms.contexts.business_connectivity.application.ports import (
    BusinessConnectivityNotFound,
    BusinessConnectivityVersionConflict,
)
from napms.contexts.business_connectivity.application.service import BusinessConnectivityService


def _camel(name: str) -> str:
    first, *rest = name.split("_")
    return first + "".join(part.capitalize() for part in rest)


class IdentityDependency(Protocol):
    def __call__(self) -> Principal: ...


class _Body(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=False, alias_generator=_camel)


class DeploymentBody(_Body):
    component_ref: UUID
    resource_ref: UUID


class ProcessBody(_Body):
    name: str
    description: str | None = None
    criticality_label: str | None = None


class CriticalityBody(_Body):
    criticality_label: str | None


class NeedBody(_Body):
    interaction_ref: UUID
    participant_component_ref: UUID
    business_basis: str


def router(
    *,
    deployments: ApplicationDeploymentService,
    connectivity: BusinessConnectivityService,
    identity: IdentityDependency,
) -> APIRouter:
    api = APIRouter(prefix="/v1")

    def permission(caller: Principal, value: str) -> None:
        if value not in caller.instance_permissions:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

    def version(value: str) -> int:
        try:
            return int(value.strip().strip('"'))
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc

    @api.post("/deployments", status_code=status.HTTP_201_CREATED)
    def create_deployment(
        body: DeploymentBody, caller: Principal = Depends(identity)
    ) -> dict[str, object]:
        permission(caller, "deployment.write")
        try:
            value = deployments.register_component_deployment(
                component_ref=body.component_ref,
                resource_ref=body.resource_ref,
            )
        except DeploymentNotFound as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        return {
            "deploymentRef": str(value.deployment_ref),
            "componentRef": str(value.component_ref),
            "resourceRef": str(value.resource_ref),
        }

    @api.post("/processes", status_code=status.HTTP_201_CREATED)
    def create_process(
        body: ProcessBody, caller: Principal = Depends(identity)
    ) -> dict[str, object]:
        permission(caller, "business.write")
        try:
            value = connectivity.register_business_process(
                name=body.name,
                description=body.description,
                criticality_label=body.criticality_label,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        return {"processRef": str(value.process_ref), "version": value.version}

    @api.put("/processes/{process_ref}/criticality")
    def set_criticality(
        process_ref: UUID,
        body: CriticalityBody,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "business.write")
        try:
            value = connectivity.set_criticality_label(
                process_ref=process_ref,
                criticality_label=body.criticality_label,
                expected_version=version(if_match),
            )
        except BusinessConnectivityVersionConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        except BusinessConnectivityNotFound as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        return {"processRef": str(value.process_ref), "version": value.version}

    @api.post("/processes/{process_ref}/needs", status_code=status.HTTP_201_CREATED)
    def declare_need(
        process_ref: UUID,
        body: NeedBody,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "business.write")
        try:
            value = connectivity.declare_need(
                process_ref=process_ref,
                interaction_ref=body.interaction_ref,
                participant_component_ref=body.participant_component_ref,
                business_basis=body.business_basis,
                subject=caller.subject,
                expected_version=version(if_match),
            )
        except BusinessConnectivityVersionConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        except (BusinessConnectivityNotFound, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        need = value.needs[-1]
        return {
            "processRef": str(value.process_ref),
            "needRef": str(need.need_ref),
            "version": value.version,
        }

    return api
