from datetime import datetime
from typing import Protocol

from napms.resource_catalogue.domain.model import ResourceRealizationVersion


class ResourceCataloguePersistenceError(Exception):
    """Resource Catalogue persistence failed without a trustworthy result."""


class ResourceCatalogueRepository(Protocol):
    def find_effective_realizations(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> tuple[ResourceRealizationVersion, ...]: ...

    def has_realization_facts(self, *, resource_reference: str) -> bool: ...
