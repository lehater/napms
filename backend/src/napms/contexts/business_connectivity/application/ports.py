from __future__ import annotations

from typing import Protocol
from uuid import UUID

from napms.contexts.business_connectivity.application.queries import (
    BusinessProcessCataloguePage,
    BusinessProcessCatalogueQuery,
)
from napms.contexts.business_connectivity.domain.model import BusinessProcess, ConnectivityNeed


class BusinessConnectivityNotFound(Exception):
    pass


class BusinessConnectivityVersionConflict(Exception):
    pass


class BusinessProcessRepository(Protocol):
    def add(self, process: BusinessProcess) -> None: ...

    def query_processes(
        self,
        query: BusinessProcessCatalogueQuery,
    ) -> BusinessProcessCataloguePage: ...

    def get_process(self, process_ref: UUID) -> BusinessProcess | None: ...

    def save_process(self, process: BusinessProcess, *, expected_version: int) -> None: ...


class CurrentNeedLocker(Protocol):
    def lock_current_need(self, need_ref: UUID) -> tuple[ConnectivityNeed, int] | None: ...
