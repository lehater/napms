from uuid import UUID

import pytest

from napms.contexts.application_communication_catalogue.application.service import (
    ApplicationCommunicationCatalogue,
)
from napms.contexts.application_communication_catalogue.domain.model import (
    Application,
    Component,
    Interaction,
    TrafficClause,
)


class Applications:
    def __init__(self) -> None:
        self.values: dict[UUID, Application] = {}

    def add(self, application: Application) -> None:
        self.values[application.application_ref] = application

    def get(self, application_ref: UUID) -> Application | None:
        return self.values.get(application_ref)

    def save(self, application: Application, *, expected_version: int) -> None:
        assert self.values[application.application_ref].version == expected_version
        self.values[application.application_ref] = application


class Interactions:
    def __init__(self) -> None:
        self.values: dict[UUID, Interaction] = {}

    def add(self, interaction: Interaction) -> None:
        self.values[interaction.interaction_ref] = interaction

    def get_interaction(self, interaction_ref: UUID) -> Interaction | None:
        return self.values.get(interaction_ref)

    def save_interaction(self, interaction: Interaction, *, expected_version: int) -> None:
        assert self.values[interaction.interaction_ref].version == expected_version
        self.values[interaction.interaction_ref] = interaction


class Components:
    def __init__(self, *values: Component) -> None:
        self.values = {item.component_ref: item for item in values}

    def resolve(self, component_ref: UUID) -> Component | None:
        return self.values.get(component_ref)


class Refs:
    def __init__(self, *values: UUID) -> None:
        self.values = iter(values)

    def __call__(self) -> UUID:
        return next(self.values)


def test_interaction_may_cross_application_boundary() -> None:
    source = Component(component_ref=UUID(int=1), name="source")
    destination = Component(component_ref=UUID(int=2), name="destination")
    interactions = Interactions()
    service = ApplicationCommunicationCatalogue(
        applications=Applications(),
        interactions=interactions,
        components=Components(source, destination),
        new_ref=Refs(UUID(int=10)),
    )

    value = service.create_interaction(
        source_component_ref=source.component_ref,
        destination_component_ref=destination.component_ref,
        purpose="cross-app communication",
    )

    assert value.source_component_ref == source.component_ref
    assert value.destination_component_ref == destination.component_ref


def test_revision_requires_non_empty_traffic_semantics() -> None:
    interaction = Interaction.create(
        interaction_ref=UUID(int=20),
        source_component_ref=UUID(int=1),
        destination_component_ref=UUID(int=2),
        purpose="status",
    )
    interactions = Interactions()
    interactions.add(interaction)
    service = ApplicationCommunicationCatalogue(
        applications=Applications(),
        interactions=interactions,
        components=Components(),
        new_ref=Refs(UUID(int=21)),
    )

    with pytest.raises(ValueError):
        service.publish_interaction_revision(
            interaction_ref=interaction.interaction_ref,
            traffic_clauses=(),
            expected_version=interaction.version,
            subject="subject:alice",
        )

    updated = service.publish_interaction_revision(
        interaction_ref=interaction.interaction_ref,
        traffic_clauses=(TrafficClause(ip_protocol=1),),
        expected_version=interaction.version,
        subject="subject:alice",
    )
    assert updated.revisions[0].revision_ref == UUID(int=21)
