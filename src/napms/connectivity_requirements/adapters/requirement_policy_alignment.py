from napms.connectivity_requirements.application.ports import (
    RequirementPersistenceError,
)
from napms.connectivity_requirements.application.read import (
    GetAuthorizedRequirement,
    RequirementDetailOutcome,
)
from napms.connectivity_requirements.domain.model import (
    RequirementApplicabilityKind,
    RequirementLifecycleState,
)
from napms.requirement_policy_alignment.application.model import (
    AlignmentApplicability,
    AlignmentApplicabilityKind,
    AlignmentRequirementLifecycle,
    AlignmentSemanticIdentity,
    RequirementAlignmentSnapshot,
)
from napms.requirement_policy_alignment.application.ports import (
    RequirementAlignmentReadOutcome,
    RequirementAlignmentReadResult,
)


class ConnectivityRequirementsAlignmentAdapter:
    def __init__(self, *, reader: GetAuthorizedRequirement) -> None:
        self._reader = reader

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

        requirement = result.requirement
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
        return RequirementAlignmentReadResult(
            RequirementAlignmentReadOutcome.FOUND,
            snapshot=RequirementAlignmentSnapshot(
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
                    if requirement.lifecycle_state
                    is RequirementLifecycleState.ACTIVE
                    else AlignmentRequirementLifecycle.RETIRED
                ),
                applicability=local_applicability,
            ),
            read_authority_reference=result.read_authority_reference,
        )
