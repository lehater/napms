from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from napms.application_catalogue.application.ports import (
    ApplicationCatalogueCurationRepository,
    ApplicationCatalogueIdentityFactory,
    ApplicationCatalogueProvenanceFactory,
    ApplicationCatalogueRepository,
)
from napms.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.application_catalogue.domain.target_model import (
    ApplicationDeployment,
    DeploymentInteraction,
    DeploymentInteractionCompatibility,
    DeploymentInteractionSide,
    InteractionDefinition,
)


@dataclass(frozen=True, slots=True)
class ActiveDependencyReference:
    reference: str
    display_name: str | None = None


class ConnectivityRequirementDependencyPort(Protocol):
    def find_active_references(
        self,
        *,
        subject: DirectedInteractionIdentity,
        as_of: datetime,
    ) -> tuple[ActiveDependencyReference, ...]: ...


class ConnectivityDecisionDependencyPort(Protocol):
    def find_active_references(
        self,
        *,
        subject: DirectedInteractionIdentity,
        as_of: datetime,
    ) -> tuple[ActiveDependencyReference, ...]: ...


class AccessRuleDependencyPort(Protocol):
    def find_active_references(
        self,
        *,
        subject: DirectedInteractionIdentity,
        as_of: datetime,
    ) -> tuple[ActiveDependencyReference, ...]: ...


class TargetApplicationCatalogueIdentityFactory(ApplicationCatalogueIdentityFactory, Protocol):
    def new_interaction_definition_id(self) -> UUID: ...

    def new_application_deployment_id(self) -> UUID: ...

    def new_deployment_interaction_id(self) -> UUID: ...


class TargetApplicationCatalogueProvenanceFactory(
    ApplicationCatalogueProvenanceFactory,
    Protocol,
):
    def for_interaction_definition(
        self,
        *,
        interaction_definition_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_interaction_definition_retirement(
        self,
        *,
        interaction_definition_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_application_deployment(
        self,
        *,
        application_deployment_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_application_deployment_retirement(
        self,
        *,
        application_deployment_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_deployment_interaction(
        self,
        *,
        deployment_interaction_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_deployment_interaction_retirement(
        self,
        *,
        deployment_interaction_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_compatibility_component_deployment(
        self,
        *,
        component_deployment_id: UUID,
        deployment_interaction_id: UUID,
        side: DeploymentInteractionSide,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...


class TargetApplicationCatalogueRepository(
    ApplicationCatalogueCurationRepository,
    ApplicationCatalogueRepository,
    Protocol,
):
    def get_interaction_definition(
        self,
        interaction_definition_id: UUID,
    ) -> InteractionDefinition | None: ...

    def add_interaction_definition(self, value: InteractionDefinition) -> None: ...

    def save_interaction_definition(
        self,
        value: InteractionDefinition,
        *,
        expected_version: int,
    ) -> None: ...

    def list_active_deployment_interactions_for_definition(
        self,
        *,
        interaction_definition_id: UUID,
    ) -> tuple[DeploymentInteraction, ...]: ...

    def get_application_deployment(
        self,
        application_deployment_id: UUID,
    ) -> ApplicationDeployment | None: ...

    def add_application_deployment(self, value: ApplicationDeployment) -> None: ...

    def save_application_deployment(
        self,
        value: ApplicationDeployment,
        *,
        expected_version: int,
    ) -> None: ...

    def get_deployment_interaction(
        self,
        deployment_interaction_id: UUID,
    ) -> DeploymentInteraction | None: ...

    def find_active_deployment_interaction(
        self,
        *,
        application_deployment_id: UUID,
        interaction_definition_id: UUID,
    ) -> DeploymentInteraction | None: ...

    def add_deployment_interaction(self, value: DeploymentInteraction) -> None: ...

    def save_deployment_interaction(
        self,
        value: DeploymentInteraction,
        *,
        expected_version: int,
    ) -> None: ...

    def get_compatibility_projection(
        self,
        deployment_interaction_id: UUID,
    ) -> DeploymentInteractionCompatibility | None: ...

    def add_compatibility_projection(
        self,
        value: DeploymentInteractionCompatibility,
    ) -> None: ...

    def save_compatibility_projection(
        self,
        value: DeploymentInteractionCompatibility,
        *,
        expected_version: int,
    ) -> None: ...
