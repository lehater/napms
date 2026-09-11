from napms.application_catalogue.application.ports import ApplicationCatalogueRepository
from napms.resource_catalogue.application.resolve_address import (
    ResolveResourcesByTechnicalAddress,
    TechnicalAddressResolutionOutcome,
)
from napms.traffic_analysis.application.model import (
    EndpointResolution,
    ResolvedResource,
    ResolutionState,
)


class ResourceCatalogueTrafficEndpointAdapter:
    def __init__(
        self,
        *,
        resolver: ResolveResourcesByTechnicalAddress,
        catalogue: ApplicationCatalogueRepository,
    ) -> None:
        self._resolver = resolver
        self._catalogue = catalogue

    def resolve(self, *, address: str, as_of):
        resolved = self._resolver.execute(technical_address=address, as_of=as_of)
        state = {
            TechnicalAddressResolutionOutcome.RESOLVED: ResolutionState.RESOLVED,
            TechnicalAddressResolutionOutcome.AMBIGUOUS: ResolutionState.AMBIGUOUS,
            TechnicalAddressResolutionOutcome.HISTORICAL: ResolutionState.HISTORICAL,
            TechnicalAddressResolutionOutcome.UNKNOWN: ResolutionState.UNKNOWN,
        }[resolved.outcome]

        resource_refs = tuple(
            dict.fromkeys(item.resource_reference for item in resolved.matches)
        )
        bindings = self._catalogue.find_effective_bindings_for_resources(
            resource_references=resource_refs,
            as_of=as_of,
        ) if resource_refs else ()
        deployment_ids = tuple(
            dict.fromkeys(item.component_deployment_id for item in bindings)
        )
        deployments = self._catalogue.get_component_deployments(deployment_ids) if deployment_ids else ()
        names = {
            item.deployment_id: item.display_name or str(item.deployment_id)
            for item in deployments
        }
        component_names_by_resource: dict[str, list[str]] = {
            item: [] for item in resource_refs
        }
        for binding in bindings:
            name = names.get(binding.component_deployment_id)
            if name is not None:
                component_names_by_resource.setdefault(binding.resource_reference, []).append(name)

        resources = tuple(
            ResolvedResource(
                resource_reference=item.resource_reference,
                endpoint_reference=item.endpoint_reference,
                technical_address=item.technical_address,
                component_names=tuple(
                    sorted(set(component_names_by_resource.get(item.resource_reference, ())))
                ),
                provenance_references=(item.provenance_reference,),
            )
            for item in resolved.matches
        )
        return EndpointResolution(state=state, address=address, resources=resources)
