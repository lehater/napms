from datetime import datetime, timedelta, timezone

import pytest

from napms.contexts.resource_catalogue.application.list_scope_resources import (
    ListResourcesInResponsibilityScope,
)
from napms.contexts.resource_catalogue.domain.model import (
    ResourceCatalogueInvariantError,
    ResourceScopeAffiliation,
)


AS_OF = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)


def affiliation(reference, resource, *, scope="scope-a"):
    return ResourceScopeAffiliation(
        affiliation_reference=reference,
        resource_reference=resource,
        responsibility_scope=scope,
        valid_from=AS_OF - timedelta(days=1),
        valid_to=None,
        provenance_reference=f"prov:{reference}",
    )


class FakeAffiliations:
    def __init__(self, rows):
        self.rows = tuple(rows)
        self.calls = []

    def list_effective_for_scope(
        self,
        *,
        responsibility_scope,
        as_of,
        offset,
        limit,
        search=None,
    ):
        self.calls.append(
            (responsibility_scope, as_of, offset, limit, search)
        )
        return self.rows[offset : offset + limit]


def test_lists_effective_resource_references_with_resource_paging():
    repo = FakeAffiliations(
        (
            affiliation("a1", "r1"),
            affiliation("a2", "r2"),
            affiliation("a3", "r3"),
        )
    )
    result = ListResourcesInResponsibilityScope(
        affiliations=repo
    ).execute(
        responsibility_scope="scope-a",
        as_of=AS_OF,
        page=1,
        page_size=2,
    )

    assert result.resource_references == ("r1", "r2")
    assert result.has_more is True
    assert repo.calls == [("scope-a", AS_OF, 0, 3, None)]


def test_search_is_normalized_before_repository_call():
    repo = FakeAffiliations((affiliation("a1", "r1"),))
    ListResourcesInResponsibilityScope(
        affiliations=repo
    ).execute(
        responsibility_scope="scope-a",
        as_of=AS_OF,
        search="  r1  ",
    )

    assert repo.calls[0][-1] == "r1"


def test_overlapping_effective_affiliations_for_same_resource_fail_closed():
    repo = FakeAffiliations(
        (
            affiliation("a1", "r1"),
            affiliation("a2", "r1"),
        )
    )

    with pytest.raises(ResourceCatalogueInvariantError):
        ListResourcesInResponsibilityScope(
            affiliations=repo
        ).execute(
            responsibility_scope="scope-a",
            as_of=AS_OF,
        )


def test_naive_as_of_is_rejected():
    with pytest.raises(ResourceCatalogueInvariantError):
        ListResourcesInResponsibilityScope(
            affiliations=FakeAffiliations(())
        ).execute(
            responsibility_scope="scope-a",
            as_of=datetime(2026, 9, 9, 12, 0),
        )
