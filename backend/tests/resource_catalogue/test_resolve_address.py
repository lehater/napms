from datetime import datetime, timezone

from napms.resource_catalogue.application.resolve_address import (
    ResolveResourcesByTechnicalAddress,
    TechnicalAddressResolutionOutcome,
)
from napms.resource_catalogue.domain.model import EndpointAddress, ResourceRealizationVersion


NOW = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)


def _realization(resource: str, endpoint: str, address: str):
    return ResourceRealizationVersion(
        fact_reference=f"fact:{resource}",
        resource_reference=resource,
        endpoint_realizations=(EndpointAddress(endpoint, address),),
        valid_from=datetime(2020, 1, 1, tzinfo=timezone.utc),
        valid_to=None,
        provenance_reference=f"prov:{resource}",
    )


class StubCatalogue:
    def __init__(self, effective=(), historical=False):
        self.effective = tuple(effective)
        self.historical = historical

    def find_effective_realizations_by_address(self, *, technical_address, as_of):
        assert as_of == NOW
        return self.effective

    def has_realization_facts_for_address(self, *, technical_address):
        return self.historical


def test_resolves_one_resource_by_address() -> None:
    result = ResolveResourcesByTechnicalAddress(
        catalogue=StubCatalogue(
            (_realization("orders", "orders:1", "10.20.20.20"),)
        )
    ).execute(technical_address="10.20.20.20", as_of=NOW)

    assert result.outcome is TechnicalAddressResolutionOutcome.RESOLVED
    assert result.matches[0].resource_reference == "orders"


def test_preserves_ambiguous_address_mapping() -> None:
    result = ResolveResourcesByTechnicalAddress(
        catalogue=StubCatalogue(
            (
                _realization("orders-a", "a", "10.20.20.20"),
                _realization("orders-b", "b", "10.20.20.20"),
            )
        )
    ).execute(technical_address="10.20.20.20", as_of=NOW)

    assert result.outcome is TechnicalAddressResolutionOutcome.AMBIGUOUS
    assert len(result.matches) == 2


def test_distinguishes_historical_from_unknown_address() -> None:
    historical = ResolveResourcesByTechnicalAddress(
        catalogue=StubCatalogue((), historical=True)
    ).execute(technical_address="10.20.20.20", as_of=NOW)
    unknown = ResolveResourcesByTechnicalAddress(
        catalogue=StubCatalogue((), historical=False)
    ).execute(technical_address="10.30.30.30", as_of=NOW)

    assert historical.outcome is TechnicalAddressResolutionOutcome.HISTORICAL
    assert unknown.outcome is TechnicalAddressResolutionOutcome.UNKNOWN
