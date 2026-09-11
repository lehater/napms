from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.contexts.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)
from napms.contexts.application_catalogue.domain.model import (
    CatalogueInvariantError,
    CatalogueLifecycleState,
)
from napms.contexts.application_catalogue.domain.target_model import (
    ApplicationDeployment,
    DeploymentInteraction,
    DeploymentInteractionCompatibility,
    DeploymentInteractionResourceBinding,
    DeploymentInteractionSide,
    InteractionDefinition,
)


def _traffic(port: int) -> tuple[AuthoredDcsTrafficAlternative, ...]:
    return (
        AuthoredDcsTrafficAlternative(
            protocol="tcp",
            source_ports=DcsPortConstraint.any(),
            destination_ports=DcsPortConstraint.ranged(DcsPortRange(port, port)),
        ),
    )


def test_interaction_definition_canonicalizes_traffic_and_versions_semantic_edits() -> None:
    interaction = InteractionDefinition(
        interaction_definition_id=UUID(int=1),
        application_id=UUID(int=2),
        source_component_id=UUID(int=3),
        destination_component_id=UUID(int=4),
        traffic_alternatives=_traffic(443),
        provenance_reference="prov:create",
    )

    changed = interaction.changed_traffic(_traffic(8443))

    assert interaction.version == 1
    assert changed.version == 2
    assert changed.traffic_alternatives == _traffic(8443)
    assert changed.source_component_id == interaction.source_component_id
    assert changed.destination_component_id == interaction.destination_component_id


def test_interaction_definition_rejects_noop_and_retired_edits() -> None:
    interaction = InteractionDefinition(
        interaction_definition_id=UUID(int=1),
        application_id=UUID(int=2),
        source_component_id=UUID(int=3),
        destination_component_id=UUID(int=4),
        traffic_alternatives=_traffic(443),
        provenance_reference="prov:create",
    )

    with pytest.raises(CatalogueInvariantError):
        interaction.changed_traffic(_traffic(443))

    retired = interaction.retired(retirement_provenance_reference="prov:retire")
    assert retired.lifecycle_state is CatalogueLifecycleState.RETIRED
    assert retired.version == 2

    with pytest.raises(CatalogueInvariantError):
        retired.changed_endpoints(
            source_component_id=UUID(int=5),
            destination_component_id=UUID(int=6),
        )


def test_application_deployment_context_is_required_but_not_identity() -> None:
    deployment = ApplicationDeployment(
        application_deployment_id=UUID(int=10),
        application_id=UUID(int=11),
        company_reference=" Company A ",
        environment=" Production ",
        scope_reference=" Moscow ",
        provenance_reference="prov:create",
    )

    changed = deployment.changed_context(
        company_reference="Company B",
        environment="Test",
        scope_reference="SPb",
    )

    assert deployment.company_reference == "Company A"
    assert deployment.environment == "Production"
    assert deployment.scope_reference == "Moscow"
    assert changed.application_deployment_id == deployment.application_deployment_id
    assert changed.version == 2

    with pytest.raises(CatalogueInvariantError):
        ApplicationDeployment(
            application_deployment_id=UUID(int=12),
            application_id=UUID(int=11),
            company_reference="",
            environment="Production",
            scope_reference="Moscow",
            provenance_reference="prov:create",
        )


def test_compatibility_side_ids_are_stable_when_current_dcs_advances() -> None:
    compatibility = DeploymentInteractionCompatibility(
        deployment_interaction_id=UUID(int=20),
        source_component_deployment_id=UUID(int=21),
        destination_component_deployment_id=UUID(int=22),
        current_dcs_revision_id=UUID(int=23),
    )

    advanced = compatibility.advanced_to(UUID(int=24))

    assert advanced.source_component_deployment_id == UUID(int=21)
    assert advanced.destination_component_deployment_id == UUID(int=22)
    assert advanced.current_dcs_revision_id == UUID(int=24)
    assert advanced.version == 2


def test_deployment_interaction_and_resource_binding_preserve_history() -> None:
    interaction = DeploymentInteraction(
        deployment_interaction_id=UUID(int=30),
        application_deployment_id=UUID(int=31),
        interaction_definition_id=UUID(int=32),
        provenance_reference="prov:create",
    )
    retired = interaction.retired(retirement_provenance_reference="prov:retire")
    assert retired.lifecycle_state is CatalogueLifecycleState.RETIRED

    start = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
    end = datetime(2026, 9, 10, 13, 0, tzinfo=timezone.utc)
    binding = DeploymentInteractionResourceBinding(
        reference_id="binding-1",
        deployment_interaction_id=interaction.deployment_interaction_id,
        side=DeploymentInteractionSide.SOURCE,
        resource_reference="resource-1",
        valid_from=start,
        valid_to=None,
        provenance_reference="prov:binding",
    )

    ended = binding.ended(valid_to=end, end_provenance_reference="prov:end")

    assert binding.is_effective_at(start)
    assert ended.valid_to == end
    assert ended.version == 2
    assert not ended.is_effective_at(end)
