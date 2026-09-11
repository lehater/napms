from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from napms.contexts.access_policy.domain.model import RuleSemanticIdentity


class ApplicationProjectionOutcome(str, Enum):
    RESOLVED = "Resolved"
    MISSING = "Missing"
    INVALID = "Invalid"
    UNKNOWN = "Unknown"


class ResourceRealizationOutcome(str, Enum):
    RESOLVED = "Resolved"
    MISSING = "Missing"
    STALE = "Stale"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class ResourceReference:
    value: str


@dataclass(frozen=True, slots=True)
class EndpointRealization:
    endpoint_reference: str
    technical_address: str


@dataclass(frozen=True, slots=True)
class ApplicationProjectionFact:
    outcome: ApplicationProjectionOutcome
    subject: RuleSemanticIdentity | None = None
    as_of: datetime | None = None
    source_resource_references: tuple[ResourceReference, ...] = ()
    destination_resource_references: tuple[ResourceReference, ...] = ()
    dcs_projection_payload: bytes | None = None
    fact_reference: str | None = None
    validity_reference: str | None = None
    provenance_reference: str | None = None


@dataclass(frozen=True, slots=True)
class ResourceRealizationFact:
    outcome: ResourceRealizationOutcome
    resource_reference: ResourceReference | None = None
    as_of: datetime | None = None
    endpoint_realizations: tuple[EndpointRealization, ...] = ()
    fact_reference: str | None = None
    validity_reference: str | None = None
    provenance_reference: str | None = None


class ApplicationCommunicationProjectionPort(Protocol):
    def resolve_projection(
        self,
        *,
        subject: RuleSemanticIdentity,
        as_of: datetime,
    ) -> ApplicationProjectionFact: ...


class ResourceCatalogueProjectionPort(Protocol):
    def resolve_realization(
        self,
        *,
        resource_reference: ResourceReference,
        as_of: datetime,
    ) -> ResourceRealizationFact: ...
