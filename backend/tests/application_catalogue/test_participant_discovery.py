from uuid import UUID

import pytest

from napms.application_catalogue.application.participant_discovery import (
    ApplicationCatalogueParticipant,
    ListApplicationCatalogueParticipants,
)
from napms.application_catalogue.domain.model import CatalogueInvariantError


class FakeCatalogue:
    def __init__(self):
        self.calls = []
        self.rows = tuple(
            ApplicationCatalogueParticipant(
                application_id=UUID(int=index + 1),
                application_display_name=f"App {index}",
                component_id=UUID(int=index + 101),
                component_display_name=f"Component {index}",
                component_deployment_id=UUID(int=index + 201),
                deployment_display_name=f"prod-{index}",
            )
            for index in range(3)
        )

    def list_active_participants(self, *, offset, limit, search):
        self.calls.append((offset, limit, search))
        return self.rows[offset : offset + limit]


def test_participant_discovery_normalizes_search_and_uses_lookahead_paging():
    catalogue = FakeCatalogue()

    result = ListApplicationCatalogueParticipants(catalogue=catalogue).execute(
        page=1,
        page_size=2,
        search="  orders  ",
    )

    assert len(result.items) == 2
    assert result.has_more is True
    assert catalogue.calls == [(0, 3, "orders")]


def test_participant_discovery_rejects_invalid_paging():
    query = ListApplicationCatalogueParticipants(catalogue=FakeCatalogue())

    with pytest.raises(CatalogueInvariantError):
        query.execute(page=0)
    with pytest.raises(CatalogueInvariantError):
        query.execute(page_size=201)
