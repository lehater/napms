from datetime import datetime, timedelta, timezone

import pytest

from napms.contexts.resource_catalogue.domain.model import (
    ResourceCatalogueInvariantError,
    ResourceScopeAffiliation,
)


AS_OF = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)


def affiliation(**overrides):
    values = {
        "affiliation_reference": "aff-1",
        "resource_reference": "resource-1",
        "responsibility_scope": "payments-prod",
        "valid_from": AS_OF - timedelta(days=1),
        "valid_to": AS_OF + timedelta(days=1),
        "provenance_reference": "prov-1",
    }
    values.update(overrides)
    return ResourceScopeAffiliation(**values)


def test_resource_scope_affiliation_is_effective_on_half_open_interval():
    item = affiliation()

    assert item.is_effective_at(AS_OF)
    assert item.is_effective_at(item.valid_from)
    assert not item.is_effective_at(item.valid_to)


def test_resource_scope_affiliation_may_be_open_ended():
    item = affiliation(valid_to=None)

    assert item.is_effective_at(AS_OF + timedelta(days=365))


@pytest.mark.parametrize(
    "field_name",
    (
        "affiliation_reference",
        "resource_reference",
        "responsibility_scope",
        "provenance_reference",
    ),
)
def test_resource_scope_affiliation_requires_non_empty_identity_fields(field_name):
    with pytest.raises(ResourceCatalogueInvariantError):
        affiliation(**{field_name: ""})


def test_resource_scope_affiliation_requires_aware_validity():
    with pytest.raises(ResourceCatalogueInvariantError):
        affiliation(valid_from=datetime(2026, 9, 9, 12, 0))


def test_resource_scope_affiliation_requires_start_before_end():
    with pytest.raises(ResourceCatalogueInvariantError):
        affiliation(valid_to=AS_OF - timedelta(days=2))
