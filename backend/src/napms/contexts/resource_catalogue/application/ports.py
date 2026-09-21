from __future__ import annotations

from datetime import datetime
from typing import Protocol
from uuid import UUID

from napms.contexts.resource_catalogue.domain.model import Resource


RESOURCE_CATALOGUE_CURATION_ACTION = "CurateResourceCatalogue"
RESOURCE_CATALOGUE_AUTHORITY_SCOPE = "resource-catalogue"


class AuthorityDenied(Exception):
    pass


class ResourceNotFound(Exception):
    pass


class ResourceVersionConflict(Exception):
    pass


class ResourceCatalogueRepository(Protocol):
    def add(self, resource: Resource) -> None: ...

    def get(self, resource_ref: UUID) -> Resource | None: ...

    def save(self, resource: Resource, *, expected_version: int) -> None: ...


class ResourceCatalogueAuthority(Protocol):
    def require(
        self,
        *,
        principal: str,
        action: str,
        scope: str,
        evaluated_at: datetime,
    ) -> None: ...
