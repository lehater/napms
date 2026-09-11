from napms.contexts.resource_catalogue.application.responsibility import ReadResourceResponsibilities
from napms.traffic_analysis.application.model import ResponsibilityItem


class ResourceResponsibilityTrafficAnalysisAdapter:
    def __init__(self, *, reader: ReadResourceResponsibilities) -> None:
        self._reader = reader

    def list_for_resources(self, *, resource_references, as_of):
        return tuple(
            ResponsibilityItem(
                resource_reference=item.resource_reference,
                role=item.role.value,
                party_reference=item.party_reference,
                party_kind=item.party_kind.value,
                display_name=item.display_name,
                contact=item.contact,
                provenance_reference=item.provenance_reference,
            )
            for item in self._reader.execute(
                resource_references=resource_references,
                as_of=as_of,
            )
        )
