from datetime import datetime, timedelta, timezone
from uuid import UUID

from napms.contexts.application_catalogue.application.binding_curation import (
    BindingTargetOutcome,
    CreateDeploymentResourceBinding,
    CreateDeploymentResourceBindingCommand,
    EndDeploymentResourceBinding,
    EndDeploymentResourceBindingCommand,
)
from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.contexts.application_catalogue.application.structure_curation import (
    CatalogueMutationOutcome,
)
from napms.contexts.application_catalogue.domain.model import (
    CatalogueLifecycleState,
    ComponentDeployment,
    DeploymentResourceBinding,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
START = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)
END = START + timedelta(days=1)
DEPLOYMENT_ID = UUID("00000000-0000-0000-0000-000000004001")
COMPONENT_ID = UUID("00000000-0000-0000-0000-000000004002")


class FakeAuthority:
    def check_curation(self, **kwargs):
        return ApplicationCatalogueAuthorityCheck(
            outcome=ApplicationCatalogueAuthorityOutcome.PERMITTED,
            authority_reference="auth-acc",
        )


class FakeTargets:
    def __init__(self, outcome=BindingTargetOutcome.ACTIVE):
        self.outcome = outcome
        self.calls = []

    def check_target(self, **kwargs):
        self.calls.append(kwargs)
        return self.outcome


class FakeIdentities:
    def __init__(self):
        self.calls = 0

    def new_binding_reference(self):
        self.calls += 1
        return "binding-generated"


class FakeProvenance:
    def for_binding(self, **kwargs):
        return "prov:binding:create"

    def for_binding_end(self, **kwargs):
        return "prov:binding:end"


class FakeCatalogue:
    def __init__(self, *, deployment=None):
        deployment = deployment or ComponentDeployment(
            deployment_id=DEPLOYMENT_ID,
            component_id=COMPONENT_ID,
            provenance_reference="prov:deployment",
        )
        self.deployments = {deployment.deployment_id: deployment}
        self.bindings = {}
        self.receipts = {}
        self.overlapping = ()
        self.overlap_calls = []
        self.add_calls = []
        self.save_calls = []
        self.commit_count = 0

    def get_component_deployment(self, deployment_id):
        return self.deployments.get(deployment_id)

    def get_binding(self, reference_id):
        return self.bindings.get(reference_id)

    def find_overlapping_bindings(self, **kwargs):
        self.overlap_calls.append(kwargs)
        return self.overlapping

    def add_binding(self, binding):
        self.add_calls.append(binding)
        self.bindings[binding.reference_id] = binding

    def save_binding(self, binding, *, expected_version):
        self.save_calls.append((binding, expected_version))
        self.bindings[binding.reference_id] = binding

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        self.commit_count += 1


