from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.application_catalogue.application.curation_detail import (
    ReadApplicationCatalogueTreeDetail,
)
from napms.application_catalogue.domain.model import (
    Application,
    CatalogueInvariantError,
    Component,
    ComponentDeployment,
    DcsRevision,
    DeploymentResourceBinding,
)


NOW = datetime(2026, 9, 10, 12, 0, tzinfo=timezone.utc)
APP = UUID("00000000-0000-0000-0000-000000005001")
COMPONENT_A = UUID("00000000-0000-0000-0000-000000005002")
COMPONENT_B = UUID("00000000-0000-0000-0000-000000005003")
DEPLOYMENT_A = UUID("00000000-0000-0000-0000-000000005004")
DEPLOYMENT_B = UUID("00000000-0000-0000-0000-000000005005")
DCS = UUID("00000000-0000-0000-0000-000000005006")


class FakeDetailCatalogue:
    def __init__(self):
        self.application = Application(APP, "Orders", "prov:app")
        self.components = (
            Component(COMPONENT_B, APP, "Worker", "prov:b"),
            Component(COMPONENT_A, APP, "API", "prov:a"),
        )
        self.deployments = {
            COMPONENT_A: (
                ComponentDeployment(
                    DEPLOYMENT_A,
                    COMPONENT_A,
                    "prov:dep-a",
                    display_name="prod",
                ),
            ),
            COMPONENT_B: (
                ComponentDeployment(
                    DEPLOYMENT_B,
                    COMPONENT_B,
                    "prov:dep-b",
                    display_name="prod",
                ),
            ),
        }
        self.binding_calls = []
        self.dcs_calls = []

    def get_application(self, application_id):
        return self.application if application_id == APP else None

    def list_components(self, *, application_id, include_retired):
        assert application_id == APP
        return self.components

    def list_component_deployments(self, *, component_id, include_retired):
        return self.deployments[component_id]

    def list_effective_bindings_for_deployments(self, *, deployment_ids, as_of):
        self.binding_calls.append((deployment_ids, as_of))
        return (
            DeploymentResourceBinding(
                reference_id="binding-b",
                component_deployment_id=DEPLOYMENT_B,
                resource_reference="resource-z",
                valid_from=NOW,
                valid_to=None,
                provenance_reference="prov:binding-b",
            ),
            DeploymentResourceBinding(
                reference_id="binding-a",
                component_deployment_id=DEPLOYMENT_A,
                resource_reference="resource-a",
                valid_from=NOW,
                valid_to=None,
                provenance_reference="prov:binding-a",
            ),
        )

    def list_dcs_revisions_for_deployments(self, *, deployment_ids):
        self.dcs_calls.append(deployment_ids)
        return (
            DcsRevision(
                revision_id=DCS,
                source_component_deployment_id=DEPLOYMENT_A,
                destination_component_deployment_id=DEPLOYMENT_B,
                projection_payload=b"payload",
                provenance_reference="prov:dcs",
                display_name="HTTPS",
            ),
        )


def test_tree_detail_batches_bindings_and_dcs_and_preserves_hierarchy():
    catalogue = FakeDetailCatalogue()

    detail = ReadApplicationCatalogueTreeDetail(catalogue=catalogue).execute(
        application_id=APP,
        as_of=NOW,
    )

    assert detail is not None
    assert detail.application.application_id == APP
    assert tuple(item.component.display_name for item in detail.components) == (
        "API",
        "Worker",
    )
    api, worker = detail.components
    assert api.deployments[0].deployment.deployment_id == DEPLOYMENT_A
    assert api.deployments[0].effective_resource_bindings[0].resource_reference == "resource-a"
    assert api.deployments[0].dcs_revisions[0].revision_id == DCS
    assert worker.deployments[0].dcs_revisions[0].revision_id == DCS
    assert len(catalogue.binding_calls) == 1
    assert len(catalogue.dcs_calls) == 1
    assert set(catalogue.binding_calls[0][0]) == {DEPLOYMENT_A, DEPLOYMENT_B}
    assert set(catalogue.dcs_calls[0]) == {DEPLOYMENT_A, DEPLOYMENT_B}


def test_tree_detail_returns_none_for_unknown_application_without_child_queries():
    catalogue = FakeDetailCatalogue()

    detail = ReadApplicationCatalogueTreeDetail(catalogue=catalogue).execute(
        application_id=UUID("00000000-0000-0000-0000-000000005999"),
        as_of=NOW,
    )

    assert detail is None
    assert catalogue.binding_calls == []
    assert catalogue.dcs_calls == []


def test_tree_detail_requires_offset_aware_as_of():
    with pytest.raises(CatalogueInvariantError):
        ReadApplicationCatalogueTreeDetail(catalogue=FakeDetailCatalogue()).execute(
            application_id=APP,
            as_of=datetime(2026, 9, 10, 12, 0),
        )
