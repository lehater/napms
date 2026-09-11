from datetime import datetime, timezone
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.contexts.application_catalogue.application.curation.application_structure import (
    RenameApplication,
    RenameApplicationCommand,
    RetireApplication,
    RetireApplicationCommand,
)
from napms.contexts.application_catalogue.application.curation.component_structure import (
    CreateComponent,
    CreateComponentCommand,
    RetireComponent,
    RetireComponentCommand,
)
from napms.contexts.application_catalogue.application.ports import CatalogueMutationOutcome
from napms.contexts.application_catalogue.domain.model import (
    Application,
    CatalogueLifecycleState,
    Component,
)


NOW = datetime(2026, 9, 10, 13, 0, tzinfo=timezone.utc)
APPLICATION_ID = UUID("00000000-0000-0000-0000-000000003001")
COMPONENT_ID = UUID("00000000-0000-0000-0000-000000003002")


class FakeAuthority:
    def __init__(self, outcome=ApplicationCatalogueAuthorityOutcome.PERMITTED):
        self.outcome = outcome
        self.calls = []

    def check_curation(self, **kwargs):
        self.calls.append(kwargs)
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
        self.component_count = 0

    def new_component_id(self):
        self.component_count += 1
        return COMPONENT_ID


class FakeProvenance:
    def __init__(self):
        self.calls = []

    def for_component(self, **kwargs):
        self.calls.append(("component", kwargs))
        return "prov:component:create"

    def for_application_retirement(self, **kwargs):
        self.calls.append(("application-retirement", kwargs))
        return "prov:application:retirement"

    def for_component_retirement(self, **kwargs):
        self.calls.append(("component-retirement", kwargs))
        return "prov:component:retirement"


class FakeCatalogue:
    def __init__(self, application=None):
        application = application or Application(
            application_id=APPLICATION_ID,
            display_name="Checkout",
            provenance_reference="prov:application:create",
        )
        self.applications = {application.application_id: application}
        self.components = {}
        self.receipts = {}
        self.active_components = False
        self.active_deployments = False
        self.application_saves = []
        self.component_saves = []
        self.component_adds = []
        self.commit_count = 0

    def get_application(self, application_id):
        return self.applications.get(application_id)

    def add_application(self, application):
        self.applications[application.application_id] = application

    def save_application(self, application, *, expected_version):
        self.application_saves.append((application, expected_version))
        self.applications[application.application_id] = application

    def has_active_components(self, *, application_id):
        return self.active_components

    def get_component(self, component_id):
        return self.components.get(component_id)

    def add_component(self, component):
        self.component_adds.append(component)
        self.components[component.component_id] = component

    def save_component(self, component, *, expected_version):
        self.component_saves.append((component, expected_version))
        self.components[component.component_id] = component

    def has_active_component_deployments(self, *, component_id):
        return self.active_deployments

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        self.commit_count += 1


