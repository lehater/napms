from datetime import datetime, timezone
from uuid import UUID

from napms.application_catalogue.adapters.scoped_connectivity_inventory import (
    ApplicationCatalogueScopedConnectivityAdapter,
)
from napms.scoped_connectivity_inventory.application.ports import (
    DependencyAvailability,
)


AS_OF = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)
COMPONENT = UUID(int=1)


class OversizedCatalogue:
    def __init__(self, *, stage):
        self.stage = stage
        self.requested_limits = []

    def find_effective_bindings_for_resources(
        self,
        *,
        resource_references,
        as_of,
        limit=None,
    ):
        self.requested_limits.append(limit)
        if self.stage == "resource-bindings":
            return tuple(object() for _ in range(limit))
        return ()

    def list_dcs_revisions_for_components(
        self,
        *,
        component_deployment_ids,
        limit=None,
    ):
        self.requested_limits.append(limit)
        if self.stage == "interactions":
            return tuple(object() for _ in range(limit))
        return ()

    def find_effective_bindings_for_components(
        self,
        *,
        component_deployment_ids,
        as_of,
        limit=None,
    ):
        self.requested_limits.append(limit)
        if self.stage == "component-bindings":
            return tuple(object() for _ in range(limit))
        return ()

    def get_component_deployments(self, deployment_ids):
        raise AssertionError("oversized reads must stop before enrichment")


def test_oversized_local_component_binding_set_is_explicitly_unavailable():
    catalogue = OversizedCatalogue(stage="resource-bindings")
    result = ApplicationCatalogueScopedConnectivityAdapter(
        catalogue=catalogue
    ).list_bound_components(
        resource_references=("resource-1",),
        as_of=AS_OF,
    )

    assert result.availability is DependencyAvailability.UNAVAILABLE
    assert catalogue.requested_limits == [2001]


def test_oversized_interaction_set_is_explicitly_unavailable():
    catalogue = OversizedCatalogue(stage="interactions")
    result = ApplicationCatalogueScopedConnectivityAdapter(
        catalogue=catalogue
    ).list_interactions_for_components(
        component_deployment_ids=(COMPONENT,),
    )

    assert result.availability is DependencyAvailability.UNAVAILABLE
    assert catalogue.requested_limits == [2001]


def test_oversized_remote_binding_set_is_explicitly_unavailable():
    catalogue = OversizedCatalogue(stage="component-bindings")
    result = ApplicationCatalogueScopedConnectivityAdapter(
        catalogue=catalogue
    ).list_resource_bindings_for_components(
        component_deployment_ids=(COMPONENT,),
        as_of=AS_OF,
    )

    assert result.availability is DependencyAvailability.UNAVAILABLE
    assert catalogue.requested_limits == [2001]
