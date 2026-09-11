from uuid import UUID

import pytest

from napms.application_catalogue.application.curation_read import (
    ListApplicationCatalogue,
    ReadApplicationCatalogueDetail,
)
from napms.application_catalogue.domain.model import (
    Application,
    CatalogueInvariantError,
    CatalogueLifecycleState,
    Component,
)


APP_1 = UUID("00000000-0000-0000-0000-000000004001")
APP_2 = UUID("00000000-0000-0000-0000-000000004002")
APP_3 = UUID("00000000-0000-0000-0000-000000004003")
COMP_A = UUID("00000000-0000-0000-0000-000000004011")
COMP_B = UUID("00000000-0000-0000-0000-000000004012")


class FakeCatalogue:
    def __init__(self):
        self.applications = (
            Application(APP_1, "Orders", "prov:orders"),
            Application(APP_2, "Payments", "prov:payments"),
            Application(
                APP_3,
                "Legacy",
                "prov:legacy",
                lifecycle_state=CatalogueLifecycleState.RETIRED,
                retirement_provenance_reference="prov:legacy:retirement",
                version=2,
            ),
        )
        self.components = (
            Component(COMP_B, APP_1, "Worker", "prov:worker"),
            Component(COMP_A, APP_1, "API", "prov:api"),
        )
        self.list_calls = []

    def list_applications(self, *, offset, limit, search, include_retired):
        self.list_calls.append(
            {
                "offset": offset,
                "limit": limit,
                "search": search,
                "include_retired": include_retired,
            }
        )
        rows = self.applications
        if not include_retired:
            rows = tuple(
                item
                for item in rows
                if item.lifecycle_state is CatalogueLifecycleState.ACTIVE
            )
        if search:
            needle = search.casefold()
            rows = tuple(item for item in rows if needle in item.display_name.casefold())
        return rows[offset : offset + limit]

    def get_application(self, application_id):
        return next(
            (item for item in self.applications if item.application_id == application_id),
            None,
        )

    def list_components(self, *, application_id, include_retired):
        rows = tuple(
            item for item in self.components if item.application_id == application_id
        )
        if not include_retired:
            rows = tuple(
                item
                for item in rows
                if item.lifecycle_state is CatalogueLifecycleState.ACTIVE
            )
        return rows


def test_list_applications_uses_limit_plus_one_and_normalizes_search():
    catalogue = FakeCatalogue()

    page = ListApplicationCatalogue(catalogue=catalogue).execute(
        page=1,
        page_size=1,
        search="  ",
    )

    assert tuple(item.application_id for item in page.items) == (APP_1,)
    assert page.has_more is True
    assert catalogue.list_calls == [
        {
            "offset": 0,
            "limit": 2,
            "search": None,
            "include_retired": False,
        }
    ]


def test_application_detail_returns_components_in_stable_display_order():
    detail = ReadApplicationCatalogueDetail(catalogue=FakeCatalogue()).execute(
        application_id=APP_1
    )

    assert detail is not None
    assert detail.application.application_id == APP_1
    assert tuple(item.component_id for item in detail.components) == (COMP_A, COMP_B)


def test_application_detail_returns_none_for_unknown_application():
    missing = UUID("00000000-0000-0000-0000-000000004099")
    assert (
        ReadApplicationCatalogueDetail(catalogue=FakeCatalogue()).execute(
            application_id=missing
        )
        is None
    )


def test_application_list_rejects_invalid_pagination():
    reader = ListApplicationCatalogue(catalogue=FakeCatalogue())
    with pytest.raises(CatalogueInvariantError):
        reader.execute(page=0)
    with pytest.raises(CatalogueInvariantError):
        reader.execute(page_size=201)
