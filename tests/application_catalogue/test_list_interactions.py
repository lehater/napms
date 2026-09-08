from uuid import UUID

import pytest

from napms.application_catalogue.application.list_interactions import ListDirectedInteractions
from napms.application_catalogue.domain.model import DcsRevision


def _revision(index):
    return DcsRevision(
        revision_id=UUID(int=index),
        source_component_deployment_id=UUID(int=index + 100),
        destination_component_deployment_id=UUID(int=index + 200),
        projection_payload=b'{"version":1}',
        provenance_reference=f"dcs:{index}",
    )


class FakeCatalogue:
    def __init__(self, rows):
        self.rows = tuple(rows)
        self.calls = []

    def list_dcs_revisions(self, *, offset, limit):
        self.calls.append((offset, limit))
        return self.rows[offset : offset + limit]


def test_interaction_discovery_is_bounded_and_reports_has_more():
    catalogue = FakeCatalogue((_revision(1), _revision(2), _revision(3)))
    query = ListDirectedInteractions(catalogue=catalogue)

    result = query.execute(page=1, page_size=2)

    assert tuple(item.dcs_contract_revision_id for item in result.items) == (
        UUID(int=1),
        UUID(int=2),
    )
    assert result.has_more is True
    assert catalogue.calls == [(0, 3)]


@pytest.mark.parametrize(("page", "page_size"), ((0, 50), (1, 0), (1, 101)))
def test_invalid_pagination_is_rejected(page, page_size):
    query = ListDirectedInteractions(catalogue=FakeCatalogue(()))
    with pytest.raises(ValueError):
        query.execute(page=page, page_size=page_size)
