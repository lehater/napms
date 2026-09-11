from uuid import UUID

from napms.contexts.application_catalogue.application.describe_interactions import (
    DescribeDirectedInteractions,
)
from napms.contexts.application_catalogue.domain.model import (
    ComponentDeployment,
    DcsRevision,
    DirectedInteractionIdentity,
)


SOURCE = UUID(int=101)
DESTINATION = UUID(int=102)
DCS = UUID(int=103)
SOURCE_COMPONENT = UUID(int=201)
DESTINATION_COMPONENT = UUID(int=202)
IDENTITY = DirectedInteractionIdentity(SOURCE, DESTINATION, DCS)


class FakeCatalogue:
    def __init__(self, *, deployments=(), revisions=()):
        self.deployments = tuple(deployments)
        self.revisions = tuple(revisions)
        self.deployment_calls = []
        self.revision_calls = []

    def get_component_deployments(self, deployment_ids):
        self.deployment_calls.append(deployment_ids)
        return tuple(
            value
            for value in self.deployments
            if value.deployment_id in deployment_ids
        )

    def get_dcs_revisions(self, revision_ids):
        self.revision_calls.append(revision_ids)
        return tuple(
            value
            for value in self.revisions
            if value.revision_id in revision_ids
        )


def deployment(deployment_id, component_id, provenance, display_name=None):
    return ComponentDeployment(
        deployment_id=deployment_id,
        component_id=component_id,
        provenance_reference=provenance,
        display_name=display_name,
    )


def test_describe_exact_identity_returns_optional_labels_and_projection_payload():
    catalogue = FakeCatalogue(
        deployments=(
            deployment(
                SOURCE,
                SOURCE_COMPONENT,
                "source-provenance",
                "Checkout Web",
            ),
            deployment(
                DESTINATION,
                DESTINATION_COMPONENT,
                "destination-provenance",
                "Orders API",
            ),
        ),
        revisions=(
            DcsRevision(
                revision_id=DCS,
                source_component_deployment_id=SOURCE,
                destination_component_deployment_id=DESTINATION,
                projection_payload=b'{"dcs":"payload"}',
                provenance_reference="dcs-provenance",
                display_name="HTTPS Orders",
            ),
        ),
    )

    result = DescribeDirectedInteractions(catalogue=catalogue).execute((IDENTITY,))

    assert len(result) == 1
    description = result[0]
    assert description.identity == IDENTITY
    assert description.source_display_name == "Checkout Web"
    assert description.destination_display_name == "Orders API"
    assert description.dcs_display_name == "HTTPS Orders"
    assert description.dcs_projection_payload == b'{"dcs":"payload"}'
    assert description.dcs_provenance_reference == "dcs-provenance"
    assert catalogue.deployment_calls == [(SOURCE, DESTINATION)]
    assert catalogue.revision_calls == [(DCS,)]


def test_describe_preserves_stable_fallback_when_labels_are_missing():
    catalogue = FakeCatalogue(
        deployments=(
            deployment(SOURCE, SOURCE_COMPONENT, "source-provenance"),
            deployment(DESTINATION, DESTINATION_COMPONENT, "destination-provenance"),
        ),
        revisions=(
            DcsRevision(
                revision_id=DCS,
                source_component_deployment_id=SOURCE,
                destination_component_deployment_id=DESTINATION,
                projection_payload=b"payload",
                provenance_reference="dcs-provenance",
            ),
        ),
    )

    description = DescribeDirectedInteractions(
        catalogue=catalogue
    ).execute((IDENTITY,))[0]

    assert description.source_display_name is None
    assert description.destination_display_name is None
    assert description.dcs_display_name is None
    assert description.dcs_projection_payload == b"payload"


def test_dcs_presentation_requires_exact_subject_match():
    catalogue = FakeCatalogue(
        deployments=(
            deployment(SOURCE, SOURCE_COMPONENT, "source", "Checkout Web"),
            deployment(DESTINATION, DESTINATION_COMPONENT, "destination", "Orders API"),
        ),
        revisions=(
            DcsRevision(
                revision_id=DCS,
                source_component_deployment_id=UUID(int=999),
                destination_component_deployment_id=DESTINATION,
                projection_payload=b"wrong-subject",
                provenance_reference="wrong-dcs",
                display_name="Wrong DCS",
            ),
        ),
    )

    description = DescribeDirectedInteractions(
        catalogue=catalogue
    ).execute((IDENTITY,))[0]

    assert description.source_display_name == "Checkout Web"
    assert description.destination_display_name == "Orders API"
    assert description.dcs_display_name is None
    assert description.dcs_projection_payload is None
    assert description.dcs_provenance_reference is None


def test_describe_batches_duplicate_component_and_revision_ids():
    second = DirectedInteractionIdentity(SOURCE, DESTINATION, DCS)
    catalogue = FakeCatalogue()

    result = DescribeDirectedInteractions(catalogue=catalogue).execute(
        (IDENTITY, second)
    )

    assert len(result) == 2
    assert catalogue.deployment_calls == [(SOURCE, DESTINATION)]
    assert catalogue.revision_calls == [(DCS,)]
