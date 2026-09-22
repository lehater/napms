from datetime import datetime, timezone
from uuid import UUID

import pytest

from napms.contexts.application_communication_catalogue.domain.model import Interaction
from napms.contexts.business_connectivity.application.queries import (
    BusinessProcessCataloguePage,
    BusinessProcessCatalogueQuery,
    BusinessProcessSortField,
    SortDirection,
)
from napms.contexts.business_connectivity.application.service import BusinessConnectivityService
from napms.contexts.business_connectivity.domain.model import BusinessProcess, NeedStatus


NOW = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)


class Processes:
    def __init__(self, process: BusinessProcess) -> None:
        self.process = process
        self.received_query: BusinessProcessCatalogueQuery | None = None

    def add(self, process: BusinessProcess) -> None:
        self.process = process

    def query_processes(
        self,
        query: BusinessProcessCatalogueQuery,
    ) -> BusinessProcessCataloguePage:
        self.received_query = query
        return BusinessProcessCataloguePage(
            items=(self.process,),
            total=1,
            page=query.page,
            page_size=query.page_size,
        )

    def get_process(self, process_ref: UUID) -> BusinessProcess | None:
        return self.process if self.process.process_ref == process_ref else None

    def save_process(self, process: BusinessProcess, *, expected_version: int) -> None:
        assert self.process.version == expected_version
        self.process = process


class Interactions:
    def __init__(self, interaction: Interaction) -> None:
        self.interaction = interaction

    def get_interaction(self, interaction_ref: UUID) -> Interaction | None:
        return self.interaction if self.interaction.interaction_ref == interaction_ref else None


def test_declare_need_requires_participant_to_be_interaction_endpoint() -> None:
    process = BusinessProcess.register(process_ref=UUID(int=1), name="Fulfillment")
    interaction = Interaction.create(
        interaction_ref=UUID(int=2),
        source_component_ref=UUID(int=3),
        destination_component_ref=UUID(int=4),
        purpose="orders",
    )
    service = BusinessConnectivityService(
        processes=Processes(process),
        interactions=Interactions(interaction),
        new_ref=lambda: UUID(int=5),
    )

    with pytest.raises(ValueError):
        service.declare_need(
            process_ref=process.process_ref,
            interaction_ref=interaction.interaction_ref,
            participant_component_ref=UUID(int=99),
            business_basis="Invalid participant",
            subject="subject:alice",
            expected_version=process.version,
        )

    updated = service.declare_need(
        process_ref=process.process_ref,
        interaction_ref=interaction.interaction_ref,
        participant_component_ref=interaction.source_component_ref,
        business_basis="Fulfillment requires orders",
        subject="subject:alice",
        expected_version=process.version,
    )
    assert updated.needs[0].participant_component_ref == interaction.source_component_ref


def test_retired_need_remains_resolvable_as_history_but_not_current() -> None:
    process = BusinessProcess.register(process_ref=UUID(int=10), name="Billing")
    interaction = Interaction.create(
        interaction_ref=UUID(int=11),
        source_component_ref=UUID(int=12),
        destination_component_ref=UUID(int=13),
        purpose="billing",
    )
    processes = Processes(process)
    refs = iter((UUID(int=14),))
    service = BusinessConnectivityService(
        processes=processes,
        interactions=Interactions(interaction),
        new_ref=lambda: next(refs),
    )
    process = service.declare_need(
        process_ref=process.process_ref,
        interaction_ref=interaction.interaction_ref,
        participant_component_ref=interaction.destination_component_ref,
        business_basis="Billing basis",
        subject="subject:alice",
        expected_version=process.version,
    )
    process = service.retire_need(
        process_ref=process.process_ref,
        need_ref=UUID(int=14),
        retired_at=NOW,
        expected_version=process.version,
    )

    historical = service.resolve_need_current_or_history(
        process_ref=process.process_ref,
        need_ref=UUID(int=14),
    )
    assert historical.status is NeedStatus.RETIRED
    with pytest.raises(Exception):
        service.lock_and_resolve_current_need(
            process_ref=process.process_ref,
            need_ref=UUID(int=14),
        )


def test_business_process_catalogue_query_is_delegated_without_reinterpretation() -> None:
    process = BusinessProcess.register(process_ref=UUID(int=20), name="Orders")
    processes = Processes(process)
    service = BusinessConnectivityService(
        processes=processes,
        interactions=Interactions(
            Interaction.create(
                interaction_ref=UUID(int=21),
                source_component_ref=UUID(int=22),
                destination_component_ref=UUID(int=23),
            )
        ),
    )
    query = BusinessProcessCatalogueQuery(
        search="Orders",
        criticality_label="HIGH",
        organization_external_reference="ORG-1",
        sort_by=BusinessProcessSortField.CRITICALITY_LABEL,
        sort_direction=SortDirection.DESC,
        page=2,
        page_size=10,
    )

    result = service.list_business_processes(query)

    assert processes.received_query == query
    assert result.items == (process,)
    assert result.total == 1
    assert result.page == 2
    assert result.page_size == 10
