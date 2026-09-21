from __future__ import annotations

from collections.abc import Callable
from uuid import UUID, uuid4

from napms.contexts.application_communication_catalogue.application.ports import (
    ApplicationRepository,
    CatalogueNotFound,
    CatalogueVersionConflict,
    ComponentResolver,
    InteractionRepository,
)
from napms.contexts.application_communication_catalogue.domain.model import (
    Application,
    Interaction,
    TrafficClause,
)


class ApplicationCommunicationCatalogue:
    def __init__(
        self,
        *,
        applications: ApplicationRepository,
        interactions: InteractionRepository,
        components: ComponentResolver,
        new_ref: Callable[[], UUID] = uuid4,
    ) -> None:
        self._applications = applications
        self._interactions = interactions
        self._components = components
        self._new_ref = new_ref

    def create_application(self, *, name: str) -> Application:
        value = Application.create(application_ref=self._new_ref(), name=name)
        self._applications.add(value)
        return value

    def add_component(
        self,
        *,
        application_ref: UUID,
        name: str,
        expected_version: int,
    ) -> Application:
        application = self._applications.get(application_ref)
        if application is None:
            raise CatalogueNotFound(str(application_ref))
        if application.version != expected_version:
            raise CatalogueVersionConflict(str(application_ref))
        updated = application.add_component(component_ref=self._new_ref(), name=name)
        self._applications.save(updated, expected_version=expected_version)
        return updated

    def create_interaction(
        self,
        *,
        source_component_ref: UUID,
        destination_component_ref: UUID,
        purpose: str | None,
    ) -> Interaction:
        if self._components.resolve(source_component_ref) is None:
            raise CatalogueNotFound(str(source_component_ref))
        if self._components.resolve(destination_component_ref) is None:
            raise CatalogueNotFound(str(destination_component_ref))
        value = Interaction.create(
            interaction_ref=self._new_ref(),
            source_component_ref=source_component_ref,
            destination_component_ref=destination_component_ref,
            purpose=purpose,
        )
        self._interactions.add(value)
        return value

    def publish_interaction_revision(
        self,
        *,
        interaction_ref: UUID,
        traffic_clauses: tuple[TrafficClause, ...],
        expected_version: int,
        subject: str,
    ) -> Interaction:
        interaction = self._interactions.get(interaction_ref)
        if interaction is None:
            raise CatalogueNotFound(str(interaction_ref))
        if interaction.version != expected_version:
            raise CatalogueVersionConflict(str(interaction_ref))
        updated = interaction.publish_revision(
            revision_ref=self._new_ref(),
            traffic_clauses=traffic_clauses,
            subject=subject,
        )
        self._interactions.save(updated, expected_version=expected_version)
        return updated
