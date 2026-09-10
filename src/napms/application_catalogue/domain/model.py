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


def _optional_non_empty(value: str | None, *, field_name: str) -> str | None:
    if value is None:
        return None
    return _require_non_empty(value, field_name=field_name)


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


def _validate_retirement_provenance(
    *,
    lifecycle_state: CatalogueLifecycleState,
    retirement_provenance_reference: str | None,
    entity_name: str,
) -> None:
    if lifecycle_state is CatalogueLifecycleState.ACTIVE:
        if retirement_provenance_reference is not None:
            raise CatalogueInvariantError(
                f"Active {entity_name} cannot have retirement provenance"
            )
        return
    if retirement_provenance_reference is None:
        raise CatalogueInvariantError(
            f"Retired {entity_name} requires retirement provenance"
        )
    _require_non_empty(
        retirement_provenance_reference,
        field_name="retirement_provenance_reference",
    )


@dataclass(frozen=True, slots=True)
class Application:
    application_id: UUID
    display_name: str
    provenance_reference: str
    description: str | None = None
    domain: str | None = None
    owner_reference: str | None = None
    lifecycle_state: CatalogueLifecycleState = CatalogueLifecycleState.ACTIVE
    retirement_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "display_name",
            _require_non_empty(self.display_name, field_name="display_name"),
        )
        for field_name in ("description", "domain", "owner_reference"):
            object.__setattr__(
                self,
                field_name,
                _optional_non_empty(getattr(self, field_name), field_name=field_name),
            )
        _require_non_empty(self.provenance_reference, field_name="provenance_reference")
        _validate_retirement_provenance(
            lifecycle_state=self.lifecycle_state,
            retirement_provenance_reference=self.retirement_provenance_reference,
            entity_name="Application",
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

    def changed_metadata(
        self,
        *,
        display_name: str,
        description: str | None,
        domain: str | None,
        owner_reference: str | None,
    ) -> "Application":
        self._require_active()
        normalized = (
            _require_non_empty(display_name, field_name="display_name"),
            _optional_non_empty(description, field_name="description"),
            _optional_non_empty(domain, field_name="domain"),
            _optional_non_empty(owner_reference, field_name="owner_reference"),
        )
        current = (
            self.display_name,
            self.description,
            self.domain,
            self.owner_reference,
        )
        if normalized == current:
            raise CatalogueInvariantError("metadata edit requires a semantic change")
        return replace(
            self,
            display_name=normalized[0],
            description=normalized[1],
            domain=normalized[2],
            owner_reference=normalized[3],
            version=self.version + 1,
        )

    def retired(self, *, retirement_provenance_reference: str) -> "Application":
        self._require_active()
        normalized = _require_non_empty(
            retirement_provenance_reference,
            field_name="retirement_provenance_reference",
        )
        return replace(
            self,
            lifecycle_state=CatalogueLifecycleState.RETIRED,
            retirement_provenance_reference=normalized,
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class Component:
    component_id: UUID
    application_id: UUID
    display_name: str
    provenance_reference: str
    component_type: str | None = None
    description: str | None = None
    lifecycle_state: CatalogueLifecycleState = CatalogueLifecycleState.ACTIVE
    retirement_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "display_name",
            _require_non_empty(self.display_name, field_name="display_name"),
        )
        object.__setattr__(
            self,
            "component_type",
            _optional_non_empty(self.component_type, field_name="component_type"),
        )
        object.__setattr__(
            self,
            "description",
            _optional_non_empty(self.description, field_name="description"),
        )
        _require_non_empty(self.provenance_reference, field_name="provenance_reference")
        _validate_retirement_provenance(
            lifecycle_state=self.lifecycle_state,
            retirement_provenance_reference=self.retirement_provenance_reference,
            entity_name="Component",
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

    def changed_metadata(
        self,
        *,
        display_name: str,
        component_type: str | None,
        description: str | None,
    ) -> "Component":
        self._require_active()
        normalized = (
            _require_non_empty(display_name, field_name="display_name"),
            _optional_non_empty(component_type, field_name="component_type"),
            _optional_non_empty(description, field_name="description"),
        )
        current = (self.display_name, self.component_type, self.description)
        if normalized == current:
            raise CatalogueInvariantError("metadata edit requires a semantic change")
        return replace(
            self,
            display_name=normalized[0],
            component_type=normalized[1],
            description=normalized[2],
            version=self.version + 1,
        )

    def retired(self, *, retirement_provenance_reference: str) -> "Component":
        self._require_active()
        normalized = _require_non_empty(
            retirement_provenance_reference,
            field_name="retirement_provenance_reference",
        )
        return replace(
            self,
            lifecycle_state=CatalogueLifecycleState.RETIRED,
            retirement_provenance_reference=normalized,
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class ComponentDeployment:
    deployment_id: UUID
    component_id: UUID
    provenance_reference: str
    display_name: str | None = None
    lifecycle_state: CatalogueLifecycleState = CatalogueLifecycleState.ACTIVE
    retirement_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        _require_non_empty(self.provenance_reference, field_name="provenance_reference")
        _validate_display_name(self.display_name, field_name="display_name")
        _validate_retirement_provenance(
            lifecycle_state=self.lifecycle_state,
            retirement_provenance_reference=self.retirement_provenance_reference,
            entity_name="Component Deployment",
        )
        if self.version < 1:
            raise CatalogueInvariantError("version must be >= 1")

    def _require_active(self) -> None:
        if self.lifecycle_state is CatalogueLifecycleState.RETIRED:
            raise CatalogueInvariantError("Retired Component Deployment is immutable")

    def renamed(self, display_name: str | None) -> "ComponentDeployment":
        self._require_active()
        if display_name is not None:
            normalized = _require_non_empty(display_name, field_name="display_name")
        else:
            normalized = None
        if normalized == self.display_name:
            raise CatalogueInvariantError("rename requires a different display name")
        return replace(self, display_name=normalized, version=self.version + 1)

    def retired(
        self,
        *,
        retirement_provenance_reference: str,
    ) -> "ComponentDeployment":
        self._require_active()
        normalized = _require_non_empty(
            retirement_provenance_reference,
            field_name="retirement_provenance_reference",
        )
        return replace(
            self,
            lifecycle_state=CatalogueLifecycleState.RETIRED,
            retirement_provenance_reference=normalized,
            version=self.version + 1,
        )


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
    end_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        for field_name, value in (
            ("reference_id", self.reference_id),
            ("resource_reference", self.resource_reference),
            ("provenance_reference", self.provenance_reference),
        ):
            _require_non_empty(value, field_name=field_name)

        if self.end_provenance_reference is not None:
            _require_non_empty(
                self.end_provenance_reference,
                field_name="end_provenance_reference",
            )
            if self.valid_to is None:
                raise CatalogueInvariantError("end provenance requires valid_to")

        _require_aware(self.valid_from, field_name="valid_from")
        if self.valid_to is not None:
            _require_aware(self.valid_to, field_name="valid_to")
            if self.valid_from >= self.valid_to:
                raise CatalogueInvariantError("valid_from must be before valid_to")
        if self.version < 1:
            raise CatalogueInvariantError("version must be >= 1")

    def is_effective_at(self, as_of: datetime) -> bool:
        _require_aware(as_of, field_name="as_of")
        return self.valid_from <= as_of and (
            self.valid_to is None or as_of < self.valid_to
        )

    def ended(
        self,
        *,
        valid_to: datetime,
        end_provenance_reference: str,
    ) -> "DeploymentResourceBinding":
        if self.valid_to is not None:
            raise CatalogueInvariantError("deployment resource binding is already ended")
        _require_aware(valid_to, field_name="valid_to")
        if valid_to <= self.valid_from:
            raise CatalogueInvariantError("valid_to must be after valid_from")
        normalized_provenance = _require_non_empty(
            end_provenance_reference,
            field_name="end_provenance_reference",
        )
        return replace(
            self,
            valid_to=valid_to,
            end_provenance_reference=normalized_provenance,
            version=self.version + 1,
        )