def create_command(*, resource="resource-a", key="create-binding"):
    return CreateDeploymentResourceBindingCommand(
        component_deployment_id=DEPLOYMENT_ID,
        resource_reference=resource,
        valid_from=START,
        valid_to=None,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def open_binding():
    return DeploymentResourceBinding(
        reference_id="binding-1",
        component_deployment_id=DEPLOYMENT_ID,
        resource_reference="resource-a",
        valid_from=START,
        valid_to=None,
        provenance_reference="prov:binding:create",
    )


def use_case(catalogue, *, targets=None, identities=None):
    return CreateDeploymentResourceBinding(
        authority=FakeAuthority(),
        catalogue=catalogue,
        resources=targets or FakeTargets(),
        identities=identities or FakeIdentities(),
        provenance=FakeProvenance(),
    )


def test_create_binding_uses_pair_specific_overlap_and_server_owned_identity():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()

    result = use_case(catalogue, identities=identities).execute(create_command())

    assert result.outcome is CatalogueMutationOutcome.CREATED
    assert result.binding is not None
    assert result.binding.reference_id == "binding-generated"
    assert result.binding.component_deployment_id == DEPLOYMENT_ID
    assert result.binding.resource_reference == "resource-a"
    assert result.binding.provenance_reference == "prov:binding:create"
    assert result.binding.version == 1
    assert catalogue.overlap_calls == [
        {
            "component_deployment_id": DEPLOYMENT_ID,
            "resource_reference": "resource-a",
            "valid_from": START,
            "valid_to": None,
        }
    ]
    assert identities.calls == 1
    assert catalogue.commit_count == 1


def test_different_resource_is_not_rejected_by_unrelated_existing_binding():
    catalogue = FakeCatalogue()
    catalogue.bindings["existing"] = DeploymentResourceBinding(
        reference_id="existing",
        component_deployment_id=DEPLOYMENT_ID,
        resource_reference="resource-a",
        valid_from=START,
        valid_to=None,
        provenance_reference="prov:existing",
    )

    result = use_case(catalogue).execute(
        create_command(resource="resource-b", key="resource-b")
    )

    assert result.outcome is CatalogueMutationOutcome.CREATED
    assert catalogue.overlap_calls[0]["resource_reference"] == "resource-b"


def test_same_pair_overlap_is_rejected_before_identity_allocation():
    catalogue = FakeCatalogue()
    catalogue.overlapping = (open_binding(),)
    identities = FakeIdentities()

    result = use_case(catalogue, identities=identities).execute(create_command())

    assert result.outcome is CatalogueMutationOutcome.INPUT_INVALID
    assert identities.calls == 0
    assert catalogue.add_calls == []
    assert catalogue.commit_count == 0


def test_new_binding_requires_active_deployment_and_active_resource_target():
    retired = ComponentDeployment(
        deployment_id=DEPLOYMENT_ID,
        component_id=COMPONENT_ID,
        provenance_reference="prov:deployment",
        lifecycle_state=CatalogueLifecycleState.RETIRED,
        retirement_provenance_reference="prov:deployment:retire",
    )
    inactive_catalogue = FakeCatalogue(deployment=retired)
    target = FakeTargets(BindingTargetOutcome.ACTIVE)

    deployment_result = use_case(inactive_catalogue, targets=target).execute(
        create_command(key="retired-deployment")
    )

    active_catalogue = FakeCatalogue()
    resource_result = use_case(
        active_catalogue,
        targets=FakeTargets(BindingTargetOutcome.INACTIVE),
    ).execute(create_command(key="retired-resource"))

    assert deployment_result.outcome is CatalogueMutationOutcome.PARENT_INACTIVE
    assert target.calls == []
    assert resource_result.outcome is CatalogueMutationOutcome.PARENT_INACTIVE
    assert active_catalogue.add_calls == []


def test_unknown_resource_target_fails_closed():
    catalogue = FakeCatalogue()

    result = use_case(
        catalogue,
        targets=FakeTargets(BindingTargetOutcome.UNKNOWN),
    ).execute(create_command())

    assert result.outcome is CatalogueMutationOutcome.PERSISTENCE_UNKNOWN
    assert catalogue.add_calls == []
    assert catalogue.commit_count == 0


def test_invalid_interval_is_rejected_before_target_and_overlap_queries():
    catalogue = FakeCatalogue()
    targets = FakeTargets()
    invalid = CreateDeploymentResourceBindingCommand(
        component_deployment_id=DEPLOYMENT_ID,
        resource_reference="resource-a",
        valid_from=START.replace(tzinfo=None),
        valid_to=None,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key="invalid-time",
    )

    result = use_case(catalogue, targets=targets).execute(invalid)

    assert result.outcome is CatalogueMutationOutcome.INPUT_INVALID
    assert targets.calls == []
    assert catalogue.overlap_calls == []


def test_create_binding_retry_resolves_without_duplicate_write():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()
    creator = use_case(catalogue, identities=identities)

    first = creator.execute(create_command(key="same-key"))
    second = creator.execute(create_command(key="same-key"))

    assert first.outcome is CatalogueMutationOutcome.CREATED
    assert second.outcome is CatalogueMutationOutcome.RESOLVED
    assert second.binding == first.binding
    assert identities.calls == 1
    assert catalogue.commit_count == 1


def test_end_binding_preserves_creation_provenance_and_records_end_provenance():
    catalogue = FakeCatalogue()
    current = open_binding()
    catalogue.bindings[current.reference_id] = current

    result = EndDeploymentResourceBinding(
        authority=FakeAuthority(),
        catalogue=catalogue,
        provenance=FakeProvenance(),
    ).execute(
        EndDeploymentResourceBindingCommand(
            binding_reference="binding-1",
            valid_to=END,
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="end-binding",
        )
    )

    assert result.outcome is CatalogueMutationOutcome.UPDATED
    assert result.binding is not None
    assert result.binding.provenance_reference == "prov:binding:create"
    assert result.binding.end_provenance_reference == "prov:binding:end"
    assert result.binding.valid_to == END
    assert result.binding.version == 2
    assert catalogue.save_calls == [(result.binding, 1)]
    assert catalogue.commit_count == 1


def test_end_binding_rejects_stale_version_without_write():
    catalogue = FakeCatalogue()
    current = open_binding()
    catalogue.bindings[current.reference_id] = current.ended(
        valid_to=END,
        end_provenance_reference="prov:old-end",
    )

    result = EndDeploymentResourceBinding(
        authority=FakeAuthority(),
        catalogue=catalogue,
        provenance=FakeProvenance(),
    ).execute(
        EndDeploymentResourceBindingCommand(
            binding_reference="binding-1",
            valid_to=END + timedelta(days=1),
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="stale-end",
        )
    )

    assert result.outcome is CatalogueMutationOutcome.CONCURRENCY_CONFLICT
    assert catalogue.save_calls == []
    assert catalogue.commit_count == 0
