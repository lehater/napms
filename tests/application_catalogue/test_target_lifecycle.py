from datetime import datetime, timezone
from uuid import UUID

from napms.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.application_catalogue.application.target_curation import TargetMutationOutcome
from napms.application_catalogue.application.target_lifecycle import (
    RetireDeploymentInteraction,
    RetireDeploymentInteractionCommand,
    RetirementDependencyKind,
    TargetRetirementDependencies,
)
from napms.application_catalogue.application.target_ports import ActiveDependencyReference
from napms.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)
from napms.application_catalogue.domain.model import (
    Application,
    CatalogueLifecycleState,
    Component,
    ComponentDeployment,
    DeploymentResourceBinding,
)
from napms.application_catalogue.domain.target_model import (
    ApplicationDeployment,
    DeploymentInteraction,
    DeploymentInteractionCompatibility,
    InteractionDefinition,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


def _traffic():
    return (
        AuthoredDcsTrafficAlternative(
            protocol="tcp",
            source_ports=DcsPortConstraint.any(),
            destination_ports=DcsPortConstraint.ranged(DcsPortRange(443, 443)),
        ),
    )


class PermitAuthority:
    def check_curation(self, *, actor_id, effective_time):
        return ApplicationCatalogueAuthorityCheck(
            ApplicationCatalogueAuthorityOutcome.PERMITTED,
            authority_reference="authority:catalogue",
        )


class DependencyPort:
    def __init__(self, *references):
        self.references = tuple(ActiveDependencyReference(value) for value in references)

    def find_active_references(self, *, subject, as_of):
        return self.references


class Provenance:
    def for_deployment_interaction_retirement(self, **kwargs):
        return f"prov:retire:interaction:{kwargs['deployment_interaction_id']}"

    def for_component_deployment_retirement(self, **kwargs):
        return f"prov:retire:compat:{kwargs['deployment_id']}"


class FakeLifecycleCatalogue:
    def __init__(self):
        self.application = Application(UUID(int=1), "CRM", "prov:app")
        self.components = {
            UUID(int=2): Component(UUID(int=2), UUID(int=1), "Web", "prov:web"),
            UUID(int=3): Component(UUID(int=3), UUID(int=1), "API", "prov:api"),
        }
        self.definition = InteractionDefinition(
            interaction_definition_id=UUID(int=4),
            application_id=UUID(int=1),
            source_component_id=UUID(int=2),
            destination_component_id=UUID(int=3),
            traffic_alternatives=_traffic(),
            provenance_reference="prov:def",
        )
        self.deployment = ApplicationDeployment(
            application_deployment_id=UUID(int=5),
            application_id=UUID(int=1),
            company_reference="Company A",
            environment="Production",
            scope_reference="Moscow",
            provenance_reference="prov:deployment",
        )
        self.interaction = DeploymentInteraction(
            deployment_interaction_id=UUID(int=6),
            application_deployment_id=UUID(int=5),
            interaction_definition_id=UUID(int=4),
            provenance_reference="prov:selection",
        )
        self.compatibility = DeploymentInteractionCompatibility(
            deployment_interaction_id=UUID(int=6),
            source_component_deployment_id=UUID(int=7),
            destination_component_deployment_id=UUID(int=8),
            current_dcs_revision_id=UUID(int=9),
        )
        self.component_deployments = {
            UUID(int=7): ComponentDeployment(UUID(int=7), UUID(int=2), "prov:compat-source"),
            UUID(int=8): ComponentDeployment(UUID(int=8), UUID(int=3), "prov:compat-destination"),
        }
        self.bindings = ()
        self.receipts = {}

    def get_deployment_interaction(self, value):
        return self.interaction if value == self.interaction.deployment_interaction_id else None

    def save_deployment_interaction(self, value, *, expected_version):
        assert self.interaction.version == expected_version
        self.interaction = value

    def get_compatibility_projection(self, value):
        return self.compatibility if value == self.compatibility.deployment_interaction_id else None

    def get_component_deployment(self, value):
        return self.component_deployments.get(value)

    def save_component_deployment(self, value, *, expected_version):
        assert self.component_deployments[value.deployment_id].version == expected_version
        self.component_deployments[value.deployment_id] = value

    def find_effective_bindings(self, *, component_deployment_id, as_of):
        return tuple(
            item
            for item in self.bindings
            if item.component_deployment_id == component_deployment_id
            and item.is_effective_at(as_of)
        )

    def list_active_components_for_application(self, *, application_id):
        return tuple(
            item
            for item in self.components.values()
            if item.application_id == application_id
            and item.lifecycle_state is CatalogueLifecycleState.ACTIVE
        )

    def list_active_interaction_definitions_for_application(self, *, application_id):
        return (self.definition,) if self.definition.application_id == application_id else ()

    def list_active_application_deployments_for_application(self, *, application_id):
        return (self.deployment,) if self.deployment.application_id == application_id else ()

    def list_active_interaction_definitions_for_component(self, *, component_id):
        if component_id in (self.definition.source_component_id, self.definition.destination_component_id):
            return (self.definition,)
        return ()

    def list_active_legacy_component_deployments(self, *, component_id):
        return ()

    def list_active_deployment_interactions_for_definition(self, *, interaction_definition_id):
        return (
            (self.interaction,)
            if self.interaction.interaction_definition_id == interaction_definition_id
            and self.interaction.lifecycle_state is CatalogueLifecycleState.ACTIVE
            else ()
        )

    def list_active_deployment_interactions_for_deployment(self, *, application_deployment_id):
        return (
            (self.interaction,)
            if self.interaction.application_deployment_id == application_deployment_id
            and self.interaction.lifecycle_state is CatalogueLifecycleState.ACTIVE
            else ()
        )

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        pass


def _dependencies(catalogue, *, requirements=(), decisions=(), rules=()):
    return TargetRetirementDependencies(
        catalogue=catalogue,
        requirements=DependencyPort(*requirements),
        decisions=DependencyPort(*decisions),
        access_rules=DependencyPort(*rules),
    )


def test_application_dependency_summary_is_server_derived_by_semantic_group() -> None:
    catalogue = FakeLifecycleCatalogue()

    groups = _dependencies(catalogue).for_application(application_id=UUID(int=1))

    assert [(group.kind, group.count) for group in groups] == [
        (RetirementDependencyKind.COMPONENTS, 2),
        (RetirementDependencyKind.INTERACTIONS, 1),
        (RetirementDependencyKind.APPLICATION_DEPLOYMENTS, 1),
    ]


def test_deployment_interaction_dependencies_include_bindings_and_downstream_owners() -> None:
    catalogue = FakeLifecycleCatalogue()
    catalogue.bindings = (
        DeploymentResourceBinding(
            reference_id="binding-source",
            component_deployment_id=UUID(int=7),
            resource_reference="resource:web",
            valid_from=NOW,
            valid_to=None,
            provenance_reference="prov:binding",
        ),
    )

    groups = _dependencies(
        catalogue,
        requirements=("requirement-1",),
        decisions=("decision-1",),
        rules=("rule-1",),
    ).for_deployment_interaction(
        deployment_interaction_id=UUID(int=6),
        as_of=NOW,
    )

    assert {group.kind: group.count for group in groups} == {
        RetirementDependencyKind.RESOURCE_BINDINGS: 1,
        RetirementDependencyKind.CONNECTIVITY_REQUIREMENTS: 1,
        RetirementDependencyKind.CONNECTIVITY_DECISIONS: 1,
        RetirementDependencyKind.ACCESS_RULES: 1,
    }


def test_deployment_interaction_retirement_is_blocked_before_compatibility_sides_change() -> None:
    catalogue = FakeLifecycleCatalogue()
    service = RetireDeploymentInteraction(
        authority=PermitAuthority(),
        catalogue=catalogue,
        provenance=Provenance(),
        dependencies=_dependencies(catalogue, rules=("rule-1",)),
    )

    result = service.execute(
        RetireDeploymentInteractionCommand(
            deployment_interaction_id=UUID(int=6),
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="retire-selection",
        )
    )

    assert result.outcome is TargetMutationOutcome.DEPENDENCY_BLOCKED
    assert catalogue.interaction.lifecycle_state is CatalogueLifecycleState.ACTIVE
    assert catalogue.component_deployments[UUID(int=7)].lifecycle_state is CatalogueLifecycleState.ACTIVE
    assert catalogue.component_deployments[UUID(int=8)].lifecycle_state is CatalogueLifecycleState.ACTIVE


def test_deployment_interaction_retirement_retires_both_compatibility_sides_only_after_clear() -> None:
    catalogue = FakeLifecycleCatalogue()
    service = RetireDeploymentInteraction(
        authority=PermitAuthority(),
        catalogue=catalogue,
        provenance=Provenance(),
        dependencies=_dependencies(catalogue),
    )
    command = RetireDeploymentInteractionCommand(
        deployment_interaction_id=UUID(int=6),
        expected_version=1,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key="retire-selection",
    )

    result = service.execute(command)
    replay = service.execute(command)

    assert result.outcome is TargetMutationOutcome.UPDATED
    assert replay.outcome is TargetMutationOutcome.RESOLVED
    assert catalogue.interaction.lifecycle_state is CatalogueLifecycleState.RETIRED
    assert catalogue.component_deployments[UUID(int=7)].lifecycle_state is CatalogueLifecycleState.RETIRED
    assert catalogue.component_deployments[UUID(int=8)].lifecycle_state is CatalogueLifecycleState.RETIRED
    assert catalogue.compatibility.current_dcs_revision_id == UUID(int=9)
