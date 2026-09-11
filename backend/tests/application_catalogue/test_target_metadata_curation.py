from datetime import datetime, timezone
from uuid import UUID

from napms.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.application_catalogue.application.target_curation import TargetMutationOutcome
from napms.application_catalogue.application.target_metadata_curation import (
    UpdateApplicationDefinitionMetadata,
    UpdateApplicationDefinitionMetadataCommand,
    UpdateApplicationDeploymentContext,
    UpdateApplicationDeploymentContextCommand,
    UpdateComponentMetadata,
    UpdateComponentMetadataCommand,
)
from napms.application_catalogue.domain.model import Application, Component
from napms.application_catalogue.domain.target_model import ApplicationDeployment


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


class PermitAuthority:
    def check_curation(self, *, actor_id, effective_time):
        return ApplicationCatalogueAuthorityCheck(
            ApplicationCatalogueAuthorityOutcome.PERMITTED,
            authority_reference="authority:catalogue",
        )


class FakeCatalogue:
    def __init__(self):
        self.application = Application(UUID(int=1), "CRM", "prov:app")
        self.component = Component(UUID(int=2), UUID(int=1), "API", "prov:component")
        self.deployment = ApplicationDeployment(
            application_deployment_id=UUID(int=3),
            application_id=UUID(int=1),
            company_reference="Company A",
            environment="Production",
            scope_reference="Moscow",
            provenance_reference="prov:deployment",
        )
        self.receipts = {}

    def get_application(self, application_id):
        return self.application if application_id == self.application.application_id else None

    def save_application(self, value, *, expected_version):
        assert self.application.version == expected_version
        self.application = value

    def get_component(self, component_id):
        return self.component if component_id == self.component.component_id else None

    def save_component(self, value, *, expected_version):
        assert self.component.version == expected_version
        self.component = value

    def get_application_deployment(self, application_deployment_id):
        return (
            self.deployment
            if application_deployment_id == self.deployment.application_deployment_id
            else None
        )

    def save_application_deployment(self, value, *, expected_version):
        assert self.deployment.version == expected_version
        self.deployment = value

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        pass


def test_application_metadata_is_mutable_without_changing_identity_and_replays() -> None:
    catalogue = FakeCatalogue()
    service = UpdateApplicationDefinitionMetadata(
        authority=PermitAuthority(),
        catalogue=catalogue,
    )
    command = UpdateApplicationDefinitionMetadataCommand(
        application_id=UUID(int=1),
        display_name="CRM Platform",
        description="Customer relationship platform",
        domain="Sales",
        owner_reference="team:crm",
        expected_version=1,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key="metadata-1",
    )

    first = service.execute(command)
    replay = service.execute(command)

    assert first.outcome is TargetMutationOutcome.UPDATED
    assert replay.outcome is TargetMutationOutcome.RESOLVED
    assert catalogue.application.application_id == UUID(int=1)
    assert catalogue.application.display_name == "CRM Platform"
    assert catalogue.application.domain == "Sales"
    assert catalogue.application.owner_reference == "team:crm"
    assert catalogue.application.version == 2


def test_component_type_is_open_descriptive_metadata() -> None:
    catalogue = FakeCatalogue()
    result = UpdateComponentMetadata(
        authority=PermitAuthority(),
        catalogue=catalogue,
    ).execute(
        UpdateComponentMetadataCommand(
            component_id=UUID(int=2),
            display_name="CRM API",
            component_type="Domain-specific custom type",
            description="Public service facade",
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="component-metadata-1",
        )
    )

    assert result.outcome is TargetMutationOutcome.UPDATED
    assert catalogue.component.component_type == "Domain-specific custom type"
    assert catalogue.component.version == 2


def test_deployment_context_correction_preserves_deployment_identity() -> None:
    catalogue = FakeCatalogue()
    result = UpdateApplicationDeploymentContext(
        authority=PermitAuthority(),
        catalogue=catalogue,
    ).execute(
        UpdateApplicationDeploymentContextCommand(
            application_deployment_id=UUID(int=3),
            company_reference="Company B",
            environment="Test",
            scope_reference="SPb",
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="deployment-context-1",
        )
    )

    assert result.outcome is TargetMutationOutcome.UPDATED
    assert catalogue.deployment.application_deployment_id == UUID(int=3)
    assert catalogue.deployment.company_reference == "Company B"
    assert catalogue.deployment.environment == "Test"
    assert catalogue.deployment.scope_reference == "SPb"
    assert catalogue.deployment.version == 2


def test_new_metadata_fields_do_not_shift_legacy_positional_lifecycle_arguments() -> None:
    from napms.application_catalogue.domain.model import CatalogueLifecycleState

    application = Application(
        UUID(int=10),
        "Legacy",
        "prov",
        CatalogueLifecycleState.RETIRED,
        "prov:retire",
        2,
    )
    component = Component(
        UUID(int=11),
        UUID(int=10),
        "Legacy component",
        "prov",
        CatalogueLifecycleState.RETIRED,
        "prov:retire",
        3,
    )

    assert application.lifecycle_state is CatalogueLifecycleState.RETIRED
    assert application.version == 2
    assert application.description is None
    assert component.lifecycle_state is CatalogueLifecycleState.RETIRED
    assert component.version == 3
    assert component.component_type is None
