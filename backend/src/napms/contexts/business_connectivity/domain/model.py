from __future__ import annotations

from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from uuid import UUID


class NeedStatus(str, Enum):
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


@dataclass(frozen=True)
class ConnectivityNeed:
    need_ref: UUID
    interaction_ref: UUID
    participant_component_ref: UUID
    business_basis: str
    status: NeedStatus
    created_by_subject: str
    retired_at: datetime | None = None

    @classmethod
    def declare(
        cls,
        *,
        need_ref: UUID,
        interaction_ref: UUID,
        participant_component_ref: UUID,
        business_basis: str,
        created_by_subject: str,
    ) -> ConnectivityNeed:
        business_basis = business_basis.strip()
        created_by_subject = created_by_subject.strip()
        if not business_basis:
            raise ValueError("business_basis must be non-empty")
        if not created_by_subject:
            raise ValueError("created_by_subject must be non-empty")
        return cls(
            need_ref=need_ref,
            interaction_ref=interaction_ref,
            participant_component_ref=participant_component_ref,
            business_basis=business_basis,
            status=NeedStatus.ACTIVE,
            created_by_subject=created_by_subject,
        )

    def retire(self, *, retired_at: datetime) -> ConnectivityNeed:
        if retired_at.tzinfo is None or retired_at.utcoffset() is None:
            raise ValueError("retired_at must be timezone-aware")
        if self.status is NeedStatus.RETIRED:
            return self
        return replace(self, status=NeedStatus.RETIRED, retired_at=retired_at)


@dataclass(frozen=True)
class BusinessProcess:
    process_ref: UUID
    name: str
    description: str | None
    organization_external_reference: str | None
    organization_display_name: str | None
    criticality_label: str | None
    version: int
    needs: tuple[ConnectivityNeed, ...] = ()

    @classmethod
    def register(
        cls,
        *,
        process_ref: UUID,
        name: str,
        description: str | None = None,
        criticality_label: str | None = None,
    ) -> BusinessProcess:
        name = name.strip()
        if not name:
            raise ValueError("process name must be non-empty")
        return cls(
            process_ref=process_ref,
            name=name,
            description=_optional_text(description),
            organization_external_reference=None,
            organization_display_name=None,
            criticality_label=_optional_text(criticality_label),
            version=1,
        )

    def set_responsible_organization(
        self,
        *,
        external_reference: str | None,
        display_name: str | None,
    ) -> BusinessProcess:
        return replace(
            self,
            organization_external_reference=_optional_text(external_reference),
            organization_display_name=_optional_text(display_name),
            version=self.version + 1,
        )

    def set_criticality_label(self, criticality_label: str | None) -> BusinessProcess:
        return replace(
            self,
            criticality_label=_optional_text(criticality_label),
            version=self.version + 1,
        )

    def add_need(self, need: ConnectivityNeed) -> BusinessProcess:
        if any(item.need_ref == need.need_ref for item in self.needs):
            raise ValueError("need_ref already exists")
        return replace(self, needs=self.needs + (need,), version=self.version + 1)

    def retire_need(self, need_ref: UUID, *, retired_at: datetime) -> BusinessProcess:
        found = False
        updated: list[ConnectivityNeed] = []
        for need in self.needs:
            if need.need_ref == need_ref:
                found = True
                updated.append(need.retire(retired_at=retired_at))
            else:
                updated.append(need)
        if not found:
            raise KeyError(str(need_ref))
        return replace(self, needs=tuple(updated), version=self.version + 1)

    def resolve_need(self, need_ref: UUID) -> ConnectivityNeed | None:
        return next((need for need in self.needs if need.need_ref == need_ref), None)


def _optional_text(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = value.strip()
    return normalized or None
