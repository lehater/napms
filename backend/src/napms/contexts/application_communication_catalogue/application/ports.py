from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from napms.contexts.application_communication_catalogue.application.queries import (
    ApplicationCataloguePage,
    ApplicationCatalogueQuery,
)
from napms.contexts.application_communication_catalogue.domain.model import (
    Application,
    Component,
    Interaction,
    InteractionRevision,
)


class CatalogueNotFound(Exception):
    pass


class CatalogueVersionConflict(Exception):
    pass


class ApplicationRepository(Protocol):
    def add(self, application: Application) -> None: ...
    def query_applications(self, query: ApplicationCatalogueQuery) -> ApplicationCataloguePage: ...
    def get_application(self, application_ref: UUID) -> Application | None: ...
    def save_application(self, application: Application, *, expected_version: int) -> None: ...


class InteractionRepository(Protocol):
    def add(self, interaction: Interaction) -> None: ...
    def get_interaction(self, interaction_ref: UUID) -> Interaction | None: ...
    def list_interactions_for_components(
        self, component_refs: tuple[UUID, ...]
    ) -> tuple[Interaction, ...]: ...
    def save_interaction(self, interaction: Interaction, *, expected_version: int) -> None: ...


class ComponentResolver(Protocol):
    def resolve(self, component_ref: UUID) -> Component | None: ...


@dataclass(frozen=True)
class ResolvedInteractionRevision:
    interaction_ref: UUID
    revision: InteractionRevision


class InteractionRevisionResolver(Protocol):
    def resolve_revision(self, revision_ref: UUID) -> ResolvedInteractionRevision | None: ...


class InteractionResolver(Protocol):
    def get_interaction(self, interaction_ref: UUID) -> Interaction | None: ...
