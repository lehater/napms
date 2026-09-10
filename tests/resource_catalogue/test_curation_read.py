from datetime import datetime, timedelta, timezone

import pytest

from napms.resource_catalogue.application.curation_read import (
    ListResourceCatalogue,
    ReadResourceCatalogueDetail,
)
from napms.resource_catalogue.domain.model import (
    EndpointAddress,
    Resource,
    ResourceCatalogueInvariantError,
    ResourceLifecycleState,
    ResourceRealizationVersion,
    ResourceScopeAffiliation,
)
from napms.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibility,
    ResourceResponsibilityRole,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


class FakeReadCatalogue:
    def __init__(self):
        self.resources = (
            Resource("res-1", "prov:1", "Orders"),
            Resource("res-2", "prov:2", "Payments"),
            Resource(
                "res-3",
                "prov:3",
                "Legacy",
                lifecycle_state=ResourceLifecycleState.RETIRED,
            ),
        )
        self.list_calls = []

    def list_resources(self, *, offset, limit, search, include_retired):
        self.list_calls.append(
            {
                "offset": offset,
                "limit": limit,
                "search": search,
                "include_retired": include_retired,
            }
        )
        rows = self.resources
        if not include_retired:
            rows = tuple(
                item
                for item in rows
                if item.lifecycle_state is ResourceLifecycleState.ACTIVE
            )
        if search:
            needle = search.casefold()
            rows = tuple(
                item
                for item in rows
                if needle in item.resource_reference.casefold()
                or (item.display_name and needle in item.display_name.casefold())
            )
        return rows[offset : offset + limit]

    def get_resource(self, resource_reference):
        return next(
            (item for item in self.resources if item.resource_reference == resource_reference),
            None,
        )

    def list_effective_realizations(self, *, resource_reference, as_of):
        return (
            ResourceRealizationVersion(
                fact_reference="future",
                resource_reference=resource_reference,
                endpoint_realizations=(EndpointAddress("ep-future", "10.0.0.2"),),
                valid_from=NOW + timedelta(days=1),
                valid_to=None,
                provenance_reference="prov:future",
            ),
            ResourceRealizationVersion(
                fact_reference="current",
                resource_reference=resource_reference,
                endpoint_realizations=(EndpointAddress("ep-current", "10.0.0.1"),),
                valid_from=NOW - timedelta(days=1),
                valid_to=None,
                provenance_reference="prov:current",
            ),
        )

    def list_effective_scope_affiliations(self, *, resource_reference, as_of):
        return (
            ResourceScopeAffiliation(
                affiliation_reference="aff-current",
                resource_reference=resource_reference,
                responsibility_scope="payments",
                valid_from=NOW - timedelta(days=1),
                valid_to=None,
                provenance_reference="prov:aff",
            ),
        )

    def list_effective_responsibilities(self, *, resource_reference, as_of):
        return (
            ResourceResponsibility(
                assignment_reference="resp-current",
                resource_reference=resource_reference,
                party_reference="team-payments",
                party_kind=ResponsiblePartyKind.TEAM,
                role=ResourceResponsibilityRole.TECHNICAL_OWNER,
                display_name="Payments team",
                contact=None,
                valid_from=NOW - timedelta(days=1),
                valid_to=None,
                provenance_reference="prov:resp",
            ),
        )


def test_list_resource_catalogue_uses_limit_plus_one_for_has_more():
    catalogue = FakeReadCatalogue()

    page = ListResourceCatalogue(catalogue=catalogue).execute(
        page=1,
        page_size=1,
        search="  ",
    )

    assert tuple(item.resource_reference for item in page.items) == ("res-1",)
    assert page.has_more is True
    assert catalogue.list_calls == [
        {
            "offset": 0,
            "limit": 2,
            "search": None,
            "include_retired": False,
        }
    ]


def test_read_resource_detail_filters_owner_rows_at_requested_time():
    detail = ReadResourceCatalogueDetail(catalogue=FakeReadCatalogue()).execute(
        resource_reference=" res-1 ",
        as_of=NOW,
    )

    assert detail is not None
    assert detail.resource.resource_reference == "res-1"
    assert tuple(item.fact_reference for item in detail.effective_realizations) == (
        "current",
    )
    assert tuple(
        item.affiliation_reference for item in detail.effective_scope_affiliations
    ) == ("aff-current",)
    assert tuple(
        item.assignment_reference for item in detail.effective_responsibilities
    ) == ("resp-current",)


def test_read_resource_detail_returns_none_for_unknown_resource():
    assert (
        ReadResourceCatalogueDetail(catalogue=FakeReadCatalogue()).execute(
            resource_reference="missing",
            as_of=NOW,
        )
        is None
    )


def test_resource_curation_read_rejects_invalid_page_and_naive_as_of():
    catalogue = FakeReadCatalogue()
    with pytest.raises(ResourceCatalogueInvariantError):
        ListResourceCatalogue(catalogue=catalogue).execute(page=0, page_size=20)
    with pytest.raises(ResourceCatalogueInvariantError):
        ReadResourceCatalogueDetail(catalogue=catalogue).execute(
            resource_reference="res-1",
            as_of=NOW.replace(tzinfo=None),
        )
