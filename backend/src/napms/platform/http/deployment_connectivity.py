from __future__ import annotations

from datetime import datetime, timezone
from typing import Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict

from napms.contexts.application_deployment.application.ports import DeploymentNotFound
from napms.contexts.application_deployment.application.queries import (
    DeploymentCatalogueQuery,
    DeploymentSortField,
    SortDirection,
)
from napms.contexts.application_deployment.application.service import ApplicationDeploymentService
from napms.contexts.authority_management.domain.model import Principal
from napms.contexts.business_connectivity.application.ports import (
    BusinessConnectivityNotFound,
    BusinessConnectivityVersionConflict,
)
from napms.contexts.business_connectivity.application.queries import (
    BusinessProcessCatalogueQuery,
    BusinessProcessSortField,
    SortDirection as BusinessProcessSortDirection,
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


class ResponsibleOrganizationBody(_Body):
    external_reference: str | None = None
    display_name: str | None = None


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

    def deployment_view(value) -> dict[str, str]:
        return {
            "deploymentRef": str(value.deployment_ref),
            "componentRef": str(value.component_ref),
            "resourceRef": str(value.resource_ref),
        }

    @api.get("/deployments")
    def list_deployments(
        search: str | None = Query(default=None, max_length=200),
        component_ref: UUID | None = Query(default=None, alias="componentRef"),
        resource_ref: UUID | None = Query(default=None, alias="resourceRef"),
        sort_by: DeploymentSortField = Query(
            default=DeploymentSortField.DEPLOYMENT_REF,
            alias="sortBy",
        ),
        sort_direction: SortDirection = Query(
            default=SortDirection.ASC,
            alias="sortDirection",
        ),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=25, ge=1, le=100, alias="pageSize"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "deployment.read")
        result = deployments.list_component_deployments(
            DeploymentCatalogueQuery(
                search=search.strip() if search and search.strip() else None,
                component_ref=component_ref,
                resource_ref=resource_ref,
                sort_by=sort_by,
                sort_direction=sort_direction,
                page=page,
                page_size=page_size,
            )
        )
        return {
            "items": [deployment_view(value) for value in result.items],
            "total": result.total,
            "page": result.page,
            "pageSize": result.page_size,
        }

    @api.get("/deployments/{deployment_ref}")
    def get_deployment(
        deployment_ref: UUID,
        caller: Principal = Depends(identity),
    ) -> dict[str, str]:
        permission(caller, "deployment.read")
        try:
            value = deployments.resolve_component_deployment(deployment_ref)
        except DeploymentNotFound as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc
        return deployment_view(value)

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

    def process_view(value) -> dict[str, object]:
        return {
            "processRef": str(value.process_ref),
            "name": value.name,
            "description": value.description,
            "organizationExternalReference": value.organization_external_reference,
            "organizationDisplayName": value.organization_display_name,
            "criticalityLabel": value.criticality_label,
            "version": value.version,
            "needs": [
                {
                    "needRef": str(need.need_ref),
                    "interactionRef": str(need.interaction_ref),
                    "participantComponentRef": str(need.participant_component_ref),
                    "businessBasis": need.business_basis,
                    "status": need.status.value,
                }
                for need in value.needs
            ],
        }

    @api.get("/processes")
    def list_processes(
        search: str | None = Query(default=None, max_length=200),
        criticality_label: str | None = Query(default=None, alias="criticalityLabel"),
        organization_external_reference: str | None = Query(
            default=None,
            alias="organizationExternalReference",
        ),
        sort_by: BusinessProcessSortField = Query(
            default=BusinessProcessSortField.NAME,
            alias="sortBy",
        ),
        sort_direction: BusinessProcessSortDirection = Query(
            default=BusinessProcessSortDirection.ASC,
            alias="sortDirection",
        ),
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=25, ge=1, le=100, alias="pageSize"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "business.read")
        result = connectivity.list_business_processes(
            BusinessProcessCatalogueQuery(
                search=search.strip() if search and search.strip() else None,
                criticality_label=(
                    criticality_label.strip()
                    if criticality_label and criticality_label.strip()
                    else None
                ),
                organization_external_reference=(
                    organization_external_reference.strip()
                    if organization_external_reference
                    and organization_external_reference.strip()
                    else None
                ),
                sort_by=sort_by,
                sort_direction=sort_direction,
                page=page,
                page_size=page_size,
            )
        )
        return {
            "items": [process_view(value) for value in result.items],
            "total": result.total,
            "page": result.page,
            "pageSize": result.page_size,
        }

    @api.get("/processes/{process_ref}")
    def get_process(
        process_ref: UUID,
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "business.read")
        try:
            value = connectivity.resolve_business_process(process_ref)
        except BusinessConnectivityNotFound as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc
        return process_view(value)

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

    @api.put("/processes/{process_ref}/responsible-organization")
    def set_responsible_organization(
        process_ref: UUID,
        body: ResponsibleOrganizationBody,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "business.write")
        try:
            value = connectivity.set_responsible_organization(
                process_ref=process_ref,
                external_reference=body.external_reference,
                display_name=body.display_name,
                expected_version=version(if_match),
            )
        except BusinessConnectivityVersionConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        except BusinessConnectivityNotFound as exc:
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

    @api.post("/processes/{process_ref}/needs/{need_ref}/retirement")
    def retire_need(
        process_ref: UUID,
        need_ref: UUID,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "business.write")
        try:
            value = connectivity.retire_need(
                process_ref=process_ref,
                need_ref=need_ref,
                retired_at=datetime.now(timezone.utc),
                expected_version=version(if_match),
            )
        except BusinessConnectivityVersionConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        except (BusinessConnectivityNotFound, ValueError) as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        return {
            "processRef": str(value.process_ref),
            "needRef": str(need_ref),
            "version": value.version,
        }

    return api
