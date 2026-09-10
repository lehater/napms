from datetime import datetime, timezone

import pytest

from napms.resource_catalogue.domain.model import (
    EndpointAddress,
    ResourceCatalogueInvariantError,
    ResourceRealizationVersion,
    ResourceScopeAffiliation,
)
from napms.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibility,
    ResourceResponsibilityRole,
)


START = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)
END = datetime(2026, 9, 11, 8, 0, tzinfo=timezone.utc)


def realization():
    return ResourceRealizationVersion(
        fact_reference="realization-1",
        resource_reference="res-1",
        endpoint_realizations=(EndpointAddress("ep-1", "10.0.0.10"),),
        valid_from=START,
        valid_to=None,
        provenance_reference="prov:realization",
    )


def affiliation():
    return ResourceScopeAffiliation(
        affiliation_reference="aff-1",
        resource_reference="res-1",
        responsibility_scope="payments",
        valid_from=START,
        valid_to=None,
        provenance_reference="prov:affiliation",
    )


def responsibility():
    return ResourceResponsibility(
        assignment_reference="resp-1",
        resource_reference="res-1",
        party_reference="team-payments",
        party_kind=ResponsiblePartyKind.TEAM,
        role=ResourceResponsibilityRole.TECHNICAL_OWNER,
        display_name="Payments platform",
        contact="payments@example.invalid",
        valid_from=START,
        valid_to=None,
        provenance_reference="prov:responsibility",
    )


@pytest.mark.parametrize("factory", [realization, affiliation, responsibility])
def test_temporal_fact_end_is_explicit_and_increments_version(factory):
    current = factory()

    ended = current.ended(valid_to=END)

    assert ended.valid_to == END
    assert ended.version == 2
    assert current.valid_to is None
    assert current.version == 1


@pytest.mark.parametrize("factory", [realization, affiliation, responsibility])
def test_temporal_fact_cannot_be_ended_twice(factory):
    ended = factory().ended(valid_to=END)

    with pytest.raises(ResourceCatalogueInvariantError, match="already ended"):
        ended.ended(valid_to=END)


@pytest.mark.parametrize("factory", [realization, affiliation, responsibility])
def test_temporal_fact_end_must_be_after_start(factory):
    with pytest.raises(ResourceCatalogueInvariantError):
        factory().ended(valid_to=START)


@pytest.mark.parametrize("factory", [realization, affiliation, responsibility])
def test_temporal_fact_version_must_be_positive(factory):
    current = factory()
    values = {
        field: getattr(current, field)
        for field in current.__dataclass_fields__
    }
    values["version"] = 0

    with pytest.raises(ResourceCatalogueInvariantError):
        type(current)(**values)
