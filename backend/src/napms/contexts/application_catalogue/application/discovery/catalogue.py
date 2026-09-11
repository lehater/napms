from dataclasses import dataclass
from uuid import UUID

from napms.contexts.application_catalogue.application.ports import (
    ApplicationCatalogueCurationReadRepository,
)
from napms.contexts.application_catalogue.domain.model import (
    Application,
    CatalogueInvariantError,
    Component,
)


@dataclass(frozen=True, slots=True)
class ApplicationCataloguePage:
    items: tuple[Application, ...]
    page: int
    page_size: int
    has_more: bool


@dataclass(frozen=True, slots=True)
class ApplicationCatalogueDetail:
    application: Application
    components: tuple[Component, ...]


class ListApplicationCatalogue:
    def __init__(self, *, catalogue: ApplicationCatalogueCurationReadRepository) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        *,
        page: int = 1,
        page_size: int = 50,
        search: str | None = None,
        include_retired: bool = False,
    ) -> ApplicationCataloguePage:
        if page < 1:
            raise CatalogueInvariantError("page must be >= 1")
        if not 1 <= page_size <= 200:
            raise CatalogueInvariantError("page_size must be within 1..200")
        normalized_search = search.strip() if search and search.strip() else None
        offset = (page - 1) * page_size
        rows = self._catalogue.list_applications(
            offset=offset,
            limit=page_size + 1,
            search=normalized_search,
            include_retired=include_retired,
        )
        return ApplicationCataloguePage(
            items=rows[:page_size],
            page=page,
            page_size=page_size,
            has_more=len(rows) > page_size,
        )


class ReadApplicationCatalogueDetail:
    def __init__(self, *, catalogue: ApplicationCatalogueCurationReadRepository) -> None:
        self._catalogue = catalogue

    def execute(
        self,
        *,
        application_id: UUID,
        include_retired_components: bool = False,
    ) -> ApplicationCatalogueDetail | None:
        application = self._catalogue.get_application(application_id)
        if application is None:
            return None
        components = self._catalogue.list_components(
            application_id=application_id,
            include_retired=include_retired_components,
        )
        return ApplicationCatalogueDetail(
            application=application,
            components=tuple(
                sorted(
                    components,
                    key=lambda item: (item.display_name.casefold(), str(item.component_id)),
                )
            ),
        )
