from datetime import datetime, timezone
from uuid import UUID

from napms.application_catalogue.application.deployment_curation import (
    CreateComponentDeployment,
    CreateComponentDeploymentCommand,
    RenameComponentDeployment,
    RenameComponentDeploymentCommand,
    RetireComponentDeployment,
    RetireComponentDeploymentCommand,
)
from napms.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.application_catalogue.application.structure_curation import (
    CatalogueMutationOutcome,
)
from napms.application_catalogue.domain.model import (
    Application,
    CatalogueLifecycleState,
    Component,
    ComponentDeployment,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
APPLICATION_ID = UUID("00000000-0000-0000-0000-000000002001")
COMPONENT_ID = UUID("00000000-0000-0000-0000-000000002002")
DEPLOYMENT_ID = UUID("00000000-0000-0000-0000-000000002003")


class FakeAuthority:
    def __init__(self, outcome=ApplicationCatalogueAuthorityOutcome.PERMITTED):
        self.outcome = outcome

    def check_curation(self, **kwargs):
        return ApplicationCatalogueAuthorityCheck(
            outcome=self.outcome,
            authority_reference=(
                "auth-acc"
                if self.outcome is ApplicationCatalogueAuthorityOutcome.PERMITTED
                else None
            ),
        )


class FakeIdentities:
    def __init__(self):
        self.calls = 0

    def new_component_deployment_id(self):
        self.calls += 1
        return DEPLOYMENT_ID


class FakeProvenance:
    def __init__(self):
        self.calls = []

    def for_component_deployment(self, **kwargs):
        self.calls.append(("create", kwargs))
        return "prov:deployment:create"

    def for_component_deployment_retirement(self, **kwargs):
        self.calls.append(("retire", kwargs))
        return "prov:deployment:retire"


class FakeCatalogue:
    def __init__(self, *, application=None, component=None, deployment=None):
        application = application or Application(
            application_id=APPLICATION_ID,
            display_name="Checkout",
            provenance_reference="prov:application",
        )
        component = component or Component(
            component_id=COMPONENT_ID,
            application_id=APPLICATION_ID,
            display_name="Web",
            provenance_reference="prov:component",
        )
        self.applications = {application.application_id: application}
        self.components = {component.component_id: component}
        self.deployments = {}
        if deployment is not None:
            self.deployments[deployment.deployment_id] = deployment
        self.receipts = {}
        self.add_calls = []
        self.save_calls = []
        self.commit_count = 0

    def get_application(self, application_id):
        return self.applications.get(application_id)

    def get_component(self, component_id):
        return self.components.get(component_id)

    def get_component_deployment(self, deployment_id):
        return self.deployments.get(deployment_id)

    def add_component_deployment(self, deployment):
        self.add_calls.append(deployment)
        self.deployments[deployment.deployment_id] = deployment

    def save_component_deployment(self, deployment, *, expected_version):
        self.save_calls.append((deployment, expected_version))
        self.deployments[deployment.deployment_id] = deployment

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        self.commit_count += 1


def deployment(*, version=1):
    return ComponentDeployment(
        deployment_id=DEPLOYMENT_ID,
        component_id=COMPONENT_ID,
        provenance_reference="prov:deployment:create",
        display_name="Production",
        version=version,
    )


def create_command(*, display_name="Production", key="create-deployment"):
    return CreateComponentDeploymentCommand(
        component_id=COMPONENT_ID,
        display_name=display_name,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def test_create_deployment_requires_active_component_and_ancestor_application():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()

    result = CreateComponentDeployment(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
    ).execute(create_command())

    assert result.outcome is CatalogueMutationOutcome.CREATED
    assert result.deployment is not None
    assert result.deployment.deployment_id == DEPLOYMENT_ID
    assert result.deployment.component_id == COMPONENT_ID
    assert result.deployment.provenance_reference == "prov:deployment:create"
    assert result.deployment.lifecycle_state is CatalogueLifecycleState.ACTIVE
    assert result.deployment.version == 1
    assert identities.calls == 1
    assert catalogue.add_calls == [result.deployment]
    assert catalogue.commit_count == 1


def test_create_deployment_rejects_retired_component_before_identity_allocation():
    retired_component = Component(
        component_id=COMPONENT_ID,
        application_id=APPLICATION_ID,
        display_name="Web",
        provenance_reference="prov:component",
        lifecycle_state=CatalogueLifecycleState.RETIRED,
        retirement_provenance_reference="prov:component:retire",
    )
    catalogue = FakeCatalogue(component=retired_component)
    identities = FakeIdentities()

    result = CreateComponentDeployment(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
    ).execute(create_command())

    assert result.outcome is CatalogueMutationOutcome.PARENT_INACTIVE
    assert identities.calls == 0
    assert catalogue.add_calls == []
    assert catalogue.commit_count == 0


def test_create_deployment_rejects_retired_ancestor_application():
    retired_application = Application(
        application_id=APPLICATION_ID,
        display_name="Checkout",
        provenance_reference="prov:application",
        lifecycle_state=CatalogueLifecycleState.RETIRED,
        retirement_provenance_reference="prov:application:retire",
    )
    catalogue = FakeCatalogue(application=retired_application)

    result = CreateComponentDeployment(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
    ).execute(create_command())

    assert result.outcome is CatalogueMutationOutcome.PARENT_INACTIVE
    assert catalogue.add_calls == []


def test_create_deployment_retry_is_resolved_without_duplicate_identity():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()
    use_case = CreateComponentDeployment(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
    )

    first = use_case.execute(create_command(key="same-key"))
    second = use_case.execute(create_command(key="same-key"))

    assert first.outcome is CatalogueMutationOutcome.CREATED
    assert second.outcome is CatalogueMutationOutcome.RESOLVED
    assert second.deployment == first.deployment
    assert identities.calls == 1
    assert catalogue.commit_count == 1


def test_rename_deployment_can_clear_optional_display_name_and_uses_expected_version():
    catalogue = FakeCatalogue(deployment=deployment())

    result = RenameComponentDeployment(
        authority=FakeAuthority(),
        catalogue=catalogue,
    ).execute(
        RenameComponentDeploymentCommand(
            deployment_id=DEPLOYMENT_ID,
            display_name=None,
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="rename-deployment",
        )
    )

    assert result.outcome is CatalogueMutationOutcome.UPDATED
    assert result.deployment is not None
    assert result.deployment.component_id == COMPONENT_ID
    assert result.deployment.display_name is None
    assert result.deployment.version == 2
    assert catalogue.save_calls == [(result.deployment, 1)]


def test_rename_deployment_rejects_stale_version_without_write():
    catalogue = FakeCatalogue(deployment=deployment(version=2))

    result = RenameComponentDeployment(
        authority=FakeAuthority(),
        catalogue=catalogue,
    ).execute(
        RenameComponentDeploymentCommand(
            deployment_id=DEPLOYMENT_ID,
            display_name="New label",
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="stale-rename",
        )
    )

    assert result.outcome is CatalogueMutationOutcome.CONCURRENCY_CONFLICT
    assert catalogue.save_calls == []
    assert catalogue.commit_count == 0


def test_retire_deployment_preserves_parent_and_records_retirement_provenance():
    catalogue = FakeCatalogue(deployment=deployment())
    provenance = FakeProvenance()

    result = RetireComponentDeployment(
        authority=FakeAuthority(),
        catalogue=catalogue,
        provenance=provenance,
    ).execute(
        RetireComponentDeploymentCommand(
            deployment_id=DEPLOYMENT_ID,
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="retire-deployment",
        )
    )

    assert result.outcome is CatalogueMutationOutcome.UPDATED
    assert result.deployment is not None
    assert result.deployment.component_id == COMPONENT_ID
    assert result.deployment.lifecycle_state is CatalogueLifecycleState.RETIRED
    assert result.deployment.retirement_provenance_reference == "prov:deployment:retire"
    assert result.deployment.version == 2
    assert catalogue.save_calls == [(result.deployment, 1)]
    assert catalogue.commit_count == 1


def test_authority_denial_performs_no_repository_write():
    catalogue = FakeCatalogue()

    result = CreateComponentDeployment(
        authority=FakeAuthority(ApplicationCatalogueAuthorityOutcome.DENIED),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
    ).execute(create_command())

    assert result.outcome is CatalogueMutationOutcome.AUTHORITY_DENIED
    assert catalogue.add_calls == []
    assert catalogue.save_calls == []
    assert catalogue.commit_count == 0
