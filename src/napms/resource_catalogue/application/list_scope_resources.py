from dataclasses import dataclass
from datetime import datetime

from napms.resource_catalogue.application.ports import (
    ResourceScopeAffiliationRepository,
)
from napms.resource_catalogue.domain.model import (
    ResourceCatalogueInvariantError,
)


@dataclass(frozen=True, slots=True)
class ResourceScopePage:
    resource_references: tuple[str, ...]
    page: int
    page_size: int
    has_more: bool


def _require_aware(value: datetime) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ResourceCatalogueInvariantError("as_of must be offset-aware")


class ListResourcesInResponsibilityScope:
    def __init__(self, *, affiliations: ResourceScopeAffiliationRepository) -> None:
        self._affiliations = affiliations

    def execute(
        self,
        *,
        responsibility_scope: str,
        as_of: datetime,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
    ) -> ResourceScopePage:
        if not responsibility_scope:
            raise ResourceCatalogueInvariantError(
                "responsibility_scope must be non-empty"
            )
        _require_aware(as_of)
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        normalized_search = search.strip() if search is not None else None
        if normalized_search == "":
            normalized_search = None
        if normalized_search is not None and len(normalized_search) > 256:
            raise ValueError("search must be at most 256 characters")

        rows = self._affiliations.list_effective_for_scope(
            responsibility_scope=responsibility_scope,
            as_of=as_of,
            offset=(page - 1) * page_size,
            limit=page_size + 1,
            search=normalized_search,
        )

        unique_refs = tuple(
            dict.fromkeys(
                row.resource_reference
                for row in rows
                if (
                    row.responsibility_scope == responsibility_scope
                    and row.is_effective_at(as_of)
                )
            )
        )
        visible = unique_refs[:page_size]
        return ResourceScopePage(
            resource_references=visible,
            page=page,
            page_size=page_size,
            has_more=len(unique_refs) > page_size,
        )
