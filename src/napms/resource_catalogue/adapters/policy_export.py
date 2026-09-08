from napms.policy_export.application.ports import (
    EndpointRealization,
    ResourceRealizationFact,
    ResourceRealizationOutcome,
)
from napms.resource_catalogue.application.resolve import (
    ResolveResourceRealization,
    ResourceResolutionOutcome,
)


class PolicyExportResourceCatalogueAdapter:
    def __init__(self, *, resolver: ResolveResourceRealization) -> None:
        self._resolver = resolver

    def resolve_realization(
        self,
        *,
        resource_reference,
        as_of,
    ) -> ResourceRealizationFact:
        result = self._resolver.execute(
            resource_reference=resource_reference.value,
            as_of=as_of,
        )
        outcome = {
            ResourceResolutionOutcome.RESOLVED: ResourceRealizationOutcome.RESOLVED,
            ResourceResolutionOutcome.MISSING: ResourceRealizationOutcome.MISSING,
            ResourceResolutionOutcome.STALE: ResourceRealizationOutcome.STALE,
            ResourceResolutionOutcome.UNKNOWN: ResourceRealizationOutcome.UNKNOWN,
        }[result.outcome]
        if outcome is not ResourceRealizationOutcome.RESOLVED:
            return ResourceRealizationFact(outcome=outcome)

        return ResourceRealizationFact(
            outcome=outcome,
            resource_reference=resource_reference,
            as_of=result.as_of,
            endpoint_realizations=tuple(
                EndpointRealization(
                    endpoint_reference=value.endpoint_reference,
                    technical_address=value.technical_address,
                )
                for value in result.endpoint_realizations
            ),
            fact_reference=result.fact_reference,
            validity_reference=result.validity_reference,
            provenance_reference=result.provenance_reference,
        )
