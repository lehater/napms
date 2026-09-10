from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from napms.resource_catalogue.domain.model import (
    Resource,
    ResourceRealizationVersion,
    ResourceScopeAffiliation,
)


RESOURCE_CATALOGUE_CURATION_ACTION = "CurateResourceCatalogue"
RESOURCE_CATALOGUE_AUTHORITY_SCOPE = "resource-catalogue"


class ResourceCataloguePersistenceError(Exception):
    """Resource Catalogue persistence failed without a trustworthy result."""


class ResourceCataloguePersistenceOutcomeUnknown(ResourceCataloguePersistenceError):
    """Commit acknowledgement failed, so authoritative outcome is uncertain."""


class ResourceCatalogueConcurrencyConflict(ResourceCataloguePersistenceError):
    """Optimistic concurrency precondition did not match authoritative state."""


class ResourceCatalogueIdempotencyConflict(ResourceCataloguePersistenceError):
    """Another command won the same idempotency-key uniqueness boundary."""


class ResourceCatalogueAuthorityOutcome(str, Enum):
    PERMITTED = "Permitted"
    DENIED = "Denied"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class ResourceCatalogueAuthorityCheck:
    outcome: ResourceCatalogueAuthorityOutcome
    authority_reference: str | None = None


class ResourceCatalogueCurationAuthorityPort(Protocol):
    def check_curation(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
    ) -> ResourceCatalogueAuthorityCheck: ...


@dataclass(frozen=True, slots=True)
class ResourceCatalogueCommandReceipt:
    command_kind: str
    request_fingerprint: str
    result_reference: str
    result_version: int


class ResourceCatalogueIdentityFactory(Protocol):
    def new_resource_reference(self) -> str: ...


class ResourceCatalogueProvenanceFactory(Protocol):
    def for_resource(
        self,
        *,
        resource_reference: str,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...


class ResourceCatalogueCurationRepository(Protocol):
    def get_resource(self, resource_reference: str) -> Resource | None: ...

    def find_command_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
    ) -> ResourceCatalogueCommandReceipt | None: ...

    def add_resource(self, resource: Resource) -> None: ...

    def save_resource(
        self,
        resource: Resource,
        *,
        expected_version: int,
    ) -> None: ...

    def has_effective_scope_affiliations(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> bool: ...

    def has_effective_responsibilities(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> bool: ...

    def record_command_receipt(
        self,
        *,
        actor_id: str,
        idempotency_key: str,
        receipt: ResourceCatalogueCommandReceipt,
    ) -> None: ...

    def commit(self) -> None: ...


class ResourceCatalogueRepository(Protocol):
    def find_effective_realizations(
        self,
        *,
        resource_reference: str,
        as_of: datetime,
    ) -> tuple[ResourceRealizationVersion, ...]: ...

    def has_realization_facts(self, *, resource_reference: str) -> bool: ...

    def find_effective_realizations_for_resources(
        self,
        *,
        resource_references: tuple[str, ...],
        as_of: datetime,
    ) -> tuple[ResourceRealizationVersion, ...]: ...

    def find_resources_with_realization_facts(
        self,
        *,
        resource_references: tuple[str, ...],
    ) -> tuple[str, ...]: ...

    def find_effective_realizations_by_address(
        self,
        *,
        technical_address: str,
        as_of: datetime,
    ) -> tuple[ResourceRealizationVersion, ...]: ...

    def has_realization_facts_for_address(
        self,
        *,
        technical_address: str,
    ) -> bool: ...


class ResourceScopeAffiliationRepository(Protocol):
    def list_effective_for_scope(
        self,
        *,
        responsibility_scope: str,
        as_of: datetime,
        offset: int,
        limit: int,
        search: str | None = None,
    ) -> tuple[ResourceScopeAffiliation, ...]: ...
