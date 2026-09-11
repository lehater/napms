from napms.application_catalogue.application.binding_curation import (
    BindingTargetOutcome,
)
from napms.contexts.resource_catalogue.application.ports import (
    ResourceCataloguePersistenceError,
)
from napms.contexts.resource_catalogue.domain.model import ResourceLifecycleState


class ResourceCatalogueBindingTargetAdapter:
    """Expose only the RC state needed to admit a new ACC binding."""

    def __init__(self, resources) -> None:
        self._resources = resources

    def check_target(self, *, resource_reference: str, effective_time):
        del effective_time  # Resource lifecycle is identity state, not a temporal fact.
        try:
            resource = self._resources.get_resource(resource_reference)
        except ResourceCataloguePersistenceError:
            return BindingTargetOutcome.UNKNOWN
        if resource is None:
            return BindingTargetOutcome.MISSING
        if resource.lifecycle_state is not ResourceLifecycleState.ACTIVE:
            return BindingTargetOutcome.INACTIVE
        return BindingTargetOutcome.ACTIVE
