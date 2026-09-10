from datetime import datetime, timezone

from napms.resource_catalogue.application.ports import (
    ResourceCatalogueAuthorityCheck,
    ResourceCatalogueAuthorityOutcome,
)
from napms.resource_catalogue.application.temporal_curation import (
    CreateResourceResponsibility,
    CreateResourceScopeAffiliation,
    CreateResponsibilityCommand,
    CreateScopeAffiliationCommand,
    EndResourceResponsibility,
    EndResourceScopeAffiliation,
    EndResponsibilityCommand,
    EndScopeAffiliationCommand,
    TemporalCurationOutcome,
)
from napms.resource_catalogue.domain.model import (
    Resource,
    ResourceLifecycleState,
    ResourceScopeAffiliation,
)
from napms.resource_catalogue.domain.responsibility import (
    ResponsiblePartyKind,
    ResourceResponsibility,
    ResourceResponsibilityRole,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
START = datetime(2026, 9, 10, 8, 0, tzinfo=timezone.utc)
END = datetime(2026, 9, 11, 8, 0, tzinfo=timezone.utc)


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
        self.affiliation_count = 0
        self.responsibility_count = 0

    def new_scope_affiliation_reference(self):
        self.affiliation_count += 1
        return "aff-generated"

    def new_responsibility_reference(self):
        self.responsibility_count += 1
        return "resp-generated"


class FakeProvenance:
    def __init__(self):
        self.calls = []

    def for_scope_affiliation(self, **kwargs):
        self.calls.append(("affiliation", kwargs))
        return "prov:affiliation:create"

    def for_scope_affiliation_end(self, **kwargs):
        self.calls.append(("affiliation-end", kwargs))
        return "prov:affiliation:end"

    def for_responsibility(self, **kwargs):
        self.calls.append(("responsibility", kwargs))
        return "prov:responsibility:create"

    def for_responsibility_end(self, **kwargs):
        self.calls.append(("responsibility-end", kwargs))
        return "prov:responsibility:end"


class FakeCatalogue:
    def __init__(self, resource=None):
        resource = resource or Resource(
            resource_reference="res-1",
            display_name="Orders",
            provenance_reference="prov:resource",
        )
        self.resources = {resource.resource_reference: resource}
        self.affiliations = {}
        self.responsibilities = {}
        self.receipts = {}
        self.overlapping_affiliations = ()
        self.affiliation_saves = []
        self.responsibility_saves = []
        self.commit_count = 0

    def get_resource(self, resource_reference):
        return self.resources.get(resource_reference)

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def get_scope_affiliation(self, affiliation_reference):
        return self.affiliations.get(affiliation_reference)

    def find_overlapping_scope_affiliations(self, **kwargs):
        return self.overlapping_affiliations

    def add_scope_affiliation(self, affiliation):
        self.affiliations[affiliation.affiliation_reference] = affiliation

    def save_scope_affiliation(self, affiliation, *, expected_version):
        self.affiliation_saves.append((affiliation, expected_version))
        self.affiliations[affiliation.affiliation_reference] = affiliation

    def get_responsibility(self, assignment_reference):
        return self.responsibilities.get(assignment_reference)

    def add_responsibility(self, responsibility):
        self.responsibilities[responsibility.assignment_reference] = responsibility

    def save_responsibility(self, responsibility, *, expected_version):
        self.responsibility_saves.append((responsibility, expected_version))
        self.responsibilities[responsibility.assignment_reference] = responsibility

    def commit(self):
        self.commit_count += 1


def affiliation_command(*, key="aff-create"):
    return CreateScopeAffiliationCommand(
        resource_reference="res-1",
        responsibility_scope="payments",
        valid_from=START,
        valid_to=None,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def responsibility_command(*, key="resp-create"):
    return CreateResponsibilityCommand(
        resource_reference="res-1",
        party_reference="team-payments",
        party_kind=ResponsiblePartyKind.TEAM,
        role=ResourceResponsibilityRole.TECHNICAL_OWNER,
        display_name="Payments platform",
        contact="payments@example.invalid",
        valid_from=START,
        valid_to=None,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def test_create_scope_affiliation_generates_reference_and_provenance():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()
    provenance = FakeProvenance()

    result = CreateResourceScopeAffiliation(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=provenance,
    ).execute(affiliation_command())

    assert result.outcome is TemporalCurationOutcome.CREATED
    assert result.affiliation is not None
    assert result.affiliation.affiliation_reference == "aff-generated"
    assert result.affiliation.resource_reference == "res-1"
    assert result.affiliation.responsibility_scope == "payments"
    assert result.affiliation.provenance_reference == "prov:affiliation:create"
    assert result.affiliation.version == 1
    assert identities.affiliation_count == 1
    assert catalogue.commit_count == 1


def test_scope_affiliation_overlap_is_rejected_before_identity_allocation():
    catalogue = FakeCatalogue()
    catalogue.overlapping_affiliations = (
        ResourceScopeAffiliation(
            affiliation_reference="existing",
            resource_reference="res-1",
            responsibility_scope="payments",
            valid_from=START,
            valid_to=None,
            provenance_reference="prov:existing",
        ),
    )
    identities = FakeIdentities()

    result = CreateResourceScopeAffiliation(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
    ).execute(affiliation_command())

    assert result.outcome is TemporalCurationOutcome.OVERLAP_CONFLICT
    assert identities.affiliation_count == 0
    assert catalogue.commit_count == 0


def test_new_temporal_fact_requires_active_resource():
    retired = Resource(
        resource_reference="res-1",
        display_name="Orders",
        provenance_reference="prov:resource",
        lifecycle_state=ResourceLifecycleState.RETIRED,
    )
    catalogue = FakeCatalogue(resource=retired)

    affiliation = CreateResourceScopeAffiliation(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
    ).execute(affiliation_command(key="inactive-aff"))
    responsibility = CreateResourceResponsibility(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
    ).execute(responsibility_command(key="inactive-resp"))

    assert affiliation.outcome is TemporalCurationOutcome.RESOURCE_INACTIVE
    assert responsibility.outcome is TemporalCurationOutcome.RESOURCE_INACTIVE
    assert catalogue.commit_count == 0


def test_end_scope_affiliation_preserves_creation_and_records_end_provenance():
    catalogue = FakeCatalogue()
    catalogue.affiliations["aff-1"] = ResourceScopeAffiliation(
        affiliation_reference="aff-1",
        resource_reference="res-1",
        responsibility_scope="payments",
        valid_from=START,
        valid_to=None,
        provenance_reference="prov:affiliation:create",
    )

    result = EndResourceScopeAffiliation(
        authority=FakeAuthority(),
        catalogue=catalogue,
        provenance=FakeProvenance(),
    ).execute(
        EndScopeAffiliationCommand(
            affiliation_reference="aff-1",
            valid_to=END,
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="aff-end",
        )
    )

    assert result.outcome is TemporalCurationOutcome.UPDATED
    assert result.affiliation is not None
    assert result.affiliation.provenance_reference == "prov:affiliation:create"
    assert result.affiliation.end_provenance_reference == "prov:affiliation:end"
    assert result.affiliation.valid_to == END
    assert result.affiliation.version == 2
    assert catalogue.affiliation_saves == [(result.affiliation, 1)]


def test_create_and_end_resource_responsibility_preserves_audit_chain():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()
    provenance = FakeProvenance()
    creator = CreateResourceResponsibility(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=provenance,
    )

    created = creator.execute(responsibility_command())

    assert created.outcome is TemporalCurationOutcome.CREATED
    assert created.responsibility is not None
    assert created.responsibility.assignment_reference == "resp-generated"
    assert created.responsibility.provenance_reference == "prov:responsibility:create"

    ended = EndResourceResponsibility(
        authority=FakeAuthority(),
        catalogue=catalogue,
        provenance=provenance,
    ).execute(
        EndResponsibilityCommand(
            assignment_reference="resp-generated",
            valid_to=END,
            expected_version=1,
            actor_id="actor-1",
            effective_time=NOW,
            idempotency_key="resp-end",
        )
    )

    assert ended.outcome is TemporalCurationOutcome.UPDATED
    assert ended.responsibility is not None
    assert ended.responsibility.provenance_reference == "prov:responsibility:create"
    assert ended.responsibility.end_provenance_reference == "prov:responsibility:end"
    assert ended.responsibility.version == 2
    assert catalogue.responsibility_saves == [(ended.responsibility, 1)]
