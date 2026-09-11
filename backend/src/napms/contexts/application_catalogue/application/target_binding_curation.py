from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from napms.contexts.application_catalogue.application.binding_curation import (
    CreateDeploymentResourceBinding,
    CreateDeploymentResourceBindingCommand,
    DeploymentBindingCurationRepository,
    DeploymentBindingMutationResult,
    EndDeploymentResourceBinding,
    EndDeploymentResourceBindingCommand,
)
from napms.contexts.application_catalogue.application.structure_curation import (
    CatalogueMutationOutcome,
)
from napms.contexts.application_catalogue.application.target_curation import (
    TargetMutationOutcome,
)
from napms.contexts.application_catalogue.application.target_ports import (
    TargetApplicationCatalogueRepository,
)
from napms.contexts.application_catalogue.domain.model import (
    CatalogueLifecycleState,
    DeploymentResourceBinding,
)
from napms.contexts.application_catalogue.domain.target_model import (
    DeploymentInteractionResourceBinding,
    DeploymentInteractionSide,
)


@dataclass(frozen=True, slots=True)
class CreateDeploymentInteractionResourceBindingCommand:
    deployment_interaction_id: UUID
    side: DeploymentInteractionSide
    resource_reference: str
    valid_from: datetime
    valid_to: datetime | None
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class EndDeploymentInteractionResourceBindingCommand:
    deployment_interaction_id: UUID
    side: DeploymentInteractionSide
    binding_reference: str
    valid_to: datetime
    expected_version: int
    actor_id: str
    effective_time: datetime
    idempotency_key: str


@dataclass(frozen=True, slots=True)
class DeploymentInteractionBindingMutationResult:
    outcome: TargetMutationOutcome
    binding: DeploymentInteractionResourceBinding | None = None


def _target_outcome(value: CatalogueMutationOutcome) -> TargetMutationOutcome:
    mapping = {
        CatalogueMutationOutcome.CREATED: TargetMutationOutcome.CREATED,
        CatalogueMutationOutcome.UPDATED: TargetMutationOutcome.UPDATED,
        CatalogueMutationOutcome.RESOLVED: TargetMutationOutcome.RESOLVED,
        CatalogueMutationOutcome.AUTHORITY_DENIED: TargetMutationOutcome.AUTHORITY_DENIED,
        CatalogueMutationOutcome.AUTHORITY_UNKNOWN: TargetMutationOutcome.AUTHORITY_UNKNOWN,
        CatalogueMutationOutcome.NOT_FOUND: TargetMutationOutcome.NOT_FOUND,
        CatalogueMutationOutcome.PARENT_INACTIVE: TargetMutationOutcome.PARENT_INACTIVE,
        CatalogueMutationOutcome.INPUT_INVALID: TargetMutationOutcome.INPUT_INVALID,
        CatalogueMutationOutcome.CONCURRENCY_CONFLICT: TargetMutationOutcome.CONCURRENCY_CONFLICT,
        CatalogueMutationOutcome.IDEMPOTENCY_CONFLICT: TargetMutationOutcome.IDEMPOTENCY_CONFLICT,
        CatalogueMutationOutcome.PERSISTENCE_UNKNOWN: TargetMutationOutcome.PERSISTENCE_UNKNOWN,
        CatalogueMutationOutcome.RETIREMENT_BLOCKED: TargetMutationOutcome.DEPENDENCY_BLOCKED,
    }
    return mapping[value]


def _compatibility_side_id(*, compatibility, side: DeploymentInteractionSide) -> UUID:
    if side is DeploymentInteractionSide.SOURCE:
        return compatibility.source_component_deployment_id
    return compatibility.destination_component_deployment_id


def _target_binding(
    *,
    binding: DeploymentResourceBinding | None,
    deployment_interaction_id: UUID,
    side: DeploymentInteractionSide,
) -> DeploymentInteractionResourceBinding | None:
    if binding is None:
        return None
    return DeploymentInteractionResourceBinding(
        reference_id=binding.reference_id,
        deployment_interaction_id=deployment_interaction_id,
        side=side,
        resource_reference=binding.resource_reference,
        valid_from=binding.valid_from,
        valid_to=binding.valid_to,
        provenance_reference=binding.provenance_reference,
        end_provenance_reference=binding.end_provenance_reference,
        version=binding.version,
    )


