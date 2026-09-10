from datetime import datetime
from typing import Protocol

from napms.traffic_analysis.application.model import (
    EndpointResolution,
    EvidenceSnapshot,
    NetworkContextView,
    PolicyMatch,
    ResponsibilityItem,
    TrafficAnalysisQuery,
)


class TechnicalEndpointResolutionPort(Protocol):
    def resolve(self, *, address: str, as_of: datetime) -> EndpointResolution: ...


class TrafficPolicyProjectionPort(Protocol):
    def find_matches(
        self,
        *,
        actor_id: str,
        query: TrafficAnalysisQuery,
        source: EndpointResolution,
        destination: EndpointResolution,
    ) -> tuple[PolicyMatch, ...]: ...


class NetworkContextProjectionPort(Protocol):
    def read(
        self,
        *,
        query: TrafficAnalysisQuery,
    ) -> NetworkContextView: ...


class ConfiguredEvidenceProjectionPort(Protocol):
    def latest_applicable(
        self,
        *,
        query: TrafficAnalysisQuery,
        provider_namespace: str,
        device_reference: str,
    ) -> EvidenceSnapshot | None: ...


class ResourceResponsibilityProjectionPort(Protocol):
    def list_for_resources(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
    ) -> tuple[ResponsibilityItem, ...]: ...
