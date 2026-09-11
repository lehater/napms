from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from napms.contexts.application_catalogue.domain.model import CatalogueInvariantError


@dataclass(frozen=True, slots=True)
class ApplicationCatalogueParticipant:
    application_id: UUID
    application_display_name: str
    component_id: UUID
    component_display_name: str
    component_deployment_id: UUID
    deployment_display_name: str | None


@dataclass(frozen=True, slots=True)
class ApplicationCatalogueParticipantPage:
    items: tuple[ApplicationCatalogueParticipant, ...]
    page: int
    page_size: int
    has_more: bool


class ApplicationCatalogueParticipantReadPort(Protocol):
    def list_active_participants(
        self,
        *,
        offset: int,
        limit: int,
        search: str | None,
    ) -> tuple[ApplicationCatalogueParticipant, ...]: ...


class ListApplicationCatalogueParticipants:
    """Discover Active deployment participants without exposing arbitrary UUID entry."""

    def __init__(self, *, catalogue: ApplicationCatalogueParticipantReadPort) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
    ) -> ApplicationCatalogueParticipantPage:
        if page < 1:
            raise CatalogueInvariantError("page must be >= 1")
        if not 1 <= page_size <= 200:
            raise CatalogueInvariantError("page_size must be within 1..200")
        normalized_search = search.strip() if search and search.strip() else None
        rows = self._catalogue.list_active_participants(
            offset=(page - 1) * page_size,
            limit=page_size + 1,
            search=normalized_search,
        )
        return ApplicationCatalogueParticipantPage(
            items=rows[:page_size],
            page=page,
            page_size=page_size,
            has_more=len(rows) > page_size,
        )
