from __future__ import annotations

from typing import Protocol
from uuid import UUID

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from napms.contexts.application_communication_catalogue.application.ports import (
    CatalogueNotFound,
    CatalogueVersionConflict,
)
from napms.contexts.application_communication_catalogue.application.service import (
    ApplicationCommunicationCatalogue,
)
from napms.contexts.application_communication_catalogue.domain.model import (
    PortRange,
    TrafficClause,
)
from napms.contexts.authority_management.domain.model import Principal


class IdentityDependency(Protocol):
    def __call__(self) -> Principal: ...


class _Body(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)


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
