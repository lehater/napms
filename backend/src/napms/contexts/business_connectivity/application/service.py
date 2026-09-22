from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from uuid import UUID, uuid4

from napms.contexts.application_communication_catalogue.application.ports import (
    InteractionResolver,
)
from napms.contexts.business_connectivity.application.queries import (
    BusinessProcessCataloguePage,
    BusinessProcessCatalogueQuery,
)
from napms.contexts.business_connectivity.application.ports import (
    BusinessConnectivityNotFound,
    BusinessConnectivityVersionConflict,
    BusinessProcessRepository,
)
from napms.contexts.business_connectivity.domain.model import (
    BusinessProcess,
    ConnectivityNeed,
    NeedStatus,
)


class BusinessConnectivityService:
    def __init__(
        self,
        *,
        processes: BusinessProcessRepository,
        interactions: InteractionResolver,
        new_ref: Callable[[], UUID] = uuid4,
    ) -> None:
        self._processes = processes
        self._interactions = interactions
        self._new_ref = new_ref

    def list_business_processes(
        self,
        query: BusinessProcessCatalogueQuery,
    ) -> BusinessProcessCataloguePage:
        return self._processes.query_processes(query)

    def resolve_business_process(self, process_ref: UUID) -> BusinessProcess:
        return self._required_process(process_ref)

    def register_business_process(
        self,
        *,
        name: str,
        description: str | None = None,
        criticality_label: str | None = None,
    ) -> BusinessProcess:
        process = BusinessProcess.register(
            process_ref=self._new_ref(),
            name=name,
            description=description,
            criticality_label=criticality_label,
        )
        self._processes.add(process)
        return process

    def set_responsible_organization(
        self,
        *,
        process_ref: UUID,
        external_reference: str | None,
        display_name: str | None,
        expected_version: int,
    ) -> BusinessProcess:
        return self._change(
            process_ref=process_ref,
            expected_version=expected_version,
            transform=lambda process: process.set_responsible_organization(
                external_reference=external_reference,
                display_name=display_name,
            ),
        )

    def set_criticality_label(
        self,
        *,
        process_ref: UUID,
        criticality_label: str | None,
        expected_version: int,
    ) -> BusinessProcess:
        return self._change(
            process_ref=process_ref,
            expected_version=expected_version,
            transform=lambda process: process.set_criticality_label(criticality_label),
        )

    def declare_need(
        self,
        *,
        process_ref: UUID,
        interaction_ref: UUID,
        participant_component_ref: UUID,
        business_basis: str,
        subject: str,
        expected_version: int,
    ) -> BusinessProcess:
        interaction = self._interactions.get_interaction(interaction_ref)
        if interaction is None:
            raise BusinessConnectivityNotFound(str(interaction_ref))
        if participant_component_ref not in (
            interaction.source_component_ref,
            interaction.destination_component_ref,
        ):
            raise ValueError("participant_component_ref must be an Interaction endpoint")
        need = ConnectivityNeed.declare(
            need_ref=self._new_ref(),
            interaction_ref=interaction_ref,
            participant_component_ref=participant_component_ref,
            business_basis=business_basis,
            created_by_subject=subject,
        )
        return self._change(
            process_ref=process_ref,
            expected_version=expected_version,
            transform=lambda process: process.add_need(need),
        )

    def retire_need(
        self,
        *,
        process_ref: UUID,
        need_ref: UUID,
        retired_at: datetime,
        expected_version: int,
    ) -> BusinessProcess:
        return self._change(
            process_ref=process_ref,
            expected_version=expected_version,
            transform=lambda process: process.retire_need(
                need_ref,
                retired_at=retired_at,
            ),
        )

    def lock_and_resolve_current_need(
        self,
        *,
        process_ref: UUID,
        need_ref: UUID,
    ) -> tuple[ConnectivityNeed, int]:
        process = self._required_process(process_ref)
        need = process.resolve_need(need_ref)
        if need is None or need.status is not NeedStatus.ACTIVE:
            raise BusinessConnectivityNotFound(str(need_ref))
        return need, process.version

    def resolve_need_current_or_history(
        self,
        *,
        process_ref: UUID,
        need_ref: UUID,
    ) -> ConnectivityNeed:
        process = self._required_process(process_ref)
        need = process.resolve_need(need_ref)
        if need is None:
            raise BusinessConnectivityNotFound(str(need_ref))
        return need

    def _required_process(self, process_ref: UUID) -> BusinessProcess:
        process = self._processes.get_process(process_ref)
        if process is None:
            raise BusinessConnectivityNotFound(str(process_ref))
        return process

    def _change(
        self,
        *,
        process_ref: UUID,
        expected_version: int,
        transform: Callable[[BusinessProcess], BusinessProcess],
    ) -> BusinessProcess:
        process = self._required_process(process_ref)
        if process.version != expected_version:
            raise BusinessConnectivityVersionConflict(str(process_ref))
        updated = transform(process)
        self._processes.save_process(updated, expected_version=expected_version)
        return updated
