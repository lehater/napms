from __future__ import annotations

from typing import Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

from napms.contexts.application_communication_catalogue.application.ports import (
    CatalogueNotFound,
    CatalogueVersionConflict,
)
from napms.contexts.application_communication_catalogue.application.queries import (
    ApplicationCatalogueQuery,
    ApplicationSortField,
    SortDirection,
)
from napms.contexts.application_communication_catalogue.application.service import (
    ApplicationCommunicationCatalogue,
)
from napms.contexts.application_communication_catalogue.domain.model import (
    Interaction,
    PortRange,
    TrafficClause,
)
from napms.contexts.authority_management.domain.model import Principal


def _camel(name: str) -> str:
    first, *rest = name.split("_")
    return first + "".join(part.capitalize() for part in rest)


class IdentityDependency(Protocol):
    def __call__(self) -> Principal: ...


class _Body(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=False, alias_generator=_camel)


class NamedBody(_Body):
    name: str


class InteractionBody(_Body):
    source_component_ref: UUID
    destination_component_ref: UUID
    purpose: str | None = None


class PortRangeBody(_Body):
    start: int = Field(alias="from")
    end: int = Field(alias="to")


class TrafficClauseBody(_Body):
    ip_protocol: int
    source_ports: tuple[PortRangeBody, ...] = ()
    destination_ports: tuple[PortRangeBody, ...] = ()


class RevisionBody(_Body):
    traffic_clauses: tuple[TrafficClauseBody, ...]


def router(
    *,
    catalogue: ApplicationCommunicationCatalogue,
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

    def execute(call):
        try:
            return call()
        except CatalogueVersionConflict as exc:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT) from exc
        except CatalogueNotFound as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT) from exc

    def clause_view(clause: TrafficClause) -> dict[str, object]:
        return {
            "ipProtocol": clause.ip_protocol,
            "sourcePorts": [{"from": item.start, "to": item.end} for item in clause.source_ports],
            "destinationPorts": [
                {"from": item.start, "to": item.end} for item in clause.destination_ports
            ],
        }

    def component_name(component_ref: UUID) -> str:
        try:
            return catalogue.resolve_component(component_ref).name
        except CatalogueNotFound as exc:
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE) from exc

    def interaction_view(item: Interaction) -> dict[str, object]:
        return {
            "interactionRef": str(item.interaction_ref),
            "sourceComponentRef": str(item.source_component_ref),
            "sourceComponentName": component_name(item.source_component_ref),
            "destinationComponentRef": str(item.destination_component_ref),
            "destinationComponentName": component_name(item.destination_component_ref),
            "purpose": item.purpose,
            "version": item.version,
            "revisions": [
                {
                    "interactionRevisionRef": str(revision.revision_ref),
                    "revisionNo": revision.revision_no,
                    "trafficClauses": [clause_view(clause) for clause in revision.traffic_clauses],
                    "createdBySubject": revision.created_by_subject,
                }
                for revision in item.revisions
            ],
        }

    @api.get("/applications")
    def list_applications(
        search: str | None = Query(default=None, max_length=200),
        component_ref: UUID | None = Query(default=None, alias="componentRef"),
        sort_by: ApplicationSortField = Query(
            default=ApplicationSortField.NAME,
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
        permission(caller, "application.read")
        result = catalogue.list_applications(
            ApplicationCatalogueQuery(
                search=search.strip() if search and search.strip() else None,
                component_ref=component_ref,
                sort_by=sort_by,
                sort_direction=sort_direction,
                page=page,
                page_size=page_size,
            )
        )
        return {
            "items": [
                {
                    "applicationRef": str(value.application_ref),
                    "name": value.name,
                    "version": value.version,
                    "components": [
                        {"componentRef": str(item.component_ref), "name": item.name}
                        for item in value.components
                    ],
                }
                for value in result.items
            ],
            "total": result.total,
            "page": result.page,
            "pageSize": result.page_size,
        }

    @api.get("/applications/{application_ref}")
    def get_application(
        application_ref: UUID,
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "application.read")
        try:
            application, interactions = catalogue.get_application_detail(application_ref)
        except CatalogueNotFound as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc

        return {
            "applicationRef": str(application.application_ref),
            "name": application.name,
            "version": application.version,
            "components": [
                {"componentRef": str(item.component_ref), "name": item.name}
                for item in application.components
            ],
            "interactions": [interaction_view(item) for item in interactions],
        }

    @api.post("/applications", status_code=status.HTTP_201_CREATED)
    def create_application(
        body: NamedBody, caller: Principal = Depends(identity)
    ) -> dict[str, object]:
        permission(caller, "application.write")
        value = execute(lambda: catalogue.create_application(name=body.name))
        return {"applicationRef": str(value.application_ref), "version": value.version}

    @api.post("/applications/{application_ref}/components", status_code=status.HTTP_201_CREATED)
    def add_component(
        application_ref: UUID,
        body: NamedBody,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "application.write")
        value = execute(
            lambda: catalogue.add_component(
                application_ref=application_ref,
                name=body.name,
                expected_version=version(if_match),
            )
        )
        component = value.components[-1]
        return {
            "applicationRef": str(value.application_ref),
            "componentRef": str(component.component_ref),
            "version": value.version,
        }

    @api.get("/interactions/{interaction_ref}")
    def get_interaction(
        interaction_ref: UUID,
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "application.read")
        try:
            item = catalogue.get_interaction(interaction_ref)
        except CatalogueNotFound as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND) from exc
        return interaction_view(item)

    @api.post("/interactions", status_code=status.HTTP_201_CREATED)
    def create_interaction(
        body: InteractionBody, caller: Principal = Depends(identity)
    ) -> dict[str, object]:
        permission(caller, "application.write")
        value = execute(
            lambda: catalogue.create_interaction(
                source_component_ref=body.source_component_ref,
                destination_component_ref=body.destination_component_ref,
                purpose=body.purpose,
            )
        )
        return {"interactionRef": str(value.interaction_ref), "version": value.version}

    @api.post(
        "/interactions/{interaction_ref}/revisions",
        status_code=status.HTTP_201_CREATED,
    )
    def publish_revision(
        interaction_ref: UUID,
        body: RevisionBody,
        if_match: str = Header(alias="If-Match"),
        caller: Principal = Depends(identity),
    ) -> dict[str, object]:
        permission(caller, "application.write")
        clauses = tuple(
            TrafficClause(
                ip_protocol=item.ip_protocol,
                source_ports=tuple(
                    PortRange(start=port.start, end=port.end) for port in item.source_ports
                ),
                destination_ports=tuple(
                    PortRange(start=port.start, end=port.end) for port in item.destination_ports
                ),
            )
            for item in body.traffic_clauses
        )
        value = execute(
            lambda: catalogue.publish_interaction_revision(
                interaction_ref=interaction_ref,
                traffic_clauses=clauses,
                expected_version=version(if_match),
                subject=caller.subject,
            )
        )
        revision = value.revisions[-1]
        return {
            "interactionRef": str(value.interaction_ref),
            "interactionRevisionRef": str(revision.revision_ref),
            "version": value.version,
        }

    return api
