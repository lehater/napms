from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from napms.contexts.resource_catalogue.application.ports import ResourceCatalogueRepository
from napms.contexts.resource_catalogue.domain.model import (
    EndpointAddress,
    ResourceCatalogueInvariantError,
)


class ResourceResolutionOutcome(str, Enum):
    RESOLVED = "Resolved"
    MISSING = "Missing"
    STALE = "Stale"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class ResourceResolution:
    outcome: ResourceResolutionOutcome
    resource_reference: str | None = None
    as_of: datetime | None = None
    endpoint_realizations: tuple[EndpointAddress, ...] = ()
    fact_reference: str | None = None
    validity_reference: str | None = None
    provenance_reference: str | None = None


def _require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ResourceCatalogueInvariantError("as_of must be offset-aware")


class ResolveResourceRealization:
    def __init__(self, *, catalogue: ResourceCatalogueRepository) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> ResourceResolution:
        if not resource_reference:
            raise ResourceCatalogueInvariantError(
                "resource_reference must be non-empty"
            )
        _require_aware(as_of)

        matches = self._catalogue.find_effective_realizations(
            resource_reference=resource_reference,
            as_of=as_of,
        )
        if not matches:
            outcome = (
                ResourceResolutionOutcome.STALE
                if self._catalogue.has_realization_facts(
                    resource_reference=resource_reference
                )
                else ResourceResolutionOutcome.MISSING
            )
            return ResourceResolution(outcome)

        if len(matches) != 1:
            return ResourceResolution(ResourceResolutionOutcome.UNKNOWN)

        realization = matches[0]
        if (
            realization.resource_reference != resource_reference
            or not realization.is_effective_at(as_of)
        ):
            return ResourceResolution(ResourceResolutionOutcome.UNKNOWN)

        return ResourceResolution(
            ResourceResolutionOutcome.RESOLVED,
            resource_reference=resource_reference,
            as_of=as_of,
            endpoint_realizations=tuple(sorted(realization.endpoint_realizations)),
            fact_reference=realization.fact_reference,
            validity_reference=f"rc-validity:{realization.fact_reference}",
            provenance_reference=realization.provenance_reference,
        )
