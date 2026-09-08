from dataclasses import dataclass

from napms.application_catalogue.application.ports import ApplicationCatalogueRepository
from napms.application_catalogue.domain.model import DirectedInteractionIdentity


@dataclass(frozen=True, slots=True)
class DirectedInteractionPage:
    items: tuple[DirectedInteractionIdentity, ...]
    page: int
    page_size: int
    has_more: bool


class ListDirectedInteractions:
    def __init__(self, *, catalogue: ApplicationCatalogueRepository) -> None:
        self._catalogue = catalogue

    def execute(self, *, page: int = 1, page_size: int = 50) -> DirectedInteractionPage:
        if page < 1:
            raise ValueError("page must be >= 1")
        if page_size < 1 or page_size > 100:
            raise ValueError("page_size must be between 1 and 100")

        rows = self._catalogue.list_dcs_revisions(
            offset=(page - 1) * page_size,
            limit=page_size + 1,
        )
        visible = rows[:page_size]
        return DirectedInteractionPage(
            items=tuple(
                DirectedInteractionIdentity(
                    source_component_deployment_id=row.source_component_deployment_id,
                    destination_component_deployment_id=row.destination_component_deployment_id,
                    dcs_contract_revision_id=row.revision_id,
                )
                for row in visible
            ),
            page=page,
            page_size=page_size,
            has_more=len(rows) > page_size,
        )
