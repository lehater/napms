from napms.contexts.application_catalogue.application.discovery.list_interactions import (
    ListDirectedInteractions,
)
from napms.contexts.application_catalogue.application.discovery.resolve import (
    CatalogueResolutionOutcome,
    ValidateDirectedInteraction,
)
from napms.contexts.application_catalogue.domain.model import DirectedInteractionIdentity
from napms.contexts.connectivity_decision.application.ports import (
    DecisionInteractionPage,
    DecisionSubjectCheck,
    SubjectOutcome,
)
from napms.contexts.connectivity_decision.domain.model import DecisionSubject


def _to_acc(subject: DecisionSubject) -> DirectedInteractionIdentity:
    return DirectedInteractionIdentity(
        source_component_deployment_id=subject.source_component_deployment_id,
        destination_component_deployment_id=subject.destination_component_deployment_id,
        dcs_contract_revision_id=subject.dcs_contract_revision_id,
    )


def _to_decision(identity: DirectedInteractionIdentity) -> DecisionSubject:
    return DecisionSubject(
        source_component_deployment_id=identity.source_component_deployment_id,
        destination_component_deployment_id=identity.destination_component_deployment_id,
        dcs_contract_revision_id=identity.dcs_contract_revision_id,
    )


class ConnectivityDecisionCatalogueAdapter:
    def __init__(self, *, validator: ValidateDirectedInteraction) -> None:
        self._validator = validator

    def validate_decision_subject(
        self,
        *,
        subject: DecisionSubject,
        effective_time,
    ) -> DecisionSubjectCheck:
        expected = _to_acc(subject)
        result = self._validator.execute(
            identity=expected,
            effective_time=effective_time,
        )
        outcome = {
            CatalogueResolutionOutcome.RESOLVED: SubjectOutcome.VALID,
            CatalogueResolutionOutcome.INVALID: SubjectOutcome.INVALID,
            CatalogueResolutionOutcome.MISSING: SubjectOutcome.UNKNOWN,
            CatalogueResolutionOutcome.UNKNOWN: SubjectOutcome.UNKNOWN,
        }[result.outcome]
        if outcome is SubjectOutcome.VALID and result.identity != expected:
            outcome = SubjectOutcome.INVALID

        return DecisionSubjectCheck(
            outcome=outcome,
            subject=subject if outcome is SubjectOutcome.VALID else None,
            provenance_reference=(
                result.provenance_reference
                if outcome is SubjectOutcome.VALID
                else None
            ),
        )


class ConnectivityDecisionInteractionDiscoveryAdapter:
    def __init__(self, *, discovery: ListDirectedInteractions) -> None:
        self._discovery = discovery

    def list_decision_subjects(
        self,
        *,
        page: int,
        page_size: int,
        search: str | None = None,
    ) -> DecisionInteractionPage:
        result = self._discovery.execute(
            page=page,
            page_size=page_size,
            search=search,
        )
        return DecisionInteractionPage(
            subjects=tuple(_to_decision(item) for item in result.items),
            page=result.page,
            page_size=result.page_size,
            has_more=result.has_more,
        )
