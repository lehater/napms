from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from napms.contexts.application_communication_catalogue.domain.model import (
    Application,
    Component,
    Interaction,
)
from napms.contexts.authority_management.domain.model import Principal
from napms.platform.http.application_catalogue import router


class Catalogue:
    def __init__(
        self,
        application: Application,
        interaction: Interaction,
        components: tuple[Component, ...],
    ) -> None:
        self.application = application
        self.interaction = interaction
        self.components = {item.component_ref: item for item in components}

    def get_application_detail(
        self,
        application_ref: UUID,
    ) -> tuple[Application, tuple[Interaction, ...]]:
        assert application_ref == self.application.application_ref
        return self.application, (self.interaction,)

    def get_interaction(self, interaction_ref: UUID) -> Interaction:
        assert interaction_ref == self.interaction.interaction_ref
        return self.interaction

    def resolve_component(self, component_ref: UUID) -> Component:
        return self.components[component_ref]


def test_interaction_reads_expose_owner_resolved_component_names() -> None:
    source = Component(component_ref=UUID(int=1), name="Customer API")
    destination = Component(component_ref=UUID(int=2), name="Identity API")
    application = Application(
        application_ref=UUID(int=3),
        name="Customer Portal",
        version=1,
        components=(source,),
    )
    interaction = Interaction.create(
        interaction_ref=UUID(int=4),
        source_component_ref=source.component_ref,
        destination_component_ref=destination.component_ref,
        purpose="Authenticate customer",
    )
    catalogue = Catalogue(application, interaction, (source, destination))
    app = FastAPI()
    app.include_router(
        router(
            catalogue=catalogue,
            identity=lambda: Principal(
                "subject:alice",
                frozenset({"application.read"}),
                (),
            ),
        )
    )
    http = TestClient(app)

    application_response = http.get(f"/v1/applications/{application.application_ref}")
    interaction_response = http.get(f"/v1/interactions/{interaction.interaction_ref}")

    assert application_response.status_code == 200
    row = application_response.json()["interactions"][0]
    assert row["sourceComponentName"] == source.name
    assert row["destinationComponentName"] == destination.name
    assert interaction_response.status_code == 200
    assert interaction_response.json()["sourceComponentName"] == source.name
    assert interaction_response.json()["destinationComponentName"] == destination.name
