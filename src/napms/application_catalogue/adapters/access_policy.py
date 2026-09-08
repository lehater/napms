from napms.access_policy.application.ports import (
    InteractionCheck,
    InteractionOutcome,
    ProposalInteractionPage,
)
from napms.access_policy.domain.model import RuleSemanticIdentity
from napms.application_catalogue.application.list_interactions import (
    ListDirectedInteractions,
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


class AccessPolicyProposalInteractionCatalogueAdapter:
    """Translate ACC directed-interaction discovery to Access Policy identities."""

    def __init__(self, *, discovery: ListDirectedInteractions) -> None:
        self._discovery = discovery

    def list_directed_interactions(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
    ) -> ProposalInteractionPage:
        result = self._discovery.execute(
            page=page,
            page_size=page_size,
            search=search,
        )
        return ProposalInteractionPage(
            identities=tuple(
                RuleSemanticIdentity(
                    source_component_deployment_id=item.source_component_deployment_id,
                    destination_component_deployment_id=item.destination_component_deployment_id,
                    dcs_contract_revision_id=item.dcs_contract_revision_id,
                )
                for item in result.items
            ),
            page=result.page,
            page_size=result.page_size,
            has_more=result.has_more,
        )
