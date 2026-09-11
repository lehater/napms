from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.contexts.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
)
from napms.contexts.application_catalogue.domain.model import (
    Application,
    Component,
    ComponentDeployment,
    DcsRevision,
    DeploymentResourceBinding,
)


APPLICATION_CATALOGUE_CURATION_ACTION = "CurateApplicationCatalogue"
APPLICATION_CATALOGUE_AUTHORITY_SCOPE = "application-catalogue"


class CataloguePersistenceError(Exception):
    """Catalogue persistence failed without a trustworthy semantic result."""


class CataloguePersistenceOutcomeUnknown(CataloguePersistenceError):
    """Commit acknowledgement failed, so authoritative outcome is uncertain."""


class CatalogueConcurrencyConflict(CataloguePersistenceError):
    """Optimistic concurrency precondition did not match authoritative state."""


# Compatibility name used by the first I27 structural curation slice.
ApplicationCatalogueConcurrencyConflict = CatalogueConcurrencyConflict


class CatalogueIdempotencyConflict(CataloguePersistenceError):
    """Another command won the same idempotency-key uniqueness boundary."""


class ApplicationCatalogueAuthorityOutcome(str, Enum):
    PERMITTED = "Permitted"
    DENIED = "Denied"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class ApplicationCatalogueAuthorityCheck:
    outcome: ApplicationCatalogueAuthorityOutcome
    authority_reference: str | None = None


class ApplicationCatalogueCurationAuthorityPort(Protocol):
    def check_curation(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> ApplicationCatalogueAuthorityCheck: ...


@dataclass(frozen=True, slots=True)
class ApplicationCatalogueCommandReceipt:
    command_kind: str
    request_fingerprint: str
    result_id: UUID | str
    result_version: int


class ApplicationCatalogueIdentityFactory(Protocol):
    def new_application_id(self) -> UUID: ...

    def new_component_id(self) -> UUID: ...

    def new_component_deployment_id(self) -> UUID: ...

    def new_dcs_revision_id(self) -> UUID: ...


class ApplicationCatalogueProvenanceFactory(Protocol):
    def for_application(
        self,
        *,
        application_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_application_retirement(
        self,
        *,
        application_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_component(
        self,
        *,
        component_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_component_retirement(
        self,
        *,
        component_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_component_deployment(
        self,
        *,
        deployment_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_component_deployment_retirement(
        self,
        *,
        deployment_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_dcs_revision(
        self,
        *,
        revision_id: UUID,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...


class DcsProjectionAuthoringEncoder(Protocol):
    def encode(
        self,
        alternatives: tuple[AuthoredDcsTrafficAlternative, ...],
    ) -> bytes: ...


class ApplicationCatalogueCurationRepository(Protocol):
    def get_application(self, application_id: UUID) -> Application | None: ...

    def add_application(self, application: Application) -> None: ...

    def save_application(
        self,
        application: Application,
        *,
        expected_version: int,
    ) -> None: ...

    def has_active_components(self, *, application_id: UUID) -> bool: ...

    def get_component(self, component_id: UUID) -> Component | None: ...

    def add_component(self, component: Component) -> None: ...

    def save_component(
        self,
        component: Component,
        *,
        expected_version: int,
    ) -> None: ...

    def has_active_component_deployments(self, *, component_id: UUID) -> bool: ...

    def get_component_deployment(
        self,
        deployment_id: UUID,
    ) -> ComponentDeployment | None: ...

    def add_component_deployment(self, deployment: ComponentDeployment) -> None: ...

    def save_component_deployment(
        self,
        deployment: ComponentDeployment,
        *,
        expected_version: int,
    ) -> None: ...

    def get_dcs_revision(self, revision_id: UUID) -> DcsRevision | None: ...

    def add_dcs_revision(self, revision: DcsRevision) -> None: ...

    def find_command_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
    ) -> ApplicationCatalogueCommandReceipt | None: ...

    def record_command_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        receipt: ApplicationCatalogueCommandReceipt,
    ) -> None: ...

    def commit(self) -> None: ...


class ApplicationCatalogueCurationReadRepository(Protocol):
    def list_applications(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
        include_retired: bool,
    ) -> tuple[Application, ...]: ...

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


class ApplicationCatalogueRepository(Protocol):
    def get_dcs_revision(self, revision_id: UUID) -> DcsRevision | None: ...

    def get_dcs_revisions(
        self,
        revision_ids: tuple[UUID, ...],
    ) -> tuple[DcsRevision, ...]: ...

    def get_component_deployments(
        self,
        deployment_ids: tuple[UUID, ...],
    ) -> tuple[ComponentDeployment, ...]: ...

    def list_dcs_revisions(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> tuple[DcsRevision, ...]: ...

    def find_effective_bindings(
        self,
        *,
        component_deployment_id: UUID,
        as_of: datetime,
    ) -> tuple[DeploymentResourceBinding, ...]: ...

    def find_effective_bindings_for_resources(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
        limit: int | None = None,
    ) -> tuple[DeploymentResourceBinding, ...]: ...

    def find_effective_bindings_for_components(
        self,
        *,
        component_deployment_ids: tuple[UUID, ...],
        as_of: datetime,
        limit: int | None = None,
    ) -> tuple[DeploymentResourceBinding, ...]: ...

    def list_dcs_revisions_for_components(
        self,
        *,
        component_deployment_ids: tuple[UUID, ...],
        limit: int | None = None,
    ) -> tuple[DcsRevision, ...]: ...
