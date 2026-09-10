from datetime import datetime, timezone

from napms.resource_catalogue.application._temporal_curation import TemporalCurationOutcome
from napms.resource_catalogue.application.ports import (
    ResourceCatalogueAuthorityCheck,
    ResourceCatalogueAuthorityOutcome,
)
from napms.resource_catalogue.application.realization_curation import (
    CreateResourceRealization,
    CreateResourceRealizationCommand,
    ReplaceResourceRealization,
    ReplaceResourceRealizationCommand,
)
from napms.resource_catalogue.domain.model import (
    EndpointAddress,
    Resource,
    ResourceRealizationVersion,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
START = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)
REPLACEMENT = datetime(2026, 9, 11, 8, 0, tzinfo=timezone.utc)


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


class FakeIdentities:
    def __init__(self):
        self.fact_count = 0
        self.endpoint_count = 0

    def new_realization_reference(self):
        self.fact_count += 1
        return f"realization-{self.fact_count}"

    def new_endpoint_reference(self):
        self.endpoint_count += 1
        return f"endpoint-{self.endpoint_count}"


class FakeProvenance:
    def for_realization(self, **kwargs):
        return f"prov:create:{kwargs['fact_reference']}"

    def for_realization_end(self, **kwargs):
        return f"prov:end:{kwargs['fact_reference']}"


class FakeCatalogue:
    def __init__(self):
        self.resources = {
            "res-1": Resource(
                resource_reference="res-1",
                display_name="Orders",
                provenance_reference="prov:resource",
            )
        }
        self.realizations = {}
        self.receipts = {}
        self.overlap_rows = ()
        self.overlap_calls = []
        self.add_calls = []
        self.save_calls = []
        self.commit_count = 0

    def get_resource(self, resource_reference):
        return self.resources.get(resource_reference)

    def get_realization(self, fact_reference):
        return self.realizations.get(fact_reference)

    def find_overlapping_realizations(self, **kwargs):
        self.overlap_calls.append(kwargs)
        return self.overlap_rows

    def add_realization(self, realization):
        self.add_calls.append(realization)
        self.realizations[realization.fact_reference] = realization

    def save_realization(self, realization, *, expected_version):
        self.save_calls.append((realization, expected_version))
        self.realizations[realization.fact_reference] = realization

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        self.commit_count += 1


def create_command(*, addresses=("10.0.0.20", "10.0.0.10"), key="create-1"):
    return CreateResourceRealizationCommand(
        resource_reference="res-1",
        technical_addresses=addresses,
        valid_from=START,
        valid_to=None,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def open_realization():
    return ResourceRealizationVersion(
        fact_reference="current",
        resource_reference="res-1",
        endpoint_realizations=(EndpointAddress("old-endpoint", "10.0.0.1"),),
        valid_from=START,
        valid_to=None,
        provenance_reference="prov:create:current",
    )


def test_create_realization_normalizes_set_and_generates_endpoint_references():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()

    result = CreateResourceRealization(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
    ).execute(create_command(addresses=(" 10.0.0.20 ", "10.0.0.10")))

    assert result.outcome is TemporalCurationOutcome.CREATED
    assert result.realization is not None
    assert result.realization.fact_reference == "realization-1"
    assert tuple(
        item.technical_address for item in result.realization.endpoint_realizations
    ) == ("10.0.0.10", "10.0.0.20")
    assert tuple(
        item.endpoint_reference for item in result.realization.endpoint_realizations
    ) == ("endpoint-1", "endpoint-2")
    assert result.realization.provenance_reference == "prov:create:realization-1"
    assert identities.fact_count == 1
    assert identities.endpoint_count == 2
    assert catalogue.commit_count == 1


def test_reordered_equivalent_addresses_replay_same_realization():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()
    use_case = CreateResourceRealization(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
    )

    first = use_case.execute(
        create_command(addresses=("10.0.0.20", "10.0.0.10"), key="same-key")
    )
    second = use_case.execute(
        create_command(addresses=("10.0.0.10", "10.0.0.20"), key="same-key")
    )

    assert first.outcome is TemporalCurationOutcome.CREATED
    assert second.outcome is TemporalCurationOutcome.RESOLVED
    assert second.realization == first.realization
    assert identities.fact_count == 1
    assert catalogue.commit_count == 1


def test_create_rejects_duplicate_or_invalid_interval_before_overlap_query():
    catalogue = FakeCatalogue()
    use_case = CreateResourceRealization(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
    )

    duplicate = use_case.execute(
        create_command(addresses=("10.0.0.10", " 10.0.0.10 "), key="dup")
    )
    naive = use_case.execute(
        CreateResourceRealizationCommand(
            resource_reference="res-1",
            technical_addresses=("10.0.0.10",),
            valid_from=START.replace(tzinfo=None),
            valid_to=None,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="naive",
        )
    )

    assert duplicate.outcome is TemporalCurationOutcome.INPUT_INVALID
    assert naive.outcome is TemporalCurationOutcome.INPUT_INVALID
    assert catalogue.overlap_calls == []


def test_create_rejects_overlapping_authoritative_realization():
    catalogue = FakeCatalogue()
    catalogue.overlap_rows = (open_realization(),)

    result = CreateResourceRealization(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
    ).execute(create_command())

    assert result.outcome is TemporalCurationOutcome.OVERLAP_CONFLICT
    assert catalogue.add_calls == []
    assert catalogue.commit_count == 0


def test_replace_ends_current_with_separate_provenance_and_creates_successor():
    catalogue = FakeCatalogue()
    current = open_realization()
    catalogue.realizations[current.fact_reference] = current
    catalogue.overlap_rows = (current,)
    identities = FakeIdentities()

    result = ReplaceResourceRealization(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
    ).execute(
        ReplaceResourceRealizationCommand(
            current_fact_reference="current",
            technical_addresses=("10.0.0.2",),
            valid_from=REPLACEMENT,
            valid_to=None,
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="replace-1",
        )
    )

    assert result.outcome is TemporalCurationOutcome.UPDATED
    assert result.realization is not None
    assert result.realization.fact_reference == "realization-1"
    assert result.realization.valid_from == REPLACEMENT
    assert result.replaced_fact_reference == "current"

    ended, expected_version = catalogue.save_calls[0]
    assert expected_version == 1
    assert ended.fact_reference == "current"
    assert ended.valid_to == REPLACEMENT
    assert ended.provenance_reference == "prov:create:current"
    assert ended.end_provenance_reference == "prov:end:current"
    assert ended.version == 2
    assert catalogue.commit_count == 1


def test_replace_rejects_stale_version_without_mutation():
    catalogue = FakeCatalogue()
    current = open_realization()
    catalogue.realizations[current.fact_reference] = current

    result = ReplaceResourceRealization(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
    ).execute(
        ReplaceResourceRealizationCommand(
            current_fact_reference="current",
            technical_addresses=("10.0.0.2",),
            valid_from=REPLACEMENT,
            valid_to=None,
            expected_version=2,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="replace-stale",
        )
    )

    assert result.outcome is TemporalCurationOutcome.CONCURRENCY_CONFLICT
    assert catalogue.save_calls == []
    assert catalogue.add_calls == []
    assert catalogue.commit_count == 0
