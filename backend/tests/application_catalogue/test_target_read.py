import pytest

from napms.contexts.application_catalogue.application.target_read import normalize_bounded_query
from napms.contexts.application_catalogue.domain.model import CatalogueInvariantError


def test_target_query_normalizes_search_and_stable_sort_direction() -> None:
    assert normalize_bounded_query(
        offset=50,
        limit=50,
        search=" CRM ",
        sort="-name",
    ) == (50, 50, "CRM", "-name")


def test_target_query_rejects_unbounded_page_and_unknown_sort() -> None:
    with pytest.raises(CatalogueInvariantError):
        normalize_bounded_query(offset=0, limit=1000, search=None, sort="name")

    with pytest.raises(CatalogueInvariantError):
        normalize_bounded_query(offset=0, limit=50, search=None, sort="version")