class CreateDeploymentInteractionResourceBinding:
    """Translate target interaction-side binding intent to the existing temporal binding use case."""

    def __init__(
        self,
        *,
        catalogue: TargetApplicationCatalogueRepository,
        create_binding: CreateDeploymentResourceBinding,
    ) -> None:
        self._catalogue = catalogue
        self._create_binding = create_binding

    def execute(
        self,
        command: CreateDeploymentInteractionResourceBindingCommand,
    ) -> DeploymentInteractionBindingMutationResult:
        interaction = self._catalogue.get_deployment_interaction(
            command.deployment_interaction_id
        )
        if interaction is None:
            return DeploymentInteractionBindingMutationResult(TargetMutationOutcome.NOT_FOUND)
        if interaction.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
            return DeploymentInteractionBindingMutationResult(
                TargetMutationOutcome.PARENT_INACTIVE
            )
        compatibility = self._catalogue.get_compatibility_projection(
            command.deployment_interaction_id
        )
        if compatibility is None:
            return DeploymentInteractionBindingMutationResult(
                TargetMutationOutcome.PERSISTENCE_UNKNOWN
            )

        result = self._create_binding.execute(
            CreateDeploymentResourceBindingCommand(
                component_deployment_id=_compatibility_side_id(
                    compatibility=compatibility,
                    side=command.side,
                ),
                resource_reference=command.resource_reference,
                valid_from=command.valid_from,
                valid_to=command.valid_to,
                actor_id=command.actor_id,
                effective_time=command.effective_time,
                idempotency_key=command.idempotency_key,
            )
        )
        return DeploymentInteractionBindingMutationResult(
            _target_outcome(result.outcome),
            binding=_target_binding(
                binding=result.binding,
                deployment_interaction_id=command.deployment_interaction_id,
                side=command.side,
            ),
        )


class EndDeploymentInteractionResourceBinding:
    """End only a compatibility binding owned by the requested interaction side."""

    def __init__(
        self,
        *,
        catalogue: TargetApplicationCatalogueRepository,
        bindings: DeploymentBindingCurationRepository,
        end_binding: EndDeploymentResourceBinding,
    ) -> None:
        self._catalogue = catalogue
        self._bindings = bindings
        self._end_binding = end_binding

    def execute(
        self,
        command: EndDeploymentInteractionResourceBindingCommand,
    ) -> DeploymentInteractionBindingMutationResult:
        interaction = self._catalogue.get_deployment_interaction(
            command.deployment_interaction_id
        )
        if interaction is None:
            return DeploymentInteractionBindingMutationResult(TargetMutationOutcome.NOT_FOUND)
        if interaction.lifecycle_state is not CatalogueLifecycleState.ACTIVE:
            return DeploymentInteractionBindingMutationResult(
                TargetMutationOutcome.PARENT_INACTIVE
            )
        compatibility = self._catalogue.get_compatibility_projection(
            command.deployment_interaction_id
        )
        if compatibility is None:
            return DeploymentInteractionBindingMutationResult(
                TargetMutationOutcome.PERSISTENCE_UNKNOWN
            )
        binding_reference = command.binding_reference.strip()
        if not binding_reference:
            return DeploymentInteractionBindingMutationResult(TargetMutationOutcome.INPUT_INVALID)
        binding = self._bindings.get_binding(binding_reference)
        if binding is None:
            return DeploymentInteractionBindingMutationResult(TargetMutationOutcome.NOT_FOUND)
        expected_component_deployment_id = _compatibility_side_id(
            compatibility=compatibility,
            side=command.side,
        )
        if binding.component_deployment_id != expected_component_deployment_id:
            return DeploymentInteractionBindingMutationResult(
                TargetMutationOutcome.INPUT_INVALID
            )

        result: DeploymentBindingMutationResult = self._end_binding.execute(
            EndDeploymentResourceBindingCommand(
                binding_reference=binding_reference,
                valid_to=command.valid_to,
                expected_version=command.expected_version,
                actor_id=command.actor_id,
                effective_time=command.effective_time,
                idempotency_key=command.idempotency_key,
            )
        )
        return DeploymentInteractionBindingMutationResult(
            _target_outcome(result.outcome),
            binding=_target_binding(
                binding=result.binding,
                deployment_interaction_id=command.deployment_interaction_id,
                side=command.side,
            ),
        )
