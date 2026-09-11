from datetime import datetime, timezone

import pytest

from napms.contexts.resource_catalogue.application.curation_read import (
    ListResourceCatalogue,
    ResourceCatalogueListItem,
    ResourceCatalogueWorkspaceCounts,
)
from napms.contexts.resource_catalogue.domain.model import (
    Resource,
    ResourceCatalogueInvariantError,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


class FakeWorkspaceCatalogue:
    def __init__(self):
        self.calls = []
        self.summary_calls = []
        self.rows = (
            ResourceCatalogueListItem(
                resource=Resource("res-1", "prov:1", "Orders"),
                has_effective_realization=True,
                has_effective_scope_affiliation=True,
                has_effective_responsibility=True,
                has_effective_contact=False,
            ),
            ResourceCatalogueListItem(
                resource=Resource("res-2", "prov:2", "Payments"),
                has_effective_realization=False,
                has_effective_scope_affiliation=False,
                has_effective_responsibility=False,
                has_effective_contact=False,
            ),
        )

    def summarize_workspace_resources(self, **kwargs):
        self.summary_calls.append(kwargs)
        return ResourceCatalogueWorkspaceCounts(
            total=2,
            all=7,
            active=5,
            retired=2,
            missing_address=3,
            missing_scope=2,
            missing_responsibility=1,
        )

    def list_workspace_resources(
        self,
        *,
        offset,
        limit,
        search,
        lifecycle,
        responsibility_scope,
        data_state,
        sort_by,
        sort_direction,
        as_of,
    ):
        self.calls.append(
            {
                "offset": offset,
                "limit": limit,
                "search": search,
                "lifecycle": lifecycle,
                "responsibility_scope": responsibility_scope,
                "data_state": data_state,
                "sort_by": sort_by,
                "sort_direction": sort_direction,
                "as_of": as_of,
            }
        )
        return self.rows[offset : offset + limit]


def test_workspace_list_normalizes_inputs_and_preserves_reference_metadata():
    catalogue = FakeWorkspaceCatalogue()

    page = ListResourceCatalogue(catalogue=catalogue).execute_workspace(
        page=1,
        page_size=1,
        search="  Orders  ",
        responsibility_scope="  payments-team  ",
        lifecycle="all",
        sort_by="reference",
        sort_direction="desc",
        as_of=NOW,
    )

    assert tuple(item.resource.resource_reference for item in page.items) == ("res-1",)
    assert page.has_more is True
    assert page.total == 2
    assert page.counts.all == 7
    assert page.counts.active == 5
    assert page.counts.retired == 2
    assert page.counts.missing_address == 3
    assert page.counts.missing_scope == 2
    assert page.counts.missing_responsibility == 1
    assert page.as_of == NOW
    assert page.responsibility_scope == "payments-team"
    assert page.data_state is None
    assert page.lifecycle == "all"
    assert page.sort_by == "reference"
    assert page.sort_direction == "desc"
    assert page.items[0].has_effective_realization is True
    assert page.items[0].has_effective_scope_affiliation is True
    assert page.items[0].has_effective_responsibility is True
    assert page.items[0].has_effective_contact is False
    assert catalogue.calls == [
        {
            "offset": 0,
            "limit": 1,
            "search": "Orders",
            "lifecycle": "all",
            "responsibility_scope": "payments-team",
            "data_state": None,
            "sort_by": "reference",
            "sort_direction": "desc",
            "as_of": NOW,
        }
    ]
    assert catalogue.summary_calls == [
        {
            "search": "Orders",
            "lifecycle": "all",
            "responsibility_scope": "payments-team",
            "data_state": None,
            "as_of": NOW,
        }
    ]


def test_workspace_list_treats_blank_scope_search_and_data_state_as_absent():
    catalogue = FakeWorkspaceCatalogue()

    page = ListResourceCatalogue(catalogue=catalogue).execute_workspace(
        page=1,
        page_size=50,
        search="   ",
        responsibility_scope="   ",
        data_state="   ",
        as_of=NOW,
    )

    assert page.responsibility_scope is None
    assert page.data_state is None
    assert page.lifecycle == "active"
    assert page.sort_by == "name"
    assert page.sort_direction == "asc"
    assert catalogue.calls[0]["search"] is None
    assert catalogue.calls[0]["responsibility_scope"] is None
    assert catalogue.calls[0]["data_state"] is None


def test_workspace_list_normalizes_and_forwards_supported_data_state():
    catalogue = FakeWorkspaceCatalogue()

    page = ListResourceCatalogue(catalogue=catalogue).execute_workspace(
        page=1,
        page_size=50,
        data_state=" missing-address ",
        as_of=NOW,
    )

    assert page.data_state == "missing-address"
    assert catalogue.calls[0]["data_state"] == "missing-address"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("data_state", "missing-contact"),
        ("lifecycle", "deleted"),
        ("sort_by", "owner"),
        ("sort_direction", "sideways"),
    ],
)
def test_workspace_list_rejects_unsupported_controls(field, value):
    catalogue = FakeWorkspaceCatalogue()
    kwargs = {
        "page": 1,
        "page_size": 50,
        "as_of": NOW,
        field: value,
    }

    with pytest.raises(ResourceCatalogueInvariantError):
        ListResourceCatalogue(catalogue=catalogue).execute_workspace(**kwargs)

    assert catalogue.calls == []
    assert catalogue.summary_calls == []


def test_workspace_list_rejects_naive_as_of_before_calling_repository():
    catalogue = FakeWorkspaceCatalogue()

    with pytest.raises(ResourceCatalogueInvariantError):
        ListResourceCatalogue(catalogue=catalogue).execute_workspace(
            page=1,
            page_size=50,
            as_of=NOW.replace(tzinfo=None),
        )

    assert catalogue.calls == []
    assert catalogue.summary_calls == []
