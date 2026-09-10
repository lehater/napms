from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from uuid import UUID


class CatalogueInvariantError(Exception):
    """Raised when Application Communication Catalogue state is invalid."""


def _require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise CatalogueInvariantError(f"{field_name} must be offset-aware")


def _require_non_empty(value: str, *, field_name: str) -> str:
    if not value or not value.strip():
        raise CatalogueInvariantError(f"{field_name} must be non-empty")
    return value.strip()


@dataclass(frozen=True, slots=True)
class DirectedInteractionIdentity:
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    dcs_contract_revision_id: UUID


def _validate_display_name(value: str | None, *, field_name: str) -> None:
    if value is not None and not value.strip():
        raise CatalogueInvariantError(f"{field_name} must be non-empty when provided")


class CatalogueLifecycleState(str, Enum):
    ACTIVE = "Active"
    RETIRED = "Retired"


@dataclass(frozen=True, slots=True)
class Application:
    application_id: UUID
    display_name: str
    provenance_reference: str
    lifecycle_state: CatalogueLifecycleState = CatalogueLifecycleState.ACTIVE
    version: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "display_name",
            _require_non_empty(self.display_name, field_name="display_name"),
        )
        _require_non_empty(
            self.provenance_reference,
            field_name="provenance_reference",
        )
        if self.version < 1:
            raise CatalogueInvariantError("version must be >= 1")

    def _require_active(self) -> None:
        if self.lifecycle_state is CatalogueLifecycleState.RETIRED:
            raise CatalogueInvariantError("Retired Application is immutable")

    def renamed(self, display_name: str) -> "Application":
        self._require_active()
        normalized = _require_non_empty(display_name, field_name="display_name")
        if normalized == self.display_name:
            raise CatalogueInvariantError("rename requires a different display name")
        return replace(self, display_name=normalized, version=self.version + 1)

    def retired(self) -> "Application":
        self._require_active()
        return replace(
            self,
            lifecycle_state=CatalogueLifecycleState.RETIRED,
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class Component:
    component_id: UUID
    application_id: UUID
    display_name: str
    provenance_reference: str
    lifecycle_state: CatalogueLifecycleState = CatalogueLifecycleState.ACTIVE
    version: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "display_name",
            _require_non_empty(self.display_name, field_name="display_name"),
        )
        _require_non_empty(
            self.provenance_reference,
            field_name="provenance_reference",
        )
        if self.version < 1:
            raise CatalogueInvariantError("version must be >= 1")

    def _require_active(self) -> None:
        if self.lifecycle_state is CatalogueLifecycleState.RETIRED:
            raise CatalogueInvariantError("Retired Component is immutable")

    def renamed(self, display_name: str) -> "Component":
        self._require_active()
        normalized = _require_non_empty(display_name, field_name="display_name")
        if normalized == self.display_name:
            raise CatalogueInvariantError("rename requires a different display name")
        return replace(self, display_name=normalized, version=self.version + 1)

    def retired(self) -> "Component":
        self._require_active()
        return replace(
            self,
            lifecycle_state=CatalogueLifecycleState.RETIRED,
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class ComponentDeployment:
    deployment_id: UUID
    provenance_reference: str
    display_name: str | None = None

    def __post_init__(self) -> None:
        if not self.provenance_reference:
            raise CatalogueInvariantError("provenance_reference must be non-empty")
        _validate_display_name(self.display_name, field_name="display_name")


@dataclass(frozen=True, slots=True)
class DcsRevision:
    revision_id: UUID
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    projection_payload: bytes
    provenance_reference: str
    display_name: str | None = None

    def __post_init__(self) -> None:
        if not self.projection_payload:
            raise CatalogueInvariantError("projection_payload must be non-empty")
        if not self.provenance_reference:
            raise CatalogueInvariantError("provenance_reference must be non-empty")
        _validate_display_name(self.display_name, field_name="display_name")


@dataclass(frozen=True, slots=True)
class DeploymentResourceBinding:
    reference_id: str
    component_deployment_id: UUID
    resource_reference: str
    valid_from: datetime
    valid_to: datetime | None
    provenance_reference: str

    def __post_init__(self) -> None:
        for field_name, value in (
            ("reference_id", self.reference_id),
            ("resource_reference", self.resource_reference),
            ("provenance_reference", self.provenance_reference),
        ):
            if not value:
                raise CatalogueInvariantError(f"{field_name} must be non-empty")

        _require_aware(self.valid_from, field_name="valid_from")
        if self.valid_to is not None:
            _require_aware(self.valid_to, field_name="valid_to")
            if self.valid_from >= self.valid_to:
                raise CatalogueInvariantError("valid_from must be before valid_to")

    def is_effective_at(self, as_of: datetime) -> bool:
        _require_aware(as_of, field_name="as_of")
        return self.valid_from <= as_of and (
            self.valid_to is None or as_of < self.valid_to
        )
