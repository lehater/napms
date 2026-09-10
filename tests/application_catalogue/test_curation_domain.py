from uuid import UUID

import pytest

from napms.application_catalogue.domain.model import (
    Application,
    CatalogueInvariantError,
    CatalogueLifecycleState,
    Component,
)


APPLICATION_ID = UUID("00000000-0000-0000-0000-000000001001")
COMPONENT_ID = UUID("00000000-0000-0000-0000-000000001002")


def application(**overrides):
    values = {
        "application_id": APPLICATION_ID,
        "display_name": "Checkout",
        "provenance_reference": "test:application",
    }
    values.update(overrides)
    return Application(**values)


def component(**overrides):
    values = {
        "component_id": COMPONENT_ID,
        "application_id": APPLICATION_ID,
        "display_name": "Web",
        "provenance_reference": "test:component",
    }
    values.update(overrides)
    return Component(**values)


def test_application_rename_preserves_identity_and_increments_version():
    current = application()

    renamed = current.renamed("  Checkout Portal  ")

    assert renamed.application_id == current.application_id
    assert renamed.display_name == "Checkout Portal"
    assert renamed.lifecycle_state is CatalogueLifecycleState.ACTIVE
    assert renamed.version == 2


def test_component_parent_identity_is_stable_across_supported_mutations():
    current = component()

    renamed = current.renamed("Frontend")
    retired = renamed.retired()

    assert renamed.application_id == APPLICATION_ID
    assert retired.application_id == APPLICATION_ID
    assert retired.lifecycle_state is CatalogueLifecycleState.RETIRED
    assert retired.version == 3


def test_retired_catalogue_identity_is_immutable():
    retired = application().retired()

    with pytest.raises(CatalogueInvariantError, match="Retired Application"):
        retired.renamed("Another name")
    with pytest.raises(CatalogueInvariantError, match="Retired Application"):
        retired.retired()


@pytest.mark.parametrize("value", ["", "   "])
def test_application_requires_non_empty_display_name(value):
    with pytest.raises(CatalogueInvariantError):
        application(display_name=value)


@pytest.mark.parametrize("value", ["", "   "])
def test_component_requires_non_empty_display_name(value):
    with pytest.raises(CatalogueInvariantError):
        component(display_name=value)


@pytest.mark.parametrize("version", [0, -1])
def test_catalogue_identity_version_must_be_positive(version):
    with pytest.raises(CatalogueInvariantError):
        application(version=version)
