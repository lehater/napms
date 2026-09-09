from dataclasses import dataclass
from datetime import datetime


class ResourceCatalogueInvariantError(Exception):
    """Raised when Resource Catalogue state is structurally invalid."""


def _require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ResourceCatalogueInvariantError(f"{field_name} must be offset-aware")


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

    def is_effective_at(self, as_of: datetime) -> bool:
        _require_aware(as_of, field_name="as_of")
        return self.valid_from <= as_of and (
            self.valid_to is None or as_of < self.valid_to
        )


@dataclass(frozen=True, slots=True)
class ResourceScopeAffiliation:
    affiliation_reference: str
    resource_reference: str
    responsibility_scope: str
    valid_from: datetime
    valid_to: datetime | None
    provenance_reference: str

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

        _require_aware(self.valid_from, field_name="valid_from")
        if self.valid_to is not None:
            _require_aware(self.valid_to, field_name="valid_to")
            if self.valid_from >= self.valid_to:
                raise ResourceCatalogueInvariantError(
                    "valid_from must be before valid_to"
                )

    def is_effective_at(self, as_of: datetime) -> bool:
        _require_aware(as_of, field_name="as_of")
        return self.valid_from <= as_of and (
            self.valid_to is None or as_of < self.valid_to
        )
