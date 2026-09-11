from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True, slots=True)
class ResourceReferenceItem:
    resource_reference: str
    display_name: str | None
    effective_scope_references: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ResourceReferencePage:
    items: tuple[ResourceReferenceItem, ...]
    total: int


class ResourceReferenceQuery(Protocol):
    def page(
        self,
        *,
        candidate_resource_references: tuple[str, ...],
        as_of: datetime,
        search: str | None,
        scope_reference: str | None,
        sort: str,
        offset: int,
        limit: int,
    ) -> ResourceReferencePage: ...


class ReadResourceReferences:
    def __init__(self, *, query: ResourceReferenceQuery) -> None:
        self._query = query

    def page(self, **kwargs) -> ResourceReferencePage:
        return self._query.page(**kwargs)
