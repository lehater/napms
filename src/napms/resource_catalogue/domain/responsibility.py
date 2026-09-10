from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum

from napms.resource_catalogue.domain.model import ResourceCatalogueInvariantError


class ResponsiblePartyKind(str, Enum):
    PERSON = "Person"
    TEAM = "Team"


class ResourceResponsibilityRole(str, Enum):
    SERVICE_OWNER = "ServiceOwner"
    TECHNICAL_OWNER = "TechnicalOwner"
    OPERATIONS_CONTACT = "OperationsContact"
    BUSINESS_OWNER = "BusinessOwner"


@dataclass(frozen=True, slots=True)
class ResourceResponsibility:
    assignment_reference: str
    resource_reference: str
    party_reference: str
    party_kind: ResponsiblePartyKind
    role: ResourceResponsibilityRole
    display_name: str
    contact: str | None
    valid_from: datetime
    valid_to: datetime | None
    provenance_reference: str
    end_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        for field_name, value in (
            ("assignment_reference", self.assignment_reference),
            ("resource_reference", self.resource_reference),
            ("party_reference", self.party_reference),
            ("display_name", self.display_name),
            ("provenance_reference", self.provenance_reference),
        ):
            if not value or not value.strip():
                raise ResourceCatalogueInvariantError(f"{field_name} must be non-empty")
        if self.contact is not None and not self.contact.strip():
            raise ResourceCatalogueInvariantError(
                "contact must be non-empty when provided"
            )
        if self.end_provenance_reference is not None:
            if not self.end_provenance_reference.strip():
                raise ResourceCatalogueInvariantError(
                    "end_provenance_reference must be non-empty when provided"
                )
            if self.valid_to is None:
                raise ResourceCatalogueInvariantError(
                    "end provenance requires valid_to"
                )
        if self.valid_from.tzinfo is None or self.valid_from.utcoffset() is None:
            raise ResourceCatalogueInvariantError("valid_from must be offset-aware")
        if self.valid_to is not None:
            if self.valid_to.tzinfo is None or self.valid_to.utcoffset() is None:
                raise ResourceCatalogueInvariantError("valid_to must be offset-aware")
            if self.valid_from >= self.valid_to:
                raise ResourceCatalogueInvariantError("valid_from must be before valid_to")
        if self.version < 1:
            raise ResourceCatalogueInvariantError("version must be >= 1")

    def is_effective_at(self, as_of: datetime) -> bool:
        if as_of.tzinfo is None or as_of.utcoffset() is None:
            raise ResourceCatalogueInvariantError("as_of must be offset-aware")
        return self.valid_from <= as_of and (
            self.valid_to is None or as_of < self.valid_to
        )

    def ended(
        self,
        *,
        valid_to: datetime,
        end_provenance_reference: str,
    ) -> "ResourceResponsibility":
        if self.valid_to is not None:
            raise ResourceCatalogueInvariantError("responsibility is already ended")
        if valid_to.tzinfo is None or valid_to.utcoffset() is None:
            raise ResourceCatalogueInvariantError("valid_to must be offset-aware")
        if valid_to <= self.valid_from:
            raise ResourceCatalogueInvariantError("valid_to must be after valid_from")
        if not end_provenance_reference or not end_provenance_reference.strip():
            raise ResourceCatalogueInvariantError(
                "end_provenance_reference must be non-empty"
            )
        return replace(
            self,
            valid_to=valid_to,
            end_provenance_reference=end_provenance_reference.strip(),
            version=self.version + 1,
        )
