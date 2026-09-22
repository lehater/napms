from __future__ import annotations

from dataclasses import dataclass, replace
from uuid import UUID


@dataclass(frozen=True, order=True)
class PortRange:
    start: int
    end: int

    def __post_init__(self) -> None:
        if not 0 <= self.start <= self.end <= 65535:
            raise ValueError("port range must be within 0..65535")


@dataclass(frozen=True)
class TrafficClause:
    ip_protocol: int
    source_ports: tuple[PortRange, ...] = ()
    destination_ports: tuple[PortRange, ...] = ()

    def __post_init__(self) -> None:
        if not 0 <= self.ip_protocol <= 255:
            raise ValueError("ip_protocol must be within 0..255")
        if self.ip_protocol not in (6, 17) and (self.source_ports or self.destination_ports):
            raise ValueError("only TCP and UDP may carry port ranges")
        _require_canonical_ranges(self.source_ports)
        _require_canonical_ranges(self.destination_ports)


@dataclass(frozen=True)
class Component:
    component_ref: UUID
    name: str


@dataclass(frozen=True)
class Application:
    application_ref: UUID
    name: str
    version: int
    components: tuple[Component, ...] = ()

    @classmethod
    def create(cls, *, application_ref: UUID, name: str) -> Application:
        name = name.strip()
        if not name:
            raise ValueError("application name must be non-empty")
        return cls(application_ref=application_ref, name=name, version=1)

    def add_component(self, *, component_ref: UUID, name: str) -> Application:
        name = name.strip()
        if not name:
            raise ValueError("component name must be non-empty")
        if any(item.component_ref == component_ref for item in self.components):
            raise ValueError("component_ref already exists")
        return replace(
            self,
            components=self.components + (Component(component_ref=component_ref, name=name),),
            version=self.version + 1,
        )


@dataclass(frozen=True)
class InteractionRevision:
    revision_ref: UUID
    revision_no: int
    traffic_clauses: tuple[TrafficClause, ...]
    created_by_subject: str

    def __post_init__(self) -> None:
        if self.revision_no < 1:
            raise ValueError("revision_no must be positive")
        if not self.traffic_clauses:
            raise ValueError("interaction revision requires traffic clauses")
        if not self.created_by_subject.strip():
            raise ValueError("created_by_subject must be non-empty")


@dataclass(frozen=True)
class Interaction:
    interaction_ref: UUID
    source_component_ref: UUID
    destination_component_ref: UUID
    purpose: str | None
    version: int
    revisions: tuple[InteractionRevision, ...] = ()

    @classmethod
    def create(
        cls,
        *,
        interaction_ref: UUID,
        source_component_ref: UUID,
        destination_component_ref: UUID,
        purpose: str | None,
    ) -> Interaction:
        normalized_purpose = purpose.strip() if purpose is not None else None
        return cls(
            interaction_ref=interaction_ref,
            source_component_ref=source_component_ref,
            destination_component_ref=destination_component_ref,
            purpose=normalized_purpose or None,
            version=1,
        )

    def publish_revision(
        self,
        *,
        revision_ref: UUID,
        traffic_clauses: tuple[TrafficClause, ...],
        subject: str,
    ) -> Interaction:
        revision = InteractionRevision(
            revision_ref=revision_ref,
            revision_no=len(self.revisions) + 1,
            traffic_clauses=traffic_clauses,
            created_by_subject=subject,
        )
        return replace(
            self,
            revisions=self.revisions + (revision,),
            version=self.version + 1,
        )


def _require_canonical_ranges(ranges: tuple[PortRange, ...]) -> None:
    if tuple(sorted(ranges)) != ranges:
        raise ValueError("port ranges must be sorted")
    for previous, current in zip(ranges, ranges[1:]):
        if current.start <= previous.end + 1:
            raise ValueError("port ranges must be non-overlapping and non-adjacent")
