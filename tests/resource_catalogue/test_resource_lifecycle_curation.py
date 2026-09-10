from datetime import datetime, timezone

from napms.resource_catalogue.application.curation import (
    RenameResource,
    RenameResourceCommand,
    ResourceMutationOutcome,
    RetireResource,
    RetireResourceCommand,
)
from napms.resource_catalogue.application.ports import (
    ResourceCatalogueAuthorityCheck,
    ResourceCatalogueAuthorityOutcome,
)
from napms.resource_catalogue.domain.model import Resource, ResourceLifecycleState


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)


class FakeAuthority:
    def __init__(self, outcome=ResourceCatalogueAuthorityOutcome.PERMITTED):
        self.outcome = outcome

    def check_curation(self, **kwargs):
        return ResourceCatalogueAuthorityCheck(
            outcome=self.outcome,
            authority_reference=(
                "auth-rc"
                if self.outcome is ResourceCatalogueAuthorityOutcome.PERMITTED
                else None
            ),
        )


class FakeResources:
    def __init__(self, resource, *, affiliations=False, responsibilities=False):
        self.items = {resource.resource_reference: resource}
        self.receipts = {}
        self.affiliations = affiliations
        self.responsibilities = responsibilities
        self.save_calls = []
        self.commit_count = 0

    def get_resource(self, resource_reference):
        return self.items.get(resource_reference)

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def add_resource(self, resource):
        raise AssertionError("not used by lifecycle tests")

    def save_resource(self, resource, *, expected_version):
        self.save_calls.append((resource, expected_version))
        self.items[resource.resource_reference] = resource

    def has_effective_scope_affiliations(self, *, resource_reference, as_of):
        return self.affiliations

    def has_effective_responsibilities(self, *, resource_reference, as_of):
        return self.responsibilities

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        self.commit_count += 1


def resource(*, version=1):
    return Resource(
        resource_reference="res-1",
        display_name="Orders",
        provenance_reference="test:resource",
        version=version,
    )


def rename_command(*, version=1, name="Orders production", key="rename-1"):
    return RenameResourceCommand(
        resource_reference="res-1",
        display_name=name,
        expected_version=version,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def retire_command(*, version=1, key="retire-1"):
    return RetireResourceCommand(
        resource_reference="res-1",
        expected_version=version,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def test_rename_resource_preserves_identity_and_uses_expected_version():
    repo = FakeResources(resource())

    result = RenameResource(
        authority=FakeAuthority(),
        resources=repo,
    ).execute(rename_command())

    assert result.outcome is ResourceMutationOutcome.UPDATED
    assert result.resource is not None
    assert result.resource.resource_reference == "res-1"
    assert result.resource.display_name == "Orders production"
    assert result.resource.version == 2
    assert repo.save_calls == [(result.resource, 1)]
    assert repo.commit_count == 1


def test_rename_resource_rejects_stale_version_before_write():
    repo = FakeResources(resource(version=2))

    result = RenameResource(
        authority=FakeAuthority(),
        resources=repo,
    ).execute(rename_command(version=1))

    assert result.outcome is ResourceMutationOutcome.CONCURRENCY_CONFLICT
    assert repo.save_calls == []
    assert repo.commit_count == 0


def test_rename_retry_is_resolved_without_second_mutation():
    repo = FakeResources(resource())
    use_case = RenameResource(authority=FakeAuthority(), resources=repo)

    first = use_case.execute(rename_command(key="same-key"))
    second = use_case.execute(rename_command(key="same-key"))

    assert first.outcome is ResourceMutationOutcome.UPDATED
    assert second.outcome is ResourceMutationOutcome.RESOLVED
    assert len(repo.save_calls) == 1
    assert repo.commit_count == 1


def test_retire_resource_is_blocked_by_current_scope_or_responsibility_facts():
    for affiliations, responsibilities in ((True, False), (False, True)):
        repo = FakeResources(
            resource(),
            affiliations=affiliations,
            responsibilities=responsibilities,
        )

        result = RetireResource(
            authority=FakeAuthority(),
            resources=repo,
        ).execute(retire_command(key=f"retire-{affiliations}-{responsibilities}"))

        assert result.outcome is ResourceMutationOutcome.RETIREMENT_BLOCKED
        assert repo.save_calls == []
        assert repo.commit_count == 0


def test_retire_resource_preserves_historical_identity():
    repo = FakeResources(resource())

    result = RetireResource(
        authority=FakeAuthority(),
        resources=repo,
    ).execute(retire_command())

    assert result.outcome is ResourceMutationOutcome.UPDATED
    assert result.resource is not None
    assert result.resource.resource_reference == "res-1"
    assert result.resource.lifecycle_state is ResourceLifecycleState.RETIRED
    assert result.resource.version == 2
    assert repo.save_calls == [(result.resource, 1)]
