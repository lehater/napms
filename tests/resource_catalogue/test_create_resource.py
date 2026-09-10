from datetime import datetime, timezone

from napms.resource_catalogue.application.curation import (
    CreateResource,
    CreateResourceCommand,
    CreateResourceOutcome,
)
from napms.resource_catalogue.application.ports import (
    ResourceCatalogueAuthorityCheck,
    ResourceCatalogueAuthorityOutcome,
)


NOW = datetime(2026, 9, 10, 11, 0, tzinfo=timezone.utc)


class FakeAuthority:
    def __init__(self, outcome=ResourceCatalogueAuthorityOutcome.PERMITTED):
        self.outcome = outcome
        self.calls = []

    def check_curation(self, **kwargs):
        self.calls.append(kwargs)
        return ResourceCatalogueAuthorityCheck(
            outcome=self.outcome,
            authority_reference=(
                "auth-rc" if self.outcome is ResourceCatalogueAuthorityOutcome.PERMITTED else None
            ),
        )


class FakeResources:
    def __init__(self):
        self.items = {}
        self.receipts = {}
        self.add_calls = []
        self.commit_count = 0

    def get_resource(self, resource_reference):
        return self.items.get(resource_reference)

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def add_resource(self, resource):
        self.add_calls.append(resource)
        self.items[resource.resource_reference] = resource

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        self.commit_count += 1


class FakeIdentities:
    def __init__(self):
        self.count = 0

    def new_resource_reference(self):
        self.count += 1
        return "resource:generated:1"


class FakeProvenance:
    def __init__(self):
        self.calls = []

    def for_resource(self, **kwargs):
        self.calls.append(kwargs)
        return "local:curation:resource"


def service(*, authority=None, resources=None, identities=None, provenance=None):
    authority = authority or FakeAuthority()
    resources = resources or FakeResources()
    identities = identities or FakeIdentities()
    provenance = provenance or FakeProvenance()
    return (
        CreateResource(
            authority=authority,
            resources=resources,
            identities=identities,
            provenance=provenance,
        ),
        authority,
        resources,
        identities,
        provenance,
    )


def command(*, display_name="Orders production", key="cmd-1"):
    return CreateResourceCommand(
        display_name=display_name,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def test_create_resource_uses_server_reference_and_provenance():
    use_case, authority, resources, identities, provenance = service()

    result = use_case.execute(command(display_name="  Orders production  "))

    assert result.outcome is CreateResourceOutcome.CREATED
    assert result.resource is not None
    assert result.resource.resource_reference == "resource:generated:1"
    assert result.resource.display_name == "Orders production"
    assert result.resource.provenance_reference == "local:curation:resource"
    assert identities.count == 1
    assert provenance.calls == [
        {
            "resource_reference": "resource:generated:1",
            "actor_id": "actor-1",
            "authority_reference": "auth-rc",
            "effective_time": NOW,
        }
    ]
    assert resources.commit_count == 1
    assert authority.calls == [{"actor_id": "actor-1", "effective_time": NOW}]


def test_resource_display_name_is_optional_but_blank_is_invalid():
    use_case, _, resources, identities, _ = service()

    unnamed = use_case.execute(command(display_name=None, key="none"))
    blank = use_case.execute(command(display_name="   ", key="blank"))

    assert unnamed.outcome is CreateResourceOutcome.CREATED
    assert unnamed.resource is not None
    assert unnamed.resource.display_name is None
    assert blank.outcome is CreateResourceOutcome.INPUT_INVALID
    assert len(resources.add_calls) == 1
    assert identities.count == 1


def test_denied_authority_has_no_write_or_reference_allocation():
    use_case, _, resources, identities, provenance = service(
        authority=FakeAuthority(ResourceCatalogueAuthorityOutcome.DENIED)
    )

    result = use_case.execute(command())

    assert result.outcome is CreateResourceOutcome.AUTHORITY_DENIED
    assert resources.add_calls == []
    assert resources.commit_count == 0
    assert identities.count == 0
    assert provenance.calls == []


def test_equivalent_retry_returns_original_resource_without_second_write():
    use_case, _, resources, identities, _ = service()

    first = use_case.execute(command(display_name="Orders production", key="same-key"))
    second = use_case.execute(command(display_name=" Orders production ", key="same-key"))

    assert first.outcome is CreateResourceOutcome.CREATED
    assert second.outcome is CreateResourceOutcome.RESOLVED
    assert second.resource is not None
    assert second.resource.resource_reference == "resource:generated:1"
    assert len(resources.add_calls) == 1
    assert resources.commit_count == 1
    assert identities.count == 1


def test_same_idempotency_key_with_different_semantics_conflicts():
    use_case, _, resources, identities, _ = service()

    first = use_case.execute(command(display_name="Orders", key="same-key"))
    second = use_case.execute(command(display_name="Payments", key="same-key"))

    assert first.outcome is CreateResourceOutcome.CREATED
    assert second.outcome is CreateResourceOutcome.IDEMPOTENCY_CONFLICT
    assert len(resources.add_calls) == 1
    assert identities.count == 1
