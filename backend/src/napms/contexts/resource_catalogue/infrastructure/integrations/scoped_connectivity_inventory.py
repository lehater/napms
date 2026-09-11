from collections import defaultdict

from napms.contexts.resource_catalogue.application.list_scope_resources import (
    ListResourcesInResponsibilityScope,
)
from napms.contexts.resource_catalogue.application.ports import (
    ResourceCataloguePersistenceError,
    ResourceCatalogueRepository,
)
from napms.contexts.resource_catalogue.domain.model import ResourceRealizationVersion
from napms.workflows.scoped_connectivity_inventory.application.model import (
    EndpointSnapshot,
    RealizationState,
    ResourceSnapshot,
)
from napms.workflows.scoped_connectivity_inventory.application.ports import (
    DependencyAvailability,
    LocalResourcePage,
    LocalResourceReadResult,
    ResourceResolutionResult,
)


def _snapshots(
    *,
    resource_references: tuple[str, ...],
    realizations: tuple[ResourceRealizationVersion, ...],
) -> tuple[ResourceSnapshot, ...]:
    by_resource: dict[str, list[ResourceRealizationVersion]] = defaultdict(list)
    for realization in realizations:
        by_resource[realization.resource_reference].append(realization)

    values = []
    for reference in resource_references:
        matches = by_resource.get(reference, [])
        if len(matches) == 1:
            realization = matches[0]
            values.append(
                ResourceSnapshot(
                    resource_reference=reference,
                    endpoints=tuple(
                        EndpointSnapshot(
                            endpoint_reference=endpoint.endpoint_reference,
                            technical_address=endpoint.technical_address,
                        )
                        for endpoint in sorted(realization.endpoint_realizations)
                    ),
                    realization_state=RealizationState.RESOLVED,
                )
            )
        elif len(matches) == 0:
            values.append(
                ResourceSnapshot(
                    resource_reference=reference,
                    endpoints=(),
                    realization_state=RealizationState.UNRESOLVED,
                )
            )
        else:
            values.append(
                ResourceSnapshot(
                    resource_reference=reference,
                    endpoints=(),
                    realization_state=RealizationState.UNKNOWN,
                )
            )
    return tuple(values)


class ResourceCatalogueScopedConnectivityAdapter:
    def __init__(
        self,
        *,
        lister: ListResourcesInResponsibilityScope,
        catalogue: ResourceCatalogueRepository,
    ) -> None:
        self._lister = lister
        self._catalogue = catalogue

    def list_local_resources(
        self,
        *,
        responsibility_scope,
        as_of,
        page,
        page_size,
        search,
    ) -> LocalResourceReadResult:
        try:
            listed = self._lister.execute(
                responsibility_scope=responsibility_scope,
                as_of=as_of,
                page=page,
                page_size=page_size,
                search=search,
            )
            realizations = self._catalogue.find_effective_realizations_for_resources(
                resource_references=listed.resource_references,
                as_of=as_of,
            )
        except ResourceCataloguePersistenceError:
            return LocalResourceReadResult(DependencyAvailability.UNAVAILABLE)

        return LocalResourceReadResult(
            DependencyAvailability.AVAILABLE,
            LocalResourcePage(
                resources=_snapshots(
                    resource_references=listed.resource_references,
                    realizations=realizations,
                ),
                page=listed.page,
                page_size=listed.page_size,
                has_more=listed.has_more,
            ),
        )

    def resolve_resources(
        self,
        *,
        resource_references,
        as_of,
    ) -> ResourceResolutionResult:
        unique = tuple(dict.fromkeys(resource_references))
        try:
            realizations = self._catalogue.find_effective_realizations_for_resources(
                resource_references=unique,
                as_of=as_of,
            )
        except ResourceCataloguePersistenceError:
            return ResourceResolutionResult(DependencyAvailability.UNAVAILABLE)

        return ResourceResolutionResult(
            DependencyAvailability.AVAILABLE,
            _snapshots(
                resource_references=unique,
                realizations=realizations,
            ),
        )
