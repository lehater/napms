from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from napms.application_catalogue.domain.model import (
    Application,
    CatalogueInvariantError,
    Component,
    ComponentDeployment,
    DcsRevision,
    DeploymentResourceBinding,
)


@dataclass(frozen=True, slots=True)
class DcsCatalogueSummary:
    revision_id: UUID
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    projection_payload: bytes
    display_name: str | None
    provenance_reference: str


@dataclass(frozen=True, slots=True)
class ComponentDeploymentCatalogueDetail:
    deployment: ComponentDeployment
    effective_resource_bindings: tuple[DeploymentResourceBinding, ...]
    dcs_revisions: tuple[DcsCatalogueSummary, ...]


@dataclass(frozen=True, slots=True)
class ComponentCatalogueDetail:
    component: Component
    deployments: tuple[ComponentDeploymentCatalogueDetail, ...]


@dataclass(frozen=True, slots=True)
class ApplicationCatalogueTreeDetail:
    application: Application
    components: tuple[ComponentCatalogueDetail, ...]
    as_of: datetime


class ApplicationCatalogueDetailReadPort(Protocol):
    def get_application(self, application_id: UUID) -> Application | None: ...

    def list_components(
        self,
        *,
        application_id: UUID,
        include_retired: bool,
    ) -> tuple[Component, ...]: ...

    def list_component_deployments(
        self,
        *,
        component_id: UUID,
        include_retired: bool,
    ) -> tuple[ComponentDeployment, ...]: ...

    def list_effective_bindings_for_deployments(
        self,
        *,
        deployment_ids: tuple[UUID, ...],
        as_of: datetime,
    ) -> tuple[DeploymentResourceBinding, ...]: ...

    def list_dcs_revisions_for_deployments(
        self,
        *,
        deployment_ids: tuple[UUID, ...],
    ) -> tuple[DcsRevision, ...]: ...


class ReadApplicationCatalogueTreeDetail:
    """Build the ACC-owned detail projection used by the Applications workspace."""

    def __init__(self, *, catalogue: ApplicationCatalogueDetailReadPort) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        *,
        application_id: UUID,
        as_of: datetime,
        include_retired_components: bool = False,
        include_retired_deployments: bool = False,
    ) -> ApplicationCatalogueTreeDetail | None:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise CatalogueInvariantError("as_of must be offset-aware")

        application = self._catalogue.get_application(application_id)
        if application is None:
            return None

        components = tuple(
            sorted(
                self._catalogue.list_components(
                    application_id=application_id,
                    include_retired=include_retired_components,
                ),
                key=lambda item: (
                    item.display_name.casefold(),
                    str(item.component_id),
                ),
            )
        )

        deployments_by_component: dict[UUID, tuple[ComponentDeployment, ...]] = {}
        deployment_ids: list[UUID] = []
        for component in components:
            deployments = tuple(
                sorted(
                    self._catalogue.list_component_deployments(
                        component_id=component.component_id,
                        include_retired=include_retired_deployments,
                    ),
                    key=lambda item: (
                        (item.display_name or "").casefold(),
                        str(item.deployment_id),
                    ),
                )
            )
            deployments_by_component[component.component_id] = deployments
            deployment_ids.extend(item.deployment_id for item in deployments)

        identifiers = tuple(deployment_ids)
        bindings = self._catalogue.list_effective_bindings_for_deployments(
            deployment_ids=identifiers,
            as_of=as_of,
        )
        revisions = self._catalogue.list_dcs_revisions_for_deployments(
            deployment_ids=identifiers,
        )

        bindings_by_deployment: dict[UUID, list[DeploymentResourceBinding]] = {
            deployment_id: [] for deployment_id in identifiers
        }
        for binding in bindings:
            bindings_by_deployment.setdefault(
                binding.component_deployment_id,
                [],
            ).append(binding)

        revisions_by_deployment: dict[UUID, dict[UUID, DcsCatalogueSummary]] = {
            deployment_id: {} for deployment_id in identifiers
        }
        for revision in revisions:
            summary = DcsCatalogueSummary(
                revision_id=revision.revision_id,
                source_component_deployment_id=revision.source_component_deployment_id,
                destination_component_deployment_id=revision.destination_component_deployment_id,
                projection_payload=revision.projection_payload,
                display_name=revision.display_name,
                provenance_reference=revision.provenance_reference,
            )
            for deployment_id in {
                revision.source_component_deployment_id,
                revision.destination_component_deployment_id,
            }:
                if deployment_id in revisions_by_deployment:
                    revisions_by_deployment[deployment_id][revision.revision_id] = summary

        component_details: list[ComponentCatalogueDetail] = []
        for component in components:
            deployment_details = []
            for deployment in deployments_by_component[component.component_id]:
                effective_bindings = tuple(
                    sorted(
                        bindings_by_deployment.get(deployment.deployment_id, ()),
                        key=lambda item: (
                            item.resource_reference,
                            item.reference_id,
                        ),
                    )
                )
                dcs_revisions = tuple(
                    sorted(
                        revisions_by_deployment.get(deployment.deployment_id, {}).values(),
                        key=lambda item: str(item.revision_id),
                    )
                )
                deployment_details.append(
                    ComponentDeploymentCatalogueDetail(
                        deployment=deployment,
                        effective_resource_bindings=effective_bindings,
                        dcs_revisions=dcs_revisions,
                    )
                )
            component_details.append(
                ComponentCatalogueDetail(
                    component=component,
                    deployments=tuple(deployment_details),
                )
            )

        return ApplicationCatalogueTreeDetail(
            application=application,
            components=tuple(component_details),
            as_of=as_of,
        )