def create_component_command(*, key="component-create"):
    return CreateComponentCommand(
        application_id=APPLICATION_ID,
        display_name="Web",
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def test_create_component_requires_active_parent_and_preserves_parent_identity():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()
    provenance = FakeProvenance()

    result = CreateComponent(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=provenance,
    ).execute(create_component_command())

    assert result.outcome is CatalogueMutationOutcome.CREATED
    assert result.component is not None
    assert result.component.component_id == COMPONENT_ID
    assert result.component.application_id == APPLICATION_ID
    assert result.component.provenance_reference == "prov:component:create"
    assert identities.component_count == 1
    assert catalogue.commit_count == 1


def test_create_component_rejects_retired_parent_before_identity_allocation():
    retired_application = Application(
        application_id=APPLICATION_ID,
        display_name="Checkout",
        provenance_reference="prov:application:create",
        lifecycle_state=CatalogueLifecycleState.RETIRED,
        retirement_provenance_reference="prov:application:retirement",
        version=2,
    )
    catalogue = FakeCatalogue(application=retired_application)
    identities = FakeIdentities()

    result = CreateComponent(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
    ).execute(create_component_command())

    assert result.outcome is CatalogueMutationOutcome.PARENT_INACTIVE
    assert identities.component_count == 0
    assert catalogue.component_adds == []


def test_component_create_retry_resolves_original_identity():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()
    use_case = CreateComponent(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
    )

    first = use_case.execute(create_component_command(key="same-key"))
    second = use_case.execute(create_component_command(key="same-key"))

    assert first.outcome is CatalogueMutationOutcome.CREATED
    assert second.outcome is CatalogueMutationOutcome.RESOLVED
    assert second.component is not None
    assert second.component.component_id == COMPONENT_ID
    assert identities.component_count == 1
    assert len(catalogue.component_adds) == 1


def test_rename_application_uses_expected_version():
    catalogue = FakeCatalogue()

    result = RenameApplication(
        authority=FakeAuthority(),
        catalogue=catalogue,
    ).execute(
        RenameApplicationCommand(
            application_id=APPLICATION_ID,
            display_name="Checkout Platform",
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="rename-app",
        )
    )

    assert result.outcome is CatalogueMutationOutcome.UPDATED
    assert result.application is not None
    assert result.application.display_name == "Checkout Platform"
    assert result.application.version == 2
    assert catalogue.application_saves == [(result.application, 1)]


def test_retire_application_is_blocked_by_active_components_before_provenance():
    catalogue = FakeCatalogue()
    catalogue.active_components = True
    provenance = FakeProvenance()

    result = RetireApplication(
        authority=FakeAuthority(),
        catalogue=catalogue,
        provenance=provenance,
    ).execute(
        RetireApplicationCommand(
            application_id=APPLICATION_ID,
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="retire-app",
        )
    )

    assert result.outcome is CatalogueMutationOutcome.RETIREMENT_BLOCKED
    assert catalogue.application_saves == []
    assert provenance.calls == []


def test_retire_application_records_transition_provenance():
    catalogue = FakeCatalogue()
    provenance = FakeProvenance()

    result = RetireApplication(
        authority=FakeAuthority(),
        catalogue=catalogue,
        provenance=provenance,
    ).execute(
        RetireApplicationCommand(
            application_id=APPLICATION_ID,
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="retire-app",
        )
    )

    assert result.outcome is CatalogueMutationOutcome.UPDATED
    assert result.application is not None
    assert result.application.lifecycle_state is CatalogueLifecycleState.RETIRED
    assert result.application.retirement_provenance_reference == "prov:application:retirement"
    assert result.application.version == 2


def test_retire_component_is_blocked_by_active_deployments():
    catalogue = FakeCatalogue()
    catalogue.components[COMPONENT_ID] = Component(
        component_id=COMPONENT_ID,
        application_id=APPLICATION_ID,
        display_name="Web",
        provenance_reference="prov:component:create",
    )
    catalogue.active_deployments = True
    provenance = FakeProvenance()

    result = RetireComponent(
        authority=FakeAuthority(),
        catalogue=catalogue,
        provenance=provenance,
    ).execute(
        RetireComponentCommand(
            component_id=COMPONENT_ID,
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="retire-component",
        )
    )

    assert result.outcome is CatalogueMutationOutcome.RETIREMENT_BLOCKED
    assert catalogue.component_saves == []
    assert provenance.calls == []


def test_retire_component_records_transition_provenance_and_preserves_parent():
    catalogue = FakeCatalogue()
    catalogue.components[COMPONENT_ID] = Component(
        component_id=COMPONENT_ID,
        application_id=APPLICATION_ID,
        display_name="Web",
        provenance_reference="prov:component:create",
    )
    provenance = FakeProvenance()

    result = RetireComponent(
        authority=FakeAuthority(),
        catalogue=catalogue,
        provenance=provenance,
    ).execute(
        RetireComponentCommand(
            component_id=COMPONENT_ID,
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="retire-component",
        )
    )

    assert result.outcome is CatalogueMutationOutcome.UPDATED
    assert result.component is not None
    assert result.component.application_id == APPLICATION_ID
    assert result.component.lifecycle_state is CatalogueLifecycleState.RETIRED
    assert result.component.retirement_provenance_reference == "prov:component:retirement"
    assert result.component.version == 2
