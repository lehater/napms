from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.application_catalogue.application.dcs_curation import (
    CreateDcsRevision,
    CreateDcsRevisionCommand,
)
from napms.application_catalogue.application.ports import (
    ApplicationCatalogueAuthorityCheck,
    ApplicationCatalogueAuthorityOutcome,
)
from napms.application_catalogue.application.structure_curation import (
    CatalogueMutationOutcome,
)
from napms.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    DcsPortConstraint,
    DcsPortRange,
)
from napms.application_catalogue.domain.model import (
    CatalogueInvariantError,
    CatalogueLifecycleState,
    ComponentDeployment,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
COMPONENT_ID = UUID("00000000-0000-0000-0000-000000003001")
SOURCE = UUID("00000000-0000-0000-0000-000000003002")
DESTINATION = UUID("00000000-0000-0000-0000-000000003003")
REVISION = UUID("00000000-0000-0000-0000-000000003004")


class FakeAuthority:
    def check_curation(self, **kwargs):
        return ApplicationCatalogueAuthorityCheck(
            outcome=ApplicationCatalogueAuthorityOutcome.PERMITTED,
            authority_reference="auth-acc",
        )


class FakeIdentities:
    def __init__(self):
        self.calls = 0

    def new_dcs_revision_id(self):
        self.calls += 1
        return REVISION


class FakeProvenance:
    def for_dcs_revision(self, **kwargs):
        return "prov:dcs:create"


class FakeEncoder:
    def __init__(self):
        self.calls = []

    def encode(self, alternatives):
        self.calls.append(alternatives)
        return b"encoded-projection"


class FakeCatalogue:
    def __init__(self, *, source=None, destination=None):
        source = source or deployment(SOURCE)
        destination = destination or deployment(DESTINATION)
        self.deployments = {
            source.deployment_id: source,
            destination.deployment_id: destination,
        }
        self.revisions = {}
        self.receipts = {}
        self.add_calls = []
        self.commit_count = 0

    def get_component_deployment(self, deployment_id):
        return self.deployments.get(deployment_id)

    def get_dcs_revision(self, revision_id):
        return self.revisions.get(revision_id)

    def add_dcs_revision(self, revision):
        self.add_calls.append(revision)
        self.revisions[revision.revision_id] = revision

    def find_command_receipt(self, *, actor_id, idempotency_key):
        return self.receipts.get((actor_id, idempotency_key))

    def record_command_receipt(self, *, actor_id, idempotency_key, receipt):
        self.receipts[(actor_id, idempotency_key)] = receipt

    def commit(self):
        self.commit_count += 1


def deployment(deployment_id, *, retired=False):
    return ComponentDeployment(
        deployment_id=deployment_id,
        component_id=COMPONENT_ID,
        provenance_reference=f"prov:{deployment_id}",
        lifecycle_state=(
            CatalogueLifecycleState.RETIRED
            if retired
            else CatalogueLifecycleState.ACTIVE
        ),
        retirement_provenance_reference=("prov:retire" if retired else None),
    )


def https_alternative(service="https"):
    return AuthoredDcsTrafficAlternative(
        protocol=" TCP ",
        source_ports=DcsPortConstraint.any(),
        destination_ports=DcsPortConstraint.ranged(
            DcsPortRange(443, 443),
        ),
        service_reference=service,
    )


def dns_alternative():
    return AuthoredDcsTrafficAlternative(
        protocol="udp",
        source_ports=DcsPortConstraint.any(),
        destination_ports=DcsPortConstraint.ranged(DcsPortRange(53, 53)),
        service_reference="dns",
    )


def command(*, alternatives=None, key="create-dcs"):
    selected = (https_alternative(),) if alternatives is None else alternatives
    return CreateDcsRevisionCommand(
        source_component_deployment_id=SOURCE,
        destination_component_deployment_id=DESTINATION,
        display_name=" HTTPS Orders ",
        traffic_alternatives=selected,
        actor_id="actor-1",
        effective_time=NOW,
        idempotency_key=key,
    )


def test_create_dcs_revision_encodes_canonical_acc_semantics():
    catalogue = FakeCatalogue()
    encoder = FakeEncoder()

    result = CreateDcsRevision(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
        encoder=encoder,
    ).execute(command(alternatives=(https_alternative(), dns_alternative())))

    assert result.outcome is CatalogueMutationOutcome.CREATED
    assert result.revision is not None
    assert result.revision.revision_id == REVISION
    assert result.revision.source_component_deployment_id == SOURCE
    assert result.revision.destination_component_deployment_id == DESTINATION
    assert result.revision.display_name == "HTTPS Orders"
    assert result.revision.projection_payload == b"encoded-projection"
    assert result.revision.provenance_reference == "prov:dcs:create"
    assert tuple(item.protocol for item in encoder.calls[0]) == ("tcp", "udp")
    assert catalogue.add_calls == [result.revision]
    assert catalogue.commit_count == 1


def test_semantically_reordered_retry_resolves_same_revision():
    catalogue = FakeCatalogue()
    identities = FakeIdentities()
    encoder = FakeEncoder()
    use_case = CreateDcsRevision(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
        encoder=encoder,
    )

    first = use_case.execute(
        command(alternatives=(https_alternative(), dns_alternative()), key="same-key")
    )
    second = use_case.execute(
        command(alternatives=(dns_alternative(), https_alternative()), key="same-key")
    )

    assert first.outcome is CatalogueMutationOutcome.CREATED
    assert second.outcome is CatalogueMutationOutcome.RESOLVED
    assert second.revision == first.revision
    assert identities.calls == 1
    assert len(encoder.calls) == 1
    assert catalogue.commit_count == 1


def test_dcs_authoring_requires_both_active_deployments_before_encoding():
    catalogue = FakeCatalogue(source=deployment(SOURCE, retired=True))
    encoder = FakeEncoder()
    identities = FakeIdentities()

    result = CreateDcsRevision(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=identities,
        provenance=FakeProvenance(),
        encoder=encoder,
    ).execute(command())

    assert result.outcome is CatalogueMutationOutcome.PARENT_INACTIVE
    assert encoder.calls == []
    assert identities.calls == 0
    assert catalogue.add_calls == []
    assert catalogue.commit_count == 0


def test_dcs_authoring_rejects_missing_participant():
    catalogue = FakeCatalogue()
    del catalogue.deployments[DESTINATION]

    result = CreateDcsRevision(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
        encoder=FakeEncoder(),
    ).execute(command())

    assert result.outcome is CatalogueMutationOutcome.NOT_FOUND
    assert catalogue.commit_count == 0


def test_dcs_authoring_rejects_empty_or_duplicate_alternatives():
    catalogue = FakeCatalogue()
    use_case = CreateDcsRevision(
        authority=FakeAuthority(),
        catalogue=catalogue,
        identities=FakeIdentities(),
        provenance=FakeProvenance(),
        encoder=FakeEncoder(),
    )

    empty = use_case.execute(command(alternatives=(), key="empty"))
    duplicate = use_case.execute(
        command(
            alternatives=(https_alternative(), https_alternative()),
            key="duplicate",
        )
    )

    assert empty.outcome is CatalogueMutationOutcome.INPUT_INVALID
    assert duplicate.outcome is CatalogueMutationOutcome.INPUT_INVALID
    assert catalogue.add_calls == []
    assert catalogue.commit_count == 0


def test_port_ranges_are_canonicalized_and_invalid_ranges_fail_at_domain_boundary():
    constraint = DcsPortConstraint.ranged(
        DcsPortRange(100, 110),
        DcsPortRange(111, 120),
        DcsPortRange(90, 99),
    )

    assert constraint.ranges == (DcsPortRange(90, 120),)

    with pytest.raises(CatalogueInvariantError):
        DcsPortRange(70000, 70001)
