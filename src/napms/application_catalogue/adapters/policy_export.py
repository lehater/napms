from napms.application_catalogue.application.resolve import (
    CatalogueResolutionOutcome,
    ResolveApplicationProjection,
)
from napms.policy_export.application.ports import (
    ApplicationProjectionFact,
    ApplicationProjectionOutcome,
    ResourceReference,
)


class PolicyExportApplicationCatalogueAdapter:
    def __init__(self, *, resolver: ResolveApplicationProjection) -> None:
        self._resolver = resolver

    def resolve_projection(self, *, subject, as_of) -> ApplicationProjectionFact:
        result = self._resolver.execute(subject=subject, as_of=as_of)
        outcome = {
            CatalogueResolutionOutcome.RESOLVED: ApplicationProjectionOutcome.RESOLVED,
            CatalogueResolutionOutcome.MISSING: ApplicationProjectionOutcome.MISSING,
            CatalogueResolutionOutcome.INVALID: ApplicationProjectionOutcome.INVALID,
            CatalogueResolutionOutcome.UNKNOWN: ApplicationProjectionOutcome.UNKNOWN,
        }[result.outcome]
        if outcome is not ApplicationProjectionOutcome.RESOLVED:
            return ApplicationProjectionFact(outcome=outcome)

        return ApplicationProjectionFact(
            outcome=outcome,
            subject=result.subject,
            as_of=result.as_of,
            source_resource_references=tuple(
                ResourceReference(value)
                for value in result.source_resource_references
            ),
            destination_resource_references=tuple(
                ResourceReference(value)
                for value in result.destination_resource_references
            ),
            dcs_projection_payload=result.projection_payload,
            fact_reference=result.fact_reference,
            validity_reference=result.validity_reference,
            provenance_reference=result.provenance_reference,
        )
