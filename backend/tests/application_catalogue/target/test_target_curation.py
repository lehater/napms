from datetime import datetime, timezone
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.contexts.application_catalogue.application.target.curation import (
    CreateApplicationDeployment,
    CreateApplicationDeploymentCommand,
    CreateInteractionDefinition,
    CreateInteractionDefinitionCommand,
    SelectDeploymentInteraction,
    SelectDeploymentInteractionCommand,
    TargetDependencyKind,
    TargetMutationOutcome,
    UpdateInteractionDefinitionEndpoints,
    UpdateInteractionDefinitionEndpointsCommand,
    UpdateInteractionDefinitionTraffic,
    UpdateInteractionDefinitionTrafficCommand,
)
from napms.contexts.application_catalogue.application.target.ports import ActiveDependencyReference
from napms.contexts.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)
from napms.contexts.application_catalogue.domain.model import (
    Application,
    CatalogueLifecycleState,
    Component,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


def _traffic(port: int) -> tuple[AuthoredDcsTrafficAlternative, ...]:
    return (
        AuthoredDcsTrafficAlternative(
            protocol="tcp",
            source_ports=DcsPortConstraint.any(),
            destination_ports=DcsPortConstraint.ranged(DcsPortRange(port, port)),
        ),
    )


class PermitAuthority:
    def check_curation(self, *, actor_id, effective_time):
        return ApplicationCatalogueAuthorityCheck(
            ApplicationCatalogueAuthorityOutcome.PERMITTED,
            authority_reference="authority:catalogue",
        )


class FakeIdentities:
    def __init__(self) -> None:
        self._next = 100

    def _uuid(self):
        self._next += 1
        return UUID(int=self._next)

    def new_application_id(self):
        return self._uuid()

    def new_component_id(self):
        return self._uuid()

    def new_component_deployment_id(self):
        return self._uuid()

    def new_dcs_revision_id(self):
        return self._uuid()

    def new_interaction_definition_id(self):
        return self._uuid()

    def new_application_deployment_id(self):
        return self._uuid()

    def new_deployment_interaction_id(self):
        return self._uuid()


class FakeProvenance:
    def for_interaction_definition(self, **kwargs):
        return f"prov:interaction:{kwargs['interaction_definition_id']}"

    def for_application_deployment(self, **kwargs):
        return f"prov:application-deployment:{kwargs['application_deployment_id']}"

    def for_deployment_interaction(self, **kwargs):
        return f"prov:deployment-interaction:{kwargs['deployment_interaction_id']}"

    def for_compatibility_component_deployment(self, **kwargs):
        return (
            f"prov:compat:{kwargs['deployment_interaction_id']}:"
            f"{kwargs['side'].value}:{kwargs['component_deployment_id']}"
        )

    def for_dcs_revision(self, **kwargs):
        return f"prov:dcs:{kwargs['revision_id']}"


class FakeEncoder:
    def encode(self, alternatives):
        ports = []
        for alternative in alternatives:
            ports.extend(
                (value.first, value.last)
                for value in alternative.destination_ports.ranges
            )
        return repr((tuple(item.protocol for item in alternatives), tuple(ports))).encode()


class DependencyPort:
    def __init__(self, references=()) -> None:
        self.references = tuple(references)
        self.subjects = []

    def find_active_references(self, *, subject, as_of):
        self.subjects.append(subject)
        return self.references


class FakeCatalogue:
    def __init__(self) -> None:
        self.applications = {}
        self.components = {}
        self.component_deployments = {}
        self.dcs_revisions = {}
        self.interaction_definitions = {}
        self.application_deployments = {}
        self.deployment_interactions = {}
        self.compatibility = {}
        self.receipts = {}
        self.commits = 0

    def get_application(self, application_id):
        return self.applications.get(application_id)

    def get_component(self, component_id):
        return self.components.get(component_id)

    def get_component_deployment(self, deployment_id):
        return self.component_deployments.get(deployment_id)

    def add_component_deployment(self, deployment):
        self.component_deployments[deployment.deployment_id] = deployment

    def save_component_deployment(self, deployment, *, expected_version):
        assert self.component_deployments[deployment.deployment_id].version == expected_version
        self.component_deployments[deployment.deployment_id] = deployment

    def get_dcs_revision(self, revision_id):
        return self.dcs_revisions.get(revision_id)

    def add_dcs_revision(self, revision):
        self.dcs_revisions[revision.revision_id] = revision

    def get_interaction_definition(self, interaction_definition_id):
        return self.interaction_definitions.get(interaction_definition_id)

    def add_interaction_definition(self, value):
        self.interaction_definitions[value.interaction_definition_id] = value

    def save_interaction_definition(self, value, *, expected_version):
        assert self.interaction_definitions[value.interaction_definition_id].version == expected_version
        self.interaction_definitions[value.interaction_definition_id] = value

    def list_active_deployment_interactions_for_definition(self, *, interaction_definition_id):
        return tuple(
            item
            for item in self.deployment_interactions.values()
            if item.interaction_definition_id == interaction_definition_id
            and item.lifecycle_state is CatalogueLifecycleState.ACTIVE
        )

    def get_application_deployment(self, application_deployment_id):
        return self.application_deployments.get(application_deployment_id)

    def add_application_deployment(self, value):
        self.application_deployments[value.application_deployment_id] = value

    def save_application_deployment(self, value, *, expected_version):
        assert self.application_deployments[value.application_deployment_id].version == expected_version
        self.application_deployments[value.application_deployment_id] = value

    def get_deployment_interaction(self, deployment_interaction_id):
        return self.deployment_interactions.get(deployment_interaction_id)

    def find_active_deployment_interaction(
        self,
        *,
        application_deployment_id,
        interaction_definition_id,
    ):
        for item in self.deployment_interactions.values():
            if (
                item.application_deployment_id == application_deployment_id
                and item.interaction_definition_id == interaction_definition_id
                and item.lifecycle_state is CatalogueLifecycleState.ACTIVE
            ):
                return item
        return None

    def add_deployment_interaction(self, value):
        self.deployment_interactions[value.deployment_interaction_id] = value

    def save_deployment_interaction(self, value, *, expected_version):
        assert self.deployment_interactions[value.deployment_interaction_id].version == expected_version
        self.deployment_interactions[value.deployment_interaction_id] = value

    def get_compatibility_projection(self, deployment_interaction_id):
        return self.compatibility.get(deployment_interaction_id)

    def add_compatibility_projection(self, value):
        self.compatibility[value.deployment_interaction_id] = value

    def save_compatibility_projection(self, value, *, expected_version):
        assert self.compatibility[value.deployment_interaction_id].version == expected_version
        self.compatibility[value.deployment_interaction_id] = value

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        self.commits += 1


def _catalogue() -> FakeCatalogue:
    catalogue = FakeCatalogue()
    app = Application(
        application_id=UUID(int=1),
        display_name="CRM",
        provenance_reference="prov:app",
    )
    catalogue.applications[app.application_id] = app
    for component_id, name in ((2, "Web"), (3, "API"), (4, "Database")):
        component = Component(
            component_id=UUID(int=component_id),
            application_id=app.application_id,
            display_name=name,
            provenance_reference=f"prov:{name}",
        )
        catalogue.components[component.component_id] = component
    return catalogue


def _create_definition(catalogue, identities, provenance, *, source=2, destination=3, port=443):
    result = CreateInteractionDefinition(
        authority=PermitAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=provenance,
    ).execute(
        CreateInteractionDefinitionCommand(
            application_id=UUID(int=1),
            source_component_id=UUID(int=source),
            destination_component_id=UUID(int=destination),
            traffic_alternatives=_traffic(port),
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key=f"definition-{source}-{destination}-{port}",
        )
    )
    assert result.outcome is TargetMutationOutcome.CREATED
    return result.interaction_definition


def _create_deployment(catalogue, identities, provenance):
    result = CreateApplicationDeployment(
        authority=PermitAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=provenance,
    ).execute(
        CreateApplicationDeploymentCommand(
            application_id=UUID(int=1),
            company_reference="Company A",
            environment="Production",
            scope_reference="Moscow",
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="deployment-1",
        )
    )
    assert result.outcome is TargetMutationOutcome.CREATED
    return result.application_deployment


def _select(catalogue, identities, provenance, deployment, definition, key):
    result = SelectDeploymentInteraction(
        authority=PermitAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=provenance,
        encoder=FakeEncoder(),
    ).execute(
        SelectDeploymentInteractionCommand(
            application_deployment_id=deployment.application_deployment_id,
            interaction_definition_id=definition.interaction_definition_id,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key=key,
        )
    )
    assert result.outcome is TargetMutationOutcome.CREATED
    return result


def test_create_interaction_definition_rejects_component_from_another_application() -> None:
    catalogue = _catalogue()
    foreign = Application(
        application_id=UUID(int=9),
        display_name="Foreign",
        provenance_reference="prov:foreign",
    )
    catalogue.applications[foreign.application_id] = foreign
    catalogue.components[UUID(int=8)] = Component(
        component_id=UUID(int=8),
        application_id=foreign.application_id,
        display_name="Foreign API",
        provenance_reference="prov:foreign-api",
    )

    result = CreateInteractionDefinition(
        authority=PermitAuthority(),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
    ).execute(
        CreateInteractionDefinitionCommand(
            application_id=UUID(int=1),
            source_component_id=UUID(int=2),
            destination_component_id=UUID(int=8),
            traffic_alternatives=_traffic(443),
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="cross-app",
        )
    )

    assert result.outcome is TargetMutationOutcome.INPUT_INVALID
    assert catalogue.interaction_definitions == {}


def test_select_interaction_creates_private_compatibility_sides_and_dcs_snapshot() -> None:
    catalogue = _catalogue()
    identities = FakeIdentities()
    provenance = FakeProvenance()
    definition = _create_definition(catalogue, identities, provenance)
    deployment = _create_deployment(catalogue, identities, provenance)

    result = _select(
        catalogue,
        identities,
        provenance,
        deployment,
        definition,
        "selection-1",
    )

    assert result.compatibility is not None
    assert result.dcs_revision is not None
    assert (
        result.compatibility.source_component_deployment_id
        != result.compatibility.destination_component_deployment_id
    )
    assert result.dcs_revision.source_component_deployment_id == (
        result.compatibility.source_component_deployment_id
    )
    assert result.dcs_revision.destination_component_deployment_id == (
        result.compatibility.destination_component_deployment_id
    )
    assert result.dcs_revision.revision_id == result.compatibility.current_dcs_revision_id
    assert catalogue.component_deployments[
        result.compatibility.source_component_deployment_id
    ].component_id == definition.source_component_id
    assert catalogue.component_deployments[
        result.compatibility.destination_component_deployment_id
    ].component_id == definition.destination_component_id


def test_two_selected_interactions_using_same_component_do_not_share_compatibility_side() -> None:
    catalogue = _catalogue()
    identities = FakeIdentities()
    provenance = FakeProvenance()
    web_to_api = _create_definition(catalogue, identities, provenance, source=2, destination=3)
    web_to_database = _create_definition(
        catalogue,
        identities,
        provenance,
        source=2,
        destination=4,
        port=5432,
    )
    deployment = _create_deployment(catalogue, identities, provenance)

    first = _select(catalogue, identities, provenance, deployment, web_to_api, "selection-1")
    second = _select(
        catalogue,
        identities,
        provenance,
        deployment,
        web_to_database,
        "selection-2",
    )

    assert first.compatibility.source_component_deployment_id != (
        second.compatibility.source_component_deployment_id
    )


def test_endpoint_edit_is_blocked_while_active_deployment_selection_exists() -> None:
    catalogue = _catalogue()
    identities = FakeIdentities()
    provenance = FakeProvenance()
    definition = _create_definition(catalogue, identities, provenance)
    deployment = _create_deployment(catalogue, identities, provenance)
    selected = _select(catalogue, identities, provenance, deployment, definition, "selection-1")

    result = UpdateInteractionDefinitionEndpoints(
        authority=PermitAuthority(),
        catalogue=catalogue,
    ).execute(
        UpdateInteractionDefinitionEndpointsCommand(
            interaction_definition_id=definition.interaction_definition_id,
            source_component_id=UUID(int=2),
            destination_component_id=UUID(int=4),
            expected_version=definition.version,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="endpoint-edit",
        )
    )

    assert result.outcome is TargetMutationOutcome.DEPENDENCY_BLOCKED
    assert result.dependencies[0].kind is TargetDependencyKind.DEPLOYMENT_INTERACTIONS
    assert result.dependencies[0].references[0].reference == str(
        selected.deployment_interaction.deployment_interaction_id
    )


def test_traffic_edit_is_blocked_by_active_downstream_reference() -> None:
    catalogue = _catalogue()
    identities = FakeIdentities()
    provenance = FakeProvenance()
    definition = _create_definition(catalogue, identities, provenance)
    deployment = _create_deployment(catalogue, identities, provenance)
    selected = _select(catalogue, identities, provenance, deployment, definition, "selection-1")
    old_revision_id = selected.compatibility.current_dcs_revision_id
    requirements = DependencyPort((ActiveDependencyReference("requirement-1"),))

    result = UpdateInteractionDefinitionTraffic(
        authority=PermitAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=provenance,
        encoder=FakeEncoder(),
        requirements=requirements,
        decisions=DependencyPort(),
        access_rules=DependencyPort(),
    ).execute(
        UpdateInteractionDefinitionTrafficCommand(
            interaction_definition_id=definition.interaction_definition_id,
            traffic_alternatives=_traffic(8443),
            expected_version=definition.version,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="traffic-edit",
        )
    )

    assert result.outcome is TargetMutationOutcome.DEPENDENCY_BLOCKED
    assert result.dependencies[0].kind is TargetDependencyKind.CONNECTIVITY_REQUIREMENTS
    assert catalogue.interaction_definitions[definition.interaction_definition_id].version == 1
    assert catalogue.compatibility[
        selected.deployment_interaction.deployment_interaction_id
    ].current_dcs_revision_id == old_revision_id
    assert len(catalogue.dcs_revisions) == 1


def test_traffic_edit_advances_dcs_snapshot_without_changing_compatibility_sides() -> None:
    catalogue = _catalogue()
    identities = FakeIdentities()
    provenance = FakeProvenance()
    definition = _create_definition(catalogue, identities, provenance)
    deployment = _create_deployment(catalogue, identities, provenance)
    selected = _select(catalogue, identities, provenance, deployment, definition, "selection-1")
    old_projection = selected.compatibility
    old_revision = selected.dcs_revision

    result = UpdateInteractionDefinitionTraffic(
        authority=PermitAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=provenance,
        encoder=FakeEncoder(),
        requirements=DependencyPort(),
        decisions=DependencyPort(),
        access_rules=DependencyPort(),
    ).execute(
        UpdateInteractionDefinitionTrafficCommand(
            interaction_definition_id=definition.interaction_definition_id,
            traffic_alternatives=_traffic(8443),
            expected_version=definition.version,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="traffic-edit",
        )
    )

    assert result.outcome is TargetMutationOutcome.UPDATED
    assert result.interaction_definition.version == 2
    assert len(result.generated_revisions) == 1
    current_projection = catalogue.compatibility[
        selected.deployment_interaction.deployment_interaction_id
    ]
    assert current_projection.source_component_deployment_id == (
        old_projection.source_component_deployment_id
    )
    assert current_projection.destination_component_deployment_id == (
        old_projection.destination_component_deployment_id
    )
    assert current_projection.current_dcs_revision_id != old_projection.current_dcs_revision_id
    assert old_revision.revision_id in catalogue.dcs_revisions
    assert current_projection.current_dcs_revision_id in catalogue.dcs_revisions
