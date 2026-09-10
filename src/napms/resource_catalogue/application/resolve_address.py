from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from napms.resource_catalogue.application.ports import ResourceCatalogueRepository
from napms.resource_catalogue.domain.model import EndpointAddress, ResourceCatalogueInvariantError


class TechnicalAddressResolutionOutcome(str, Enum):
    RESOLVED = "Resolved"
    AMBIGUOUS = "Ambiguous"
    HISTORICAL = "Historical"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class TechnicalAddressResourceMatch:
    resource_reference: str
    endpoint_reference: str
    technical_address: str
    fact_reference: str
    provenance_reference: str


@dataclass(frozen=True, slots=True)
class TechnicalAddressResolution:
    outcome: TechnicalAddressResolutionOutcome
    technical_address: str
    as_of: datetime
    matches: tuple[TechnicalAddressResourceMatch, ...] = ()


def _require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ResourceCatalogueInvariantError("as_of must be offset-aware")


class ResolveResourcesByTechnicalAddress:
    def __init__(self, *, catalogue: ResourceCatalogueRepository) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        *,
        technical_address: str,
        as_of: datetime,
    ) -> TechnicalAddressResolution:
        if not technical_address or not technical_address.strip():
            raise ResourceCatalogueInvariantError("technical_address must be non-empty")
        _require_aware(as_of)
        normalized = technical_address.strip()

        realizations = self._catalogue.find_effective_realizations_by_address(
            technical_address=normalized,
            as_of=as_of,
        )
        matches = tuple(
            sorted(
                (
                    TechnicalAddressResourceMatch(
                        resource_reference=realization.resource_reference,
                        endpoint_reference=endpoint.endpoint_reference,
                        technical_address=endpoint.technical_address,
                        fact_reference=realization.fact_reference,
                        provenance_reference=realization.provenance_reference,
                    )
                    for realization in realizations
                    for endpoint in realization.endpoint_realizations
                    if endpoint.technical_address == normalized
                ),
                key=lambda item: (
                    item.resource_reference,
                    item.endpoint_reference,
                    item.fact_reference,
                ),
            )
        )

        distinct_resources = {item.resource_reference for item in matches}
        if len(distinct_resources) == 1 and matches:
            outcome = TechnicalAddressResolutionOutcome.RESOLVED
        elif len(distinct_resources) > 1:
            outcome = TechnicalAddressResolutionOutcome.AMBIGUOUS
        elif self._catalogue.has_realization_facts_for_address(
            technical_address=normalized
        ):
            outcome = TechnicalAddressResolutionOutcome.HISTORICAL
        else:
            outcome = TechnicalAddressResolutionOutcome.UNKNOWN

        return TechnicalAddressResolution(
            outcome=outcome,
            technical_address=normalized,
            as_of=as_of,
            matches=matches,
        )
