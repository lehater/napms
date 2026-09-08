from napms.access_policy.application.ports import (
    InteractionCheck,
    InteractionOutcome,
)
from napms.application_catalogue.application.resolve import (
    CatalogueResolutionOutcome,
    ValidateDirectedInteraction,
)
from napms.application_catalogue.domain.model import DirectedInteractionIdentity


class AccessPolicyCommunicationCatalogueAdapter:
    def __init__(self, *, validator: ValidateDirectedInteraction) -> None:
        self._validator = validator

    def resolve_directed_interaction(
        self,
        *,
        identity,
        effective_time,
    ) -> InteractionCheck:
        catalogue_identity = DirectedInteractionIdentity(
            source_component_deployment_id=identity.source_component_deployment_id,
            destination_component_deployment_id=identity.destination_component_deployment_id,
            dcs_contract_revision_id=identity.dcs_contract_revision_id,
        )
        result = self._validator.execute(
            identity=catalogue_identity,
            effective_time=effective_time,
        )
        outcome = {
            CatalogueResolutionOutcome.RESOLVED: InteractionOutcome.VALID,
            CatalogueResolutionOutcome.INVALID: InteractionOutcome.INVALID,
            CatalogueResolutionOutcome.MISSING: InteractionOutcome.UNKNOWN,
            CatalogueResolutionOutcome.UNKNOWN: InteractionOutcome.UNKNOWN,
        }[result.outcome]
        if (
            outcome is InteractionOutcome.VALID
            and result.identity != catalogue_identity
        ):
            outcome = InteractionOutcome.INVALID

        return InteractionCheck(
            outcome=outcome,
            identity=identity if outcome is InteractionOutcome.VALID else None,
            provenance_reference=(
                result.provenance_reference
                if outcome is InteractionOutcome.VALID
                else None
            ),
        )
