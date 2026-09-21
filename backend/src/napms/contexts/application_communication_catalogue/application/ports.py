from __future__ import annotations

from typing import Protocol
from uuid import UUID

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
    def get(self, application_ref: UUID) -> Application | None: ...
    def save(self, application: Application, *, expected_version: int) -> None: ...


class InteractionRepository(Protocol):
    def add(self, interaction: Interaction) -> None: ...
    def get(self, interaction_ref: UUID) -> Interaction | None: ...
    def save(self, interaction: Interaction, *, expected_version: int) -> None: ...


class ComponentResolver(Protocol):
    def resolve(self, component_ref: UUID) -> Component | None: ...


class InteractionRevisionResolver(Protocol):
    def resolve(self, revision_ref: UUID) -> InteractionRevision | None: ...
