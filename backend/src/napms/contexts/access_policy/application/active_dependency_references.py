from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID


@dataclass(frozen=True, slots=True)
class AccessRuleDependencySubject:
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    dcs_contract_revision_id: UUID


class AccessRuleDependencyQuery(Protocol):
    def page(self, *, subjects, as_of, offset, limit) -> tuple[int, tuple[str, ...]]: ...


class ReadActiveAccessRuleReferences:
    def __init__(self, *, query: AccessRuleDependencyQuery) -> None:
        self._query = query

    def page(
        self,
        *,
        subjects: tuple[AccessRuleDependencySubject, ...],
        as_of: datetime,
        offset: int,
        limit: int,
    ) -> tuple[int, tuple[str, ...]]:
        return self._query.page(
            subjects=subjects, as_of=as_of, offset=offset, limit=limit
        )
