from napms.application_catalogue.application.list_interactions import (
    ListDirectedInteractions,
)
from napms.application_catalogue.application.resolve import (
    CatalogueResolutionOutcome,
    ValidateDirectedInteraction,
)
from napms.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.contexts.connectivity_requirements.application.ports import (
    InteractionOutcome,
    RequirementInteractionCheck,
    RequirementInteractionPage,
)
from napms.contexts.connectivity_requirements.domain.model import RequiredSemanticInteraction


def _to_acc(identity: RequiredSemanticInteraction) -> DirectedInteractionIdentity:
    return DirectedInteractionIdentity(
        source_component_deployment_id=identity.source_component_deployment_id,
        destination_component_deployment_id=identity.destination_component_deployment_id,
        dcs_contract_revision_id=identity.dcs_contract_revision_id,
    )


def _to_requirement(
    identity: DirectedInteractionIdentity,
) -> RequiredSemanticInteraction:
    return RequiredSemanticInteraction(
        source_component_deployment_id=identity.source_component_deployment_id,
        destination_component_deployment_id=identity.destination_component_deployment_id,
        dcs_contract_revision_id=identity.dcs_contract_revision_id,
    )


class ConnectivityRequirementsCatalogueAdapter:
    def __init__(self, *, validator: ValidateDirectedInteraction) -> None:
        self._validator = validator

    def validate_required_interaction(
        self,
        *,
        identity: RequiredSemanticInteraction,
        effective_time,
    ) -> RequirementInteractionCheck:
        result = self._validator.execute(
            identity=_to_acc(identity),
            effective_time=effective_time,
        )
        outcome = {
            CatalogueResolutionOutcome.RESOLVED: InteractionOutcome.VALID,
            CatalogueResolutionOutcome.INVALID: InteractionOutcome.INVALID,
            CatalogueResolutionOutcome.MISSING: InteractionOutcome.UNKNOWN,
            CatalogueResolutionOutcome.UNKNOWN: InteractionOutcome.UNKNOWN,
        }[result.outcome]
        return RequirementInteractionCheck(
            outcome=outcome,
            identity=(
                _to_requirement(result.identity)
                if result.identity is not None
                else None
            ),
            provenance_reference=result.provenance_reference,
        )


class ConnectivityRequirementsInteractionDiscoveryAdapter:
    def __init__(self, *, discovery: ListDirectedInteractions) -> None:
        self._discovery = discovery

    def list_required_interactions(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
    ) -> RequirementInteractionPage:
        result = self._discovery.execute(
            page=page,
            page_size=page_size,
            search=search,
        )
        return RequirementInteractionPage(
            interactions=tuple(_to_requirement(item) for item in result.items),
            page=result.page,
            page_size=result.page_size,
            has_more=result.has_more,
        )
