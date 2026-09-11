from napms.contexts.application_catalogue.infrastructure.integrations.dcs_json_codec import (
    JsonDcsProjectionCodec,
)
from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueRepository,
    CataloguePersistenceError,
)
from napms.workflows.policy_export.application.normalization_ports import (
    DcsProjectionDecodeError,
)
from napms.workflows.policy_export.application.normalization_types import (
    PortConstraintKind,
)
from napms.scoped_connectivity_inventory.application.model import (
    BoundComponentSnapshot,
    ComponentResourceBindingSnapshot,
    InteractionIdentity,
    InteractionSnapshot,
)
from napms.scoped_connectivity_inventory.application.ports import (
    BoundComponentReadResult,
    ComponentResourceBindingReadResult,
    DependencyAvailability,
    InteractionReadResult,
)


_MAX_SCOPED_CHILD_ROWS = 2000


def _constraint_text(value) -> str:
    if value.kind is PortConstraintKind.ANY:
        return "any"
    if value.kind is PortConstraintKind.NOT_APPLICABLE:
        return "-"
    return ",".join(
        str(item.first) if item.first == item.last else f"{item.first}-{item.last}"
        for item in value.ranges
    )


def _traffic_summary(codec: JsonDcsProjectionCodec, payload: bytes) -> str | None:
    try:
        alternatives = codec.decode(payload)
    except DcsProjectionDecodeError:
        return None

    parts = []
    for alternative in alternatives:
        destination = _constraint_text(alternative.destination_ports)
        if destination == "-":
            parts.append(alternative.protocol)
        else:
            parts.append(f"{alternative.protocol} {destination}")
    return " | ".join(parts) if parts else None


class ApplicationCatalogueScopedConnectivityAdapter:
    def __init__(
        self,
        *,
        catalogue: ApplicationCatalogueRepository,
        decoder: JsonDcsProjectionCodec | None = None,
    ) -> None:
        self._catalogue = catalogue
        self._decoder = decoder or JsonDcsProjectionCodec()

    def list_bound_components(
        self,
        *,
        resource_references,
        as_of,
    ) -> BoundComponentReadResult:
        unique_refs = tuple(dict.fromkeys(resource_references))
        try:
            bindings = self._catalogue.find_effective_bindings_for_resources(
                resource_references=unique_refs,
                as_of=as_of,
                limit=_MAX_SCOPED_CHILD_ROWS + 1,
            )
            if len(bindings) > _MAX_SCOPED_CHILD_ROWS:
                return BoundComponentReadResult(
                    DependencyAvailability.UNAVAILABLE
                )
            component_ids = tuple(
                dict.fromkeys(
                    binding.component_deployment_id for binding in bindings
                )
            )
            deployments = self._catalogue.get_component_deployments(component_ids)
        except CataloguePersistenceError:
            return BoundComponentReadResult(DependencyAvailability.UNAVAILABLE)

        display_names = {
            deployment.deployment_id: deployment.display_name
            for deployment in deployments
        }
        items = tuple(
            BoundComponentSnapshot(
                resource_reference=binding.resource_reference,
                component_deployment_id=binding.component_deployment_id,
                display_name=display_names.get(binding.component_deployment_id),
            )
            for binding in bindings
        )
        return BoundComponentReadResult(DependencyAvailability.AVAILABLE, items)

    def list_interactions_for_components(
        self,
        *,
        component_deployment_ids,
    ) -> InteractionReadResult:
        unique_ids = tuple(dict.fromkeys(component_deployment_ids))
        try:
            revisions = self._catalogue.list_dcs_revisions_for_components(
                component_deployment_ids=unique_ids,
                limit=_MAX_SCOPED_CHILD_ROWS + 1,
            )
            if len(revisions) > _MAX_SCOPED_CHILD_ROWS:
                return InteractionReadResult(
                    DependencyAvailability.UNAVAILABLE
                )
            all_deployment_ids = tuple(
                dict.fromkeys(
                    deployment_id
                    for revision in revisions
                    for deployment_id in (
                        revision.source_component_deployment_id,
                        revision.destination_component_deployment_id,
                    )
                )
            )
            deployments = self._catalogue.get_component_deployments(
                all_deployment_ids
            )
        except CataloguePersistenceError:
            return InteractionReadResult(DependencyAvailability.UNAVAILABLE)

        display_names = {
            deployment.deployment_id: deployment.display_name
            for deployment in deployments
        }
        return InteractionReadResult(
            DependencyAvailability.AVAILABLE,
            tuple(
                InteractionSnapshot(
                    identity=InteractionIdentity(
                        revision.source_component_deployment_id,
                        revision.destination_component_deployment_id,
                        revision.revision_id,
                    ),
                    source_display_name=display_names.get(
                        revision.source_component_deployment_id
                    ),
                    destination_display_name=display_names.get(
                        revision.destination_component_deployment_id
                    ),
                    dcs_display_name=revision.display_name,
                    access_summary=_traffic_summary(
                        self._decoder,
                        revision.projection_payload,
                    ),
                )
                for revision in revisions
            ),
        )

    def list_resource_bindings_for_components(
        self,
        *,
        component_deployment_ids,
        as_of,
    ) -> ComponentResourceBindingReadResult:
        unique_ids = tuple(dict.fromkeys(component_deployment_ids))
        try:
            bindings = self._catalogue.find_effective_bindings_for_components(
                component_deployment_ids=unique_ids,
                as_of=as_of,
                limit=_MAX_SCOPED_CHILD_ROWS + 1,
            )
            if len(bindings) > _MAX_SCOPED_CHILD_ROWS:
                return ComponentResourceBindingReadResult(
                    DependencyAvailability.UNAVAILABLE
                )
        except CataloguePersistenceError:
            return ComponentResourceBindingReadResult(
                DependencyAvailability.UNAVAILABLE
            )
        return ComponentResourceBindingReadResult(
            DependencyAvailability.AVAILABLE,
            tuple(
                ComponentResourceBindingSnapshot(
                    component_deployment_id=binding.component_deployment_id,
                    resource_reference=binding.resource_reference,
                )
                for binding in bindings
            ),
        )
