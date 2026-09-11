from dataclasses import dataclass

from napms.contexts.connectivity_requirements.domain.model import (
    RequiredSemanticInteraction,
    RequirementApplicability,
    RequirementLifecycleState,
)


@dataclass(frozen=True, slots=True)
class ConnectivityRequirementInventorySnapshot:
    governance_scope: str
    required_interaction: RequiredSemanticInteraction
    lifecycle_state: RequirementLifecycleState
    applicability: RequirementApplicability
