from datetime import datetime, timezone

from napms.resource_catalogue.domain.responsibility import (
    ResourceResponsibility,
    ResourceResponsibilityRole,
    ResponsiblePartyKind,
)


_VALID_FROM = datetime(2020, 1, 1, tzinfo=timezone.utc)


class LocalDemoResourceResponsibilityAdapter:
    """Deterministic local-only responsibility source for the supported demo target."""

    _ROWS = (
        ResourceResponsibility(
            assignment_reference="local-demo:responsibility:source:service-owner",
            resource_reference="local-demo-source",
            party_reference="local-demo:team:application",
            party_kind=ResponsiblePartyKind.TEAM,
            role=ResourceResponsibilityRole.SERVICE_OWNER,
            display_name="Demo Application Team",
            contact="demo-app-ops",
            valid_from=_VALID_FROM,
            valid_to=None,
            provenance_reference="local-demo:responsibility-source",
        ),
        ResourceResponsibility(
            assignment_reference="local-demo:responsibility:source:operations",
            resource_reference="local-demo-source",
            party_reference="local-demo:team:application-ops",
            party_kind=ResponsiblePartyKind.TEAM,
            role=ResourceResponsibilityRole.OPERATIONS_CONTACT,
            display_name="Demo Application Operations",
            contact="demo-app-ops",
            valid_from=_VALID_FROM,
            valid_to=None,
            provenance_reference="local-demo:responsibility-source",
        ),
        ResourceResponsibility(
            assignment_reference="local-demo:responsibility:destination:service-owner",
            resource_reference="local-demo-destination",
            party_reference="local-demo:team:orders",
            party_kind=ResponsiblePartyKind.TEAM,
            role=ResourceResponsibilityRole.SERVICE_OWNER,
            display_name="Demo Orders Team",
            contact="demo-orders-ops",
            valid_from=_VALID_FROM,
            valid_to=None,
            provenance_reference="local-demo:responsibility-source",
        ),
    )

    def list_effective_for_resources(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
    ) -> tuple[ResourceResponsibility, ...]:
        selected = set(resource_references)
        return tuple(
            item
            for item in self._ROWS
            if item.resource_reference in selected and item.is_effective_at(as_of)
        )
