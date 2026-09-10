from datetime import datetime, timezone
from uuid import UUID

from napms.application_catalogue.application.binding_curation import (
    DeploymentBindingMutationResult,
)
from napms.application_catalogue.application.structure_curation import CatalogueMutationOutcome
from napms.application_catalogue.application.target_binding_curation import (
    CreateDeploymentInteractionResourceBinding,
    CreateDeploymentInteractionResourceBindingCommand,
    EndDeploymentInteractionResourceBinding,
    EndDeploymentInteractionResourceBindingCommand,
)
from napms.application_catalogue.application.target_curation import TargetMutationOutcome
from napms.application_catalogue.domain.model import DeploymentResourceBinding
from napms.application_catalogue.domain.target_model import (
    DeploymentInteraction,
    DeploymentInteractionCompatibility,
    DeploymentInteractionResourceBinding,
    DeploymentInteractionSide,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


class TargetCatalogue:
    def __init__(self):
        self.interaction = DeploymentInteraction(
            deployment_interaction_id=UUID(int=1),
            application_deployment_id=UUID(int=2),
            interaction_definition_id=UUID(int=3),
            provenance_reference="prov:selection",
        )
        self.compatibility = DeploymentInteractionCompatibility(
            deployment_interaction_id=UUID(int=1),
            source_component_deployment_id=UUID(int=10),
            destination_component_deployment_id=UUID(int=11),
            current_dcs_revision_id=UUID(int=12),
        )

    def get_deployment_interaction(self, deployment_interaction_id):
        return self.interaction if deployment_interaction_id == UUID(int=1) else None

    def get_compatibility_projection(self, deployment_interaction_id):
        return self.compatibility if deployment_interaction_id == UUID(int=1) else None


class CreateBinding:
    def __init__(self):
        self.command = None

    def execute(self, command):
        self.command = command
        binding = DeploymentResourceBinding(
            reference_id="binding-1",
            component_deployment_id=command.component_deployment_id,
            resource_reference=command.resource_reference,
            valid_from=command.valid_from,
            valid_to=command.valid_to,
            provenance_reference="prov:binding",
        )
        return DeploymentBindingMutationResult(
            CatalogueMutationOutcome.CREATED,
            binding=binding,
            result_version=1,
        )


class BindingRepository:
    def __init__(self, binding):
        self.binding = binding

    def get_binding(self, reference_id):
        return self.binding if reference_id == self.binding.reference_id else None


class EndBinding:
    def __init__(self, binding):
        self.binding = binding
        self.command = None

    def execute(self, command):
        self.command = command
        ended = self.binding.ended(
            valid_to=command.valid_to,
            end_provenance_reference="prov:end",
        )
        return DeploymentBindingMutationResult(
            CatalogueMutationOutcome.UPDATED,
            binding=ended,
            result_version=ended.version,
        )


def test_source_binding_targets_only_source_compatibility_side() -> None:
    catalogue = TargetCatalogue()
    delegated = CreateBinding()
    result = CreateDeploymentInteractionResourceBinding(
        catalogue=catalogue,
        create_binding=delegated,
    ).execute(
        CreateDeploymentInteractionResourceBindingCommand(
            deployment_interaction_id=UUID(int=1),
            side=DeploymentInteractionSide.SOURCE,
            resource_reference="resource:web",
            valid_from=NOW,
            valid_to=None,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="binding-source",
        )
    )

    assert result.outcome is TargetMutationOutcome.CREATED
    assert delegated.command.component_deployment_id == UUID(int=10)
    assert isinstance(result.binding, DeploymentInteractionResourceBinding)
    assert result.binding.deployment_interaction_id == UUID(int=1)
    assert result.binding.side is DeploymentInteractionSide.SOURCE
    assert result.binding.resource_reference == "resource:web"
    assert not hasattr(result.binding, "component_deployment_id")


def test_destination_binding_targets_only_destination_compatibility_side() -> None:
    catalogue = TargetCatalogue()
    delegated = CreateBinding()
    result = CreateDeploymentInteractionResourceBinding(
        catalogue=catalogue,
        create_binding=delegated,
    ).execute(
        CreateDeploymentInteractionResourceBindingCommand(
            deployment_interaction_id=UUID(int=1),
            side=DeploymentInteractionSide.DESTINATION,
            resource_reference="resource:api",
            valid_from=NOW,
            valid_to=None,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="binding-destination",
        )
    )

    assert delegated.command.component_deployment_id == UUID(int=11)
    assert result.binding.side is DeploymentInteractionSide.DESTINATION


def test_end_binding_rejects_reference_owned_by_other_interaction_side() -> None:
    catalogue = TargetCatalogue()
    foreign_binding = DeploymentResourceBinding(
        reference_id="binding-foreign",
        component_deployment_id=UUID(int=11),
        resource_reference="resource:api",
        valid_from=NOW,
        valid_to=None,
        provenance_reference="prov:binding",
    )
    delegated = EndBinding(foreign_binding)

    result = EndDeploymentInteractionResourceBinding(
        catalogue=catalogue,
        bindings=BindingRepository(foreign_binding),
        end_binding=delegated,
    ).execute(
        EndDeploymentInteractionResourceBindingCommand(
            deployment_interaction_id=UUID(int=1),
            side=DeploymentInteractionSide.SOURCE,
            binding_reference="binding-foreign",
            valid_to=datetime(2026, 9, 10, 13, 0, tzinfo=timezone.utc),
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="end-binding",
        )
    )

    assert result.outcome is TargetMutationOutcome.INPUT_INVALID
    assert delegated.command is None


def test_end_binding_returns_target_projection_without_compatibility_identity() -> None:
    catalogue = TargetCatalogue()
    binding = DeploymentResourceBinding(
        reference_id="binding-source",
        component_deployment_id=UUID(int=10),
        resource_reference="resource:web",
        valid_from=NOW,
        valid_to=None,
        provenance_reference="prov:binding",
    )
    delegated = EndBinding(binding)

    result = EndDeploymentInteractionResourceBinding(
        catalogue=catalogue,
        bindings=BindingRepository(binding),
        end_binding=delegated,
    ).execute(
        EndDeploymentInteractionResourceBindingCommand(
            deployment_interaction_id=UUID(int=1),
            side=DeploymentInteractionSide.SOURCE,
            binding_reference="binding-source",
            valid_to=datetime(2026, 9, 10, 13, 0, tzinfo=timezone.utc),
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="end-binding-source",
        )
    )

    assert result.outcome is TargetMutationOutcome.UPDATED
    assert result.binding.deployment_interaction_id == UUID(int=1)
    assert result.binding.side is DeploymentInteractionSide.SOURCE
    assert result.binding.valid_to == datetime(2026, 9, 10, 13, 0, tzinfo=timezone.utc)
    assert not hasattr(result.binding, "component_deployment_id")
