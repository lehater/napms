import pytest

from napms.resource_catalogue.domain.model import (
    Resource,
    ResourceCatalogueInvariantError,
    ResourceLifecycleState,
)


def resource(**overrides):
    values = {
        "resource_reference": "res-1",
        "provenance_reference": "test:resource",
        "display_name": "Orders production",
    }
    values.update(overrides)
    return Resource(**values)


def test_resource_rename_preserves_identity_and_increments_version():
    current = resource()

    renamed = current.renamed("  Orders API production  ")

    assert renamed.resource_reference == current.resource_reference
    assert renamed.display_name == "Orders API production"
    assert renamed.lifecycle_state is ResourceLifecycleState.ACTIVE
    assert renamed.version == 2


def test_resource_retirement_preserves_identity_and_records_transition_provenance():
    retired = resource().retired(
        retirement_provenance_reference="test:resource:retirement"
    )

    assert retired.resource_reference == "res-1"
    assert retired.lifecycle_state is ResourceLifecycleState.RETIRED
    assert retired.retirement_provenance_reference == "test:resource:retirement"
    assert retired.version == 2

    with pytest.raises(ResourceCatalogueInvariantError, match="Retired Resource"):
        retired.renamed("Another")
    with pytest.raises(ResourceCatalogueInvariantError, match="Retired Resource"):
        retired.retired(retirement_provenance_reference="test:again")


def test_retired_resource_requires_retirement_provenance():
    with pytest.raises(ResourceCatalogueInvariantError, match="requires retirement provenance"):
        resource(lifecycle_state=ResourceLifecycleState.RETIRED)


def test_active_resource_rejects_retirement_provenance():
    with pytest.raises(ResourceCatalogueInvariantError, match="Active Resource"):
        resource(retirement_provenance_reference="test:invalid")


def test_resource_may_exist_without_display_name():
    value = resource(display_name=None)

    assert value.display_name is None


@pytest.mark.parametrize("value", ["", "   "])
def test_resource_reference_must_be_non_empty(value):
    with pytest.raises(ResourceCatalogueInvariantError):
        resource(resource_reference=value)


@pytest.mark.parametrize("version", [0, -1])
def test_resource_version_must_be_positive(version):
    with pytest.raises(ResourceCatalogueInvariantError):
        resource(version=version)
