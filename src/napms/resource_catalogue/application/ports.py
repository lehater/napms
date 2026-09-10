from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol

from napms.resource_catalogue.domain.model import (
    Resource,
    ResourceRealizationVersion,
    ResourceScopeAffiliation,
)
from napms.resource_catalogue.domain.responsibility import ResourceResponsibility


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

    def new_realization_reference(self) -> str: ...

    def new_endpoint_reference(self) -> str: ...

    def new_scope_affiliation_reference(self) -> str: ...

    def new_responsibility_reference(self) -> str: ...


class ResourceCatalogueProvenanceFactory(Protocol):
    def for_resource(
        self,
        *,
        resource_reference: str,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_resource_retirement(
        self,
        *,
        resource_reference: str,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_realization(
        self,
        *,
        fact_reference: str,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_realization_end(
        self,
        *,
        fact_reference: str,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_scope_affiliation(
        self,
        *,
        affiliation_reference: str,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_scope_affiliation_end(
        self,
        *,
        affiliation_reference: str,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_responsibility(
        self,
        *,
        assignment_reference: str,
        actor_id: str,
        authority_reference: str,
        effective_time: datetime,
    ) -> str: ...

    def for_responsibility_end(
        self,
        *,
        assignment_reference: str,
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

    def get_realization(
        self,
        fact_reference: str,
    ) -> ResourceRealizationVersion | None: ...

    def find_overlapping_realizations(
        self,
        *,
        resource_reference: str,
        valid_from: datetime,
        valid_to: datetime | None,
    ) -> tuple[ResourceRealizationVersion, ...]: ...

    def add_realization(self, realization: ResourceRealizationVersion) -> None: ...

    def save_realization(
        self,
        realization: ResourceRealizationVersion,
        *,
        expected_version: int,
    ) -> None: ...

    def get_scope_affiliation(
        self,
        affiliation_reference: str,
    ) -> ResourceScopeAffiliation | None: ...

    def find_overlapping_scope_affiliations(
        self,
        *,
        resource_reference: str,
        responsibility_scope: str,
        valid_from: datetime,
        valid_to: datetime | None,
    ) -> tuple[ResourceScopeAffiliation, ...]: ...

    def add_scope_affiliation(self, affiliation: ResourceScopeAffiliation) -> None: ...

    def save_scope_affiliation(
        self,
        affiliation: ResourceScopeAffiliation,
        *,
        expected_version: int,
    ) -> None: ...

    def get_responsibility(
        self,
        assignment_reference: str,
    ) -> ResourceResponsibility | None: ...

    def add_responsibility(self, responsibility: ResourceResponsibility) -> None: ...

    def save_responsibility(
        self,
        responsibility: ResourceResponsibility,
        *,
        expected_version: int,
    ) -> None: ...

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
