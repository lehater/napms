from datetime import datetime
from typing import Protocol

from napms.contexts.resource_catalogue.domain.model import ResourceCatalogueInvariantError
from napms.contexts.resource_catalogue.domain.responsibility import ResourceResponsibility


class ResourceResponsibilityPort(Protocol):
    def list_effective_for_resources(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
    ) -> tuple[ResourceResponsibility, ...]: ...


class ReadResourceResponsibilities:
    def __init__(self, *, responsibilities: ResourceResponsibilityPort) -> None:
        self._responsibilities = responsibilities

    def execute(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
    ) -> tuple[ResourceResponsibility, ...]:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ResourceCatalogueInvariantError("as_of must be offset-aware")
        normalized = tuple(sorted({item.strip() for item in resource_references if item.strip()}))
        if not normalized:
            return ()
        rows = self._responsibilities.list_effective_for_resources(
            resource_references=normalized,
            as_of=as_of,
        )
        return tuple(
            sorted(
                (item for item in rows if item.is_effective_at(as_of)),
                key=lambda item: (
                    item.resource_reference,
                    item.role.value,
                    item.display_name,
                    item.assignment_reference,
                ),
            )
        )
