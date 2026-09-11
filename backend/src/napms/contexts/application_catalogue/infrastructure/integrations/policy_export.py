from napms.contexts.application_catalogue.application.resolve import (
    CatalogueResolutionOutcome,
    ResolveApplicationProjection,
)
from napms.contexts.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.workflows.policy_export.application.ports import (
    ApplicationProjectionFact,
    ApplicationProjectionOutcome,
    ResourceReference,
)


class PolicyExportApplicationCatalogueAdapter:
    def __init__(self, *, resolver: ResolveApplicationProjection) -> None:
        self._resolver = resolver

    def resolve_projection(self, *, subject, as_of) -> ApplicationProjectionFact:
        catalogue_subject = DirectedInteractionIdentity(
            source_component_deployment_id=subject.source_component_deployment_id,
            destination_component_deployment_id=subject.destination_component_deployment_id,
            dcs_contract_revision_id=subject.dcs_contract_revision_id,
        )
        result = self._resolver.execute(
            subject=catalogue_subject,
            as_of=as_of,
        )
        outcome = {
            CatalogueResolutionOutcome.RESOLVED: ApplicationProjectionOutcome.RESOLVED,
            CatalogueResolutionOutcome.MISSING: ApplicationProjectionOutcome.MISSING,
            CatalogueResolutionOutcome.INVALID: ApplicationProjectionOutcome.INVALID,
            CatalogueResolutionOutcome.UNKNOWN: ApplicationProjectionOutcome.UNKNOWN,
        }[result.outcome]
        if (
            outcome is ApplicationProjectionOutcome.RESOLVED
            and result.subject != catalogue_subject
        ):
            outcome = ApplicationProjectionOutcome.INVALID
        if outcome is not ApplicationProjectionOutcome.RESOLVED:
            return ApplicationProjectionFact(outcome=outcome)

        return ApplicationProjectionFact(
            outcome=outcome,
            subject=subject,
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
