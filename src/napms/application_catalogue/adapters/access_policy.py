from napms.access_policy.application.ports import (
    InteractionCheck,
    InteractionOutcome,
)
from napms.application_catalogue.application.resolve import (
    CatalogueResolutionOutcome,
    ValidateDirectedInteraction,
)


class AccessPolicyCommunicationCatalogueAdapter:
    def __init__(self, *, validator: ValidateDirectedInteraction) -> None:
        self._validator = validator

    def resolve_directed_interaction(
        self,
        *,
        identity,
        effective_time,
    ) -> InteractionCheck:
        result = self._validator.execute(
            identity=identity,
            effective_time=effective_time,
        )
        outcome = {
            CatalogueResolutionOutcome.RESOLVED: InteractionOutcome.VALID,
            CatalogueResolutionOutcome.INVALID: InteractionOutcome.INVALID,
            CatalogueResolutionOutcome.MISSING: InteractionOutcome.UNKNOWN,
            CatalogueResolutionOutcome.UNKNOWN: InteractionOutcome.UNKNOWN,
        }[result.outcome]
        return InteractionCheck(
            outcome=outcome,
            identity=result.identity if outcome is InteractionOutcome.VALID else None,
            provenance_reference=(
                result.provenance_reference
                if outcome is InteractionOutcome.VALID
                else None
            ),
        )
