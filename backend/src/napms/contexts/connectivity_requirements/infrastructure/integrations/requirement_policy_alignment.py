from napms.contexts.connectivity_requirements.application.ports import (
    RequirementPersistenceError,
)
from napms.contexts.connectivity_requirements.application.read import (
    GetAuthorizedRequirement,
    ListConnectivityRequirements,
    RequirementDetailOutcome,
)
from napms.contexts.connectivity_requirements.domain.model import (
    RequirementApplicabilityKind,
    RequirementLifecycleState,
)
from napms.workflows.requirement_policy_alignment.application.model import (
    AlignmentApplicability,
    AlignmentApplicabilityKind,
    AlignmentRequirementLifecycle,
    AlignmentSemanticIdentity,
    RequirementAlignmentSnapshot,
)
from napms.workflows.requirement_policy_alignment.application.ports import (
    RequirementAlignmentListOutcome,
    RequirementAlignmentListResult,
    RequirementAlignmentReadOutcome,
    RequirementAlignmentReadResult,
    RequirementAlignmentSnapshotPage,
)


def _snapshot(requirement) -> RequirementAlignmentSnapshot:
    applicability = requirement.applicability
    local_applicability = (
        AlignmentApplicability(AlignmentApplicabilityKind.ONGOING)
        if applicability.kind is RequirementApplicabilityKind.ONGOING
        else AlignmentApplicability(
            AlignmentApplicabilityKind.ABSOLUTE_WINDOW,
            start=applicability.start,
            end=applicability.end,
        )
    )
    return RequirementAlignmentSnapshot(
        requirement_id=requirement.requirement_id,
        semantic_identity=AlignmentSemanticIdentity(
            source_component_deployment_id=(
                requirement.required_interaction.source_component_deployment_id
            ),
            destination_component_deployment_id=(
                requirement.required_interaction.destination_component_deployment_id
            ),
            dcs_contract_revision_id=(
                requirement.required_interaction.dcs_contract_revision_id
            ),
        ),
        lifecycle=(
            AlignmentRequirementLifecycle.ACTIVE
            if requirement.lifecycle_state is RequirementLifecycleState.ACTIVE
            else AlignmentRequirementLifecycle.RETIRED
        ),
        applicability=local_applicability,
    )


class ConnectivityRequirementsAlignmentAdapter:
    def __init__(
        self,
        *,
        reader: GetAuthorizedRequirement,
        lister: ListConnectivityRequirements,
    ) -> None:
        self._reader = reader
        self._lister = lister

    def get_for_alignment(
        self,
        *,
        requirement_id,
        actor_id,
        as_of,
    ) -> RequirementAlignmentReadResult:
        try:
            result = self._reader.execute(
                requirement_id=requirement_id,
                actor_id=actor_id,
                effective_time=as_of,
            )
        except RequirementPersistenceError:
            return RequirementAlignmentReadResult(
                RequirementAlignmentReadOutcome.UNAVAILABLE
            )

        if result.outcome is RequirementDetailOutcome.REQUIREMENT_NOT_FOUND:
            return RequirementAlignmentReadResult(
                RequirementAlignmentReadOutcome.NOT_FOUND
            )
        if result.outcome is RequirementDetailOutcome.AUTHORITY_DENIED:
            return RequirementAlignmentReadResult(
                RequirementAlignmentReadOutcome.AUTHORITY_DENIED
            )
        if result.outcome is RequirementDetailOutcome.AUTHORITY_UNKNOWN:
            return RequirementAlignmentReadResult(
                RequirementAlignmentReadOutcome.AUTHORITY_UNKNOWN
            )

        if (
            result.requirement is None
            or result.read_authority_reference is None
        ):
            return RequirementAlignmentReadResult(
                RequirementAlignmentReadOutcome.AUTHORITY_UNKNOWN
            )

        return RequirementAlignmentReadResult(
            RequirementAlignmentReadOutcome.FOUND,
            snapshot=_snapshot(result.requirement),
            read_authority_reference=result.read_authority_reference,
        )


    def list_for_alignment(
        self,
        *,
        actor_id,
        as_of,
        page,
        page_size,
    ) -> RequirementAlignmentListResult:
        try:
            result = self._lister.execute(
                actor_id=actor_id,
                effective_time=as_of,
                page=page,
                page_size=page_size,
            )
        except RequirementPersistenceError:
            return RequirementAlignmentListResult(
                RequirementAlignmentListOutcome.UNAVAILABLE
            )
        return RequirementAlignmentListResult(
            RequirementAlignmentListOutcome.AVAILABLE,
            page=RequirementAlignmentSnapshotPage(
                snapshots=tuple(_snapshot(value) for value in result.requirements),
                page=result.page,
                page_size=result.page_size,
                has_more=result.has_more,
                ambiguous_scopes=result.ambiguous_scopes,
            ),
        )
