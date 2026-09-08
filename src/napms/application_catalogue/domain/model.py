from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


class CatalogueInvariantError(Exception):
    """Raised when Application Communication Catalogue state is invalid."""


def _require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise CatalogueInvariantError(f"{field_name} must be offset-aware")


@dataclass(frozen=True, slots=True)
class DirectedInteractionIdentity:
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    dcs_contract_revision_id: UUID


@dataclass(frozen=True, slots=True)
class ComponentDeployment:
    deployment_id: UUID
    provenance_reference: str

    def __post_init__(self) -> None:
        if not self.provenance_reference:
            raise CatalogueInvariantError("provenance_reference must be non-empty")


@dataclass(frozen=True, slots=True)
class DcsRevision:
    revision_id: UUID
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    projection_payload: bytes
    provenance_reference: str

    def __post_init__(self) -> None:
        if not self.projection_payload:
            raise CatalogueInvariantError("projection_payload must be non-empty")
        if not self.provenance_reference:
            raise CatalogueInvariantError("provenance_reference must be non-empty")


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
