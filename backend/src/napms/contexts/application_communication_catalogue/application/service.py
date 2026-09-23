from __future__ import annotations

from collections.abc import Callable
from uuid import UUID, uuid4

from napms.contexts.application_communication_catalogue.application.queries import (
    ApplicationCataloguePage,
    ApplicationCatalogueQuery,
    ComponentCataloguePage,
    ComponentCatalogueQuery,
)
from napms.contexts.application_communication_catalogue.application.ports import (
    ApplicationRepository,
    CatalogueNotFound,
    CatalogueVersionConflict,
    ComponentResolver,
    InteractionRepository,
)
from napms.contexts.application_communication_catalogue.domain.model import (
    Application,
    Component,
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

    def list_applications(self, query: ApplicationCatalogueQuery) -> ApplicationCataloguePage:
        return self._applications.query_applications(query)

    def list_components(self, query: ComponentCatalogueQuery) -> ComponentCataloguePage:
        return self._applications.query_components(query)

    def get_application_detail(
        self, application_ref: UUID
    ) -> tuple[Application, tuple[Interaction, ...]]:
        application = self._applications.get_application(application_ref)
        if application is None:
            raise CatalogueNotFound(str(application_ref))
        component_refs = tuple(item.component_ref for item in application.components)
        return application, self._interactions.list_interactions_for_components(component_refs)

    def resolve_component(self, component_ref: UUID) -> Component:
        component = self._components.resolve(component_ref)
        if component is None:
            raise CatalogueNotFound(str(component_ref))
        return component

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
        application = self._applications.get_application(application_ref)
        if application is None:
            raise CatalogueNotFound(str(application_ref))
        if application.version != expected_version:
            raise CatalogueVersionConflict(str(application_ref))
        updated = application.add_component(component_ref=self._new_ref(), name=name)
        self._applications.save_application(updated, expected_version=expected_version)
        return updated

    def get_interaction(self, interaction_ref: UUID) -> Interaction:
        interaction = self._interactions.get_interaction(interaction_ref)
        if interaction is None:
            raise CatalogueNotFound(str(interaction_ref))
        return interaction

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
        if not traffic_clauses:
            raise ValueError("interaction revision requires traffic clauses")
        interaction = self._interactions.get_interaction(interaction_ref)
        if interaction is None:
            raise CatalogueNotFound(str(interaction_ref))
        if interaction.version != expected_version:
            raise CatalogueVersionConflict(str(interaction_ref))
        updated = interaction.publish_revision(
            revision_ref=self._new_ref(),
            traffic_clauses=traffic_clauses,
            subject=subject,
        )
        self._interactions.save_interaction(updated, expected_version=expected_version)
        return updated
