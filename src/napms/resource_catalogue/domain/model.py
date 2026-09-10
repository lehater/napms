from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum


class ResourceCatalogueInvariantError(Exception):
    """Raised when Resource Catalogue state is structurally invalid."""


def _require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ResourceCatalogueInvariantError(f"{field_name} must be offset-aware")


def _require_non_empty(value: str, *, field_name: str) -> str:
    if not value or not value.strip():
        raise ResourceCatalogueInvariantError(f"{field_name} must be non-empty")
    return value.strip()


class ResourceLifecycleState(str, Enum):
    ACTIVE = "Active"
    RETIRED = "Retired"


@dataclass(frozen=True, slots=True)
class Resource:
    resource_reference: str
    provenance_reference: str
    display_name: str | None = None
    lifecycle_state: ResourceLifecycleState = ResourceLifecycleState.ACTIVE
    retirement_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        _require_non_empty(
            self.resource_reference,
            field_name="resource_reference",
        )
        _require_non_empty(
            self.provenance_reference,
            field_name="provenance_reference",
        )
        if self.display_name is not None:
            object.__setattr__(
                self,
                "display_name",
                _require_non_empty(self.display_name, field_name="display_name"),
            )
        if self.lifecycle_state is ResourceLifecycleState.ACTIVE:
            if self.retirement_provenance_reference is not None:
                raise ResourceCatalogueInvariantError(
                    "Active Resource cannot have retirement provenance"
                )
        else:
            if self.retirement_provenance_reference is None:
                raise ResourceCatalogueInvariantError(
                    "Retired Resource requires retirement provenance"
                )
            _require_non_empty(
                self.retirement_provenance_reference,
                field_name="retirement_provenance_reference",
            )
        if self.version < 1:
            raise ResourceCatalogueInvariantError("version must be >= 1")

    def _require_active(self) -> None:
        if self.lifecycle_state is ResourceLifecycleState.RETIRED:
            raise ResourceCatalogueInvariantError("Retired Resource is immutable")

    def renamed(self, display_name: str) -> "Resource":
        self._require_active()
        normalized = _require_non_empty(display_name, field_name="display_name")
        if normalized == self.display_name:
            raise ResourceCatalogueInvariantError(
                "rename requires a different display name"
            )
        return replace(self, display_name=normalized, version=self.version + 1)

    def retired(
        self,
        *,
        retirement_provenance_reference: str,
    ) -> "Resource":
        self._require_active()
        normalized = _require_non_empty(
            retirement_provenance_reference,
            field_name="retirement_provenance_reference",
        )
        return replace(
            self,
            lifecycle_state=ResourceLifecycleState.RETIRED,
            retirement_provenance_reference=normalized,
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True, order=True)
class EndpointAddress:
    endpoint_reference: str
    technical_address: str

    def __post_init__(self) -> None:
        if not self.endpoint_reference:
            raise ResourceCatalogueInvariantError(
                "endpoint_reference must be non-empty"
            )
        if not self.technical_address:
            raise ResourceCatalogueInvariantError(
                "technical_address must be non-empty"
            )


@dataclass(frozen=True, slots=True)
class ResourceRealizationVersion:
    fact_reference: str
    resource_reference: str
    endpoint_realizations: tuple[EndpointAddress, ...]
    valid_from: datetime
    valid_to: datetime | None
    provenance_reference: str
    end_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        for field_name, value in (
            ("fact_reference", self.fact_reference),
            ("resource_reference", self.resource_reference),
            ("provenance_reference", self.provenance_reference),
        ):
            if not value:
                raise ResourceCatalogueInvariantError(
                    f"{field_name} must be non-empty"
                )

        if self.end_provenance_reference is not None:
            _require_non_empty(
                self.end_provenance_reference,
                field_name="end_provenance_reference",
            )
            if self.valid_to is None:
                raise ResourceCatalogueInvariantError(
                    "end provenance requires valid_to"
                )

        if not self.endpoint_realizations:
            raise ResourceCatalogueInvariantError(
                "resource realization requires at least one endpoint/address"
            )
        if len(set(self.endpoint_realizations)) != len(self.endpoint_realizations):
            raise ResourceCatalogueInvariantError(
                "duplicate endpoint/address realization is not allowed"
            )

        _require_aware(self.valid_from, field_name="valid_from")
        if self.valid_to is not None:
            _require_aware(self.valid_to, field_name="valid_to")
            if self.valid_from >= self.valid_to:
                raise ResourceCatalogueInvariantError(
                    "valid_from must be before valid_to"
                )
        if self.version < 1:
            raise ResourceCatalogueInvariantError("version must be >= 1")

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
    ) -> "ResourceRealizationVersion":
        if self.valid_to is not None:
            raise ResourceCatalogueInvariantError("realization is already ended")
        _require_aware(valid_to, field_name="valid_to")
        if valid_to <= self.valid_from:
            raise ResourceCatalogueInvariantError("valid_to must be after valid_from")
        end_provenance_reference = _require_non_empty(
            end_provenance_reference,
            field_name="end_provenance_reference",
        )
        return replace(
            self,
            valid_to=valid_to,
            end_provenance_reference=end_provenance_reference,
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class ResourceScopeAffiliation:
    affiliation_reference: str
    resource_reference: str
    responsibility_scope: str
    valid_from: datetime
    valid_to: datetime | None
    provenance_reference: str
    end_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        for field_name, value in (
            ("affiliation_reference", self.affiliation_reference),
            ("resource_reference", self.resource_reference),
            ("responsibility_scope", self.responsibility_scope),
            ("provenance_reference", self.provenance_reference),
        ):
            if not value:
                raise ResourceCatalogueInvariantError(
                    f"{field_name} must be non-empty"
                )

        if self.end_provenance_reference is not None:
            _require_non_empty(
                self.end_provenance_reference,
                field_name="end_provenance_reference",
            )
            if self.valid_to is None:
                raise ResourceCatalogueInvariantError(
                    "end provenance requires valid_to"
                )

        _require_aware(self.valid_from, field_name="valid_from")
        if self.valid_to is not None:
            _require_aware(self.valid_to, field_name="valid_to")
            if self.valid_from >= self.valid_to:
                raise ResourceCatalogueInvariantError(
                    "valid_from must be before valid_to"
                )
        if self.version < 1:
            raise ResourceCatalogueInvariantError("version must be >= 1")

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
    ) -> "ResourceScopeAffiliation":
        if self.valid_to is not None:
            raise ResourceCatalogueInvariantError("scope affiliation is already ended")
        _require_aware(valid_to, field_name="valid_to")
        if valid_to <= self.valid_from:
            raise ResourceCatalogueInvariantError("valid_to must be after valid_from")
        end_provenance_reference = _require_non_empty(
            end_provenance_reference,
            field_name="end_provenance_reference",
        )
        return replace(
            self,
            valid_to=valid_to,
            end_provenance_reference=end_provenance_reference,
            version=self.version + 1,
        )
