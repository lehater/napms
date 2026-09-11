from datetime import datetime, timezone
from uuid import UUID

from napms.contexts.access_policy.application.ports import InteractionOutcome
from napms.contexts.access_policy.domain.model import RuleSemanticIdentity
from napms.contexts.application_catalogue.infrastructure.integrations.access_policy import (
    AccessPolicyCommunicationCatalogueAdapter,
)
from napms.contexts.application_catalogue.infrastructure.integrations.policy_export import (
    PolicyExportApplicationCatalogueAdapter,
)
from napms.contexts.application_catalogue.application.discovery.resolve import (
    CatalogueResolutionOutcome,
    ResolveApplicationProjection,
    ValidateDirectedInteraction,
)
from napms.contexts.application_catalogue.domain.model import (
    DcsRevision,
    DeploymentResourceBinding,
    DirectedInteractionIdentity,
)
from napms.workflows.policy_export.application.ports import ApplicationProjectionOutcome


SOURCE = UUID(int=1)
DESTINATION = UUID(int=2)
DCS = UUID(int=3)
AS_OF = datetime(2026, 9, 8, 12, 0, tzinfo=timezone.utc)
IDENTITY = RuleSemanticIdentity(SOURCE, DESTINATION, DCS)
CATALOGUE_IDENTITY = DirectedInteractionIdentity(SOURCE, DESTINATION, DCS)


def dcs(source=SOURCE, destination=DESTINATION):
    return DcsRevision(
        revision_id=DCS,
        source_component_deployment_id=source,
        destination_component_deployment_id=destination,
        projection_payload=b'{"version":1}',
        provenance_reference="dcs-provenance",
    )


def binding(reference, deployment, resource):
    return DeploymentResourceBinding(
        reference_id=reference,
        component_deployment_id=deployment,
        resource_reference=resource,
        valid_from=datetime(2026, 9, 1, tzinfo=timezone.utc),
        valid_to=None,
        provenance_reference=f"provenance-{reference}",
    )


class FakeCatalogue:
    def __init__(self, dcs_revision=None, bindings=None):
        self.dcs_revision = dcs_revision
        self.bindings = bindings or {}

    def get_dcs_revision(self, revision_id):
        if self.dcs_revision is not None and self.dcs_revision.revision_id == revision_id:
            return self.dcs_revision
        return None

    def find_effective_bindings(self, *, component_deployment_id, as_of):
        return tuple(self.bindings.get(component_deployment_id, ()))


def test_exact_dcs_identity_is_valid_for_proposal():
    adapter = AccessPolicyCommunicationCatalogueAdapter(
        validator=ValidateDirectedInteraction(
            catalogue=FakeCatalogue(dcs_revision=dcs())
        )
    )

    result = adapter.resolve_directed_interaction(
        identity=IDENTITY,
        effective_time=AS_OF,
    )

    assert result.outcome is InteractionOutcome.VALID
    assert result.identity == IDENTITY
    assert result.provenance_reference == "dcs-provenance"


def test_dcs_subject_mismatch_is_invalid():
    result = ValidateDirectedInteraction(
        catalogue=FakeCatalogue(dcs_revision=dcs(source=UUID(int=99)))
    ).execute(identity=CATALOGUE_IDENTITY, effective_time=AS_OF)

    assert result.outcome is CatalogueResolutionOutcome.INVALID


def test_missing_dcs_is_unknown_to_access_policy():
    adapter = AccessPolicyCommunicationCatalogueAdapter(
        validator=ValidateDirectedInteraction(catalogue=FakeCatalogue())
    )

    result = adapter.resolve_directed_interaction(
        identity=IDENTITY,
        effective_time=AS_OF,
    )

    assert result.outcome is InteractionOutcome.UNKNOWN


def test_projection_resolves_multiple_distinct_resources_deterministically():
    catalogue = FakeCatalogue(
        dcs_revision=dcs(),
        bindings={
            SOURCE: (
                binding("source-b", SOURCE, "resource-b"),
                binding("source-a", SOURCE, "resource-a"),
            ),
            DESTINATION: (binding("destination-a", DESTINATION, "resource-z"),),
        },
    )
    adapter = PolicyExportApplicationCatalogueAdapter(
        resolver=ResolveApplicationProjection(catalogue=catalogue)
    )

    result = adapter.resolve_projection(subject=IDENTITY, as_of=AS_OF)

    assert result.outcome is ApplicationProjectionOutcome.RESOLVED
    assert result.subject == IDENTITY
    assert result.as_of == AS_OF
    assert tuple(ref.value for ref in result.source_resource_references) == (
        "resource-a",
        "resource-b",
    )
    assert tuple(ref.value for ref in result.destination_resource_references) == (
        "resource-z",
    )
    assert result.dcs_projection_payload == b'{"version":1}'
    assert result.fact_reference.startswith("acc-projection:")
    assert "source-a" in result.validity_reference
    assert "destination-a" in result.validity_reference
    assert result.provenance_reference.startswith("acc-provenance:v1:")
    assert "dcs-provenance" in result.provenance_reference
    assert "provenance-source-a" in result.provenance_reference
    assert "provenance-destination-a" in result.provenance_reference


def test_projection_missing_required_binding_fails_closed():
    result = ResolveApplicationProjection(
        catalogue=FakeCatalogue(
            dcs_revision=dcs(),
            bindings={SOURCE: (binding("source-a", SOURCE, "resource-a"),)},
        )
    ).execute(subject=CATALOGUE_IDENTITY, as_of=AS_OF)

    assert result.outcome is CatalogueResolutionOutcome.MISSING


def test_overlapping_versions_for_same_resource_fail_closed_unknown():
    result = ResolveApplicationProjection(
        catalogue=FakeCatalogue(
            dcs_revision=dcs(),
            bindings={
                SOURCE: (
                    binding("source-a-v1", SOURCE, "resource-a"),
                    binding("source-a-v2", SOURCE, "resource-a"),
                ),
                DESTINATION: (binding("destination-a", DESTINATION, "resource-z"),),
            },
        )
    ).execute(subject=IDENTITY, as_of=AS_OF)

    assert result.outcome is CatalogueResolutionOutcome.UNKNOWN
