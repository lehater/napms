from uuid import UUID

import pytest

from napms.contexts.application_catalogue.domain.model import (
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
    retired = renamed.retired(
        retirement_provenance_reference="test:component:retirement"
    )

    assert renamed.application_id == APPLICATION_ID
    assert retired.application_id == APPLICATION_ID
    assert retired.lifecycle_state is CatalogueLifecycleState.RETIRED
    assert retired.retirement_provenance_reference == "test:component:retirement"
    assert retired.version == 3


def test_retired_catalogue_identity_is_immutable():
    retired = application().retired(
        retirement_provenance_reference="test:application:retirement"
    )

    with pytest.raises(CatalogueInvariantError, match="Retired Application"):
        retired.renamed("Another name")
    with pytest.raises(CatalogueInvariantError, match="Retired Application"):
        retired.retired(retirement_provenance_reference="test:again")


@pytest.mark.parametrize(
    "factory,state",
    [
        (application, CatalogueLifecycleState.RETIRED),
        (component, CatalogueLifecycleState.RETIRED),
    ],
)
def test_retired_catalogue_identity_requires_retirement_provenance(factory, state):
    with pytest.raises(CatalogueInvariantError, match="requires retirement provenance"):
        factory(lifecycle_state=state)


@pytest.mark.parametrize("factory", [application, component])
def test_active_catalogue_identity_rejects_retirement_provenance(factory):
    with pytest.raises(CatalogueInvariantError, match="cannot have retirement provenance"):
        factory(retirement_provenance_reference="test:invalid")


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
