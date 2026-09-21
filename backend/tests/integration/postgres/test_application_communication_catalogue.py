import os
from uuid import UUID

import psycopg
import pytest

from napms.contexts.application_communication_catalogue.domain.model import (
    Application,
    Interaction,
    PortRange,
    TrafficClause,
)
from napms.contexts.application_communication_catalogue.infrastructure.persistence.postgres.migration import (
    migrate,
)
from napms.contexts.application_communication_catalogue.infrastructure.persistence.postgres.repository import (
    PostgresApplicationCommunicationCatalogue,
)


pytestmark = pytest.mark.postgres
DSN = os.environ["NAPMS_TEST_POSTGRES_DSN"]


@pytest.fixture(autouse=True)
def fresh_schema() -> None:
    with psycopg.connect(DSN) as connection:
        connection.execute(
            "DROP SCHEMA IF EXISTS application_communication_catalogue CASCADE"
        )
        migrate(connection)


def test_application_component_and_interaction_revision_round_trip() -> None:
    repository = PostgresApplicationCommunicationCatalogue(DSN)
    application = Application.create(application_ref=UUID(int=1), name="Orders")
    repository.add(application)
    application = application.add_component(component_ref=UUID(int=2), name="API")
    application = application.add_component(component_ref=UUID(int=3), name="DB")
    repository.save_application(application, expected_version=1)

    interaction = Interaction.create(
        interaction_ref=UUID(int=10),
        source_component_ref=UUID(int=2),
        destination_component_ref=UUID(int=3),
        purpose="query orders",
    )
    repository.add(interaction)
    interaction = interaction.publish_revision(
        revision_ref=UUID(int=11),
        traffic_clauses=(
            TrafficClause(
                ip_protocol=6,
                destination_ports=(PortRange(start=5432, end=5432),),
            ),
        ),
        subject="subject:alice",
    )
    repository.save_interaction(interaction, expected_version=1)

    assert repository.get_application(application.application_ref) == application
    assert repository.resolve(UUID(int=2)) == application.components[0]
    assert repository.get_interaction(interaction.interaction_ref) == interaction
    assert repository.resolve_revision(UUID(int=11)) == interaction.revisions[0]
