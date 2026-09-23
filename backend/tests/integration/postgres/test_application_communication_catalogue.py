import os
from uuid import UUID

import psycopg
import pytest

from napms.contexts.application_communication_catalogue.application.queries import (
    ApplicationCatalogueQuery,
    ApplicationSortField,
    ComponentCatalogueQuery,
    SortDirection,
)
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
        connection.execute("DROP SCHEMA IF EXISTS application_communication_catalogue CASCADE")
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
    assert repository.list_interactions_for_components((UUID(int=2),)) == (interaction,)
    assert repository.list_interactions_for_components((UUID(int=99),)) == ()
    resolved_revision = repository.resolve_revision(UUID(int=11))
    assert resolved_revision is not None
    assert resolved_revision.interaction_ref == interaction.interaction_ref
    assert resolved_revision.revision == interaction.revisions[0]


def test_application_catalogue_query_applies_search_filter_sort_and_paging() -> None:
    repository = PostgresApplicationCommunicationCatalogue(DSN)

    zulu = Application.create(application_ref=UUID(int=101), name="Zulu app")
    alpha = Application.create(application_ref=UUID(int=102), name="Alpha app")
    other = Application.create(application_ref=UUID(int=103), name="Other")
    for value in (zulu, alpha, other):
        repository.add(value)

    zulu = zulu.add_component(component_ref=UUID(int=201), name="Gateway")
    alpha = alpha.add_component(component_ref=UUID(int=202), name="API")
    repository.save_application(zulu, expected_version=1)
    repository.save_application(alpha, expected_version=1)

    first = repository.query_applications(
        ApplicationCatalogueQuery(
            search="app",
            sort_by=ApplicationSortField.NAME,
            sort_direction=SortDirection.ASC,
            page=1,
            page_size=1,
        )
    )
    assert first.total == 2
    assert [item.name for item in first.items] == ["Alpha app"]

    second = repository.query_applications(
        ApplicationCatalogueQuery(
            search="app",
            sort_by=ApplicationSortField.NAME,
            sort_direction=SortDirection.ASC,
            page=2,
            page_size=1,
        )
    )
    assert [item.name for item in second.items] == ["Zulu app"]

    filtered = repository.query_applications(ApplicationCatalogueQuery(component_ref=UUID(int=201)))
    assert filtered.total == 1
    assert [item.application_ref for item in filtered.items] == [UUID(int=101)]


def test_component_catalogue_query_searches_component_and_application_context() -> None:
    repository = PostgresApplicationCommunicationCatalogue(DSN)
    payments = Application.create(application_ref=UUID(int=301), name="Payments")
    identity = Application.create(application_ref=UUID(int=302), name="Identity")
    repository.add(payments)
    repository.add(identity)
    payments = payments.add_component(component_ref=UUID(int=401), name="API")
    identity = identity.add_component(component_ref=UUID(int=402), name="API")
    repository.save_application(payments, expected_version=1)
    repository.save_application(identity, expected_version=1)

    page = repository.query_components(
        ComponentCatalogueQuery(search="payments", page=1, page_size=10)
    )

    assert page.total == 1
    assert page.items[0].component_ref == UUID(int=401)
    assert page.items[0].name == "API"
    assert page.items[0].application_name == "Payments"
