from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from uuid import UUID

from napms.application_catalogue.domain.communication import (
    AuthoredDcsTrafficAlternative,
    canonical_dcs_alternatives,
)
from napms.application_catalogue.domain.model import (
    CatalogueInvariantError,
    CatalogueLifecycleState,
)


def _required(value: str, *, field_name: str) -> str:
    normalized = value.strip() if value else ""
    if not normalized:
        raise CatalogueInvariantError(f"{field_name} must be non-empty")
    return normalized


def _require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise CatalogueInvariantError(f"{field_name} must be offset-aware")


def _validate_retirement(
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
    _required(
        retirement_provenance_reference,
        field_name="retirement_provenance_reference",
    )


class DeploymentInteractionSide(str, Enum):
    SOURCE = "Source"
    DESTINATION = "Destination"


@dataclass(frozen=True, slots=True)
class InteractionDefinition:
    interaction_definition_id: UUID
    application_id: UUID
    source_component_id: UUID
    destination_component_id: UUID
    traffic_alternatives: tuple[AuthoredDcsTrafficAlternative, ...]
    provenance_reference: str
    lifecycle_state: CatalogueLifecycleState = CatalogueLifecycleState.ACTIVE
    retirement_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "traffic_alternatives",
            canonical_dcs_alternatives(self.traffic_alternatives),
        )
        _required(self.provenance_reference, field_name="provenance_reference")
        _validate_retirement(
            lifecycle_state=self.lifecycle_state,
            retirement_provenance_reference=self.retirement_provenance_reference,
            entity_name="Interaction Definition",
        )
        if self.version < 1:
            raise CatalogueInvariantError("version must be >= 1")

    def _require_active(self) -> None:
        if self.lifecycle_state is CatalogueLifecycleState.RETIRED:
            raise CatalogueInvariantError("Retired Interaction Definition is immutable")

    def changed_endpoints(
        self,
        *,
        source_component_id: UUID,
        destination_component_id: UUID,
    ) -> "InteractionDefinition":
        self._require_active()
        if (
            source_component_id == self.source_component_id
            and destination_component_id == self.destination_component_id
        ):
            raise CatalogueInvariantError("endpoint edit requires a semantic change")
        return replace(
            self,
            source_component_id=source_component_id,
            destination_component_id=destination_component_id,
            version=self.version + 1,
        )

    def changed_traffic(
        self,
        traffic_alternatives: tuple[AuthoredDcsTrafficAlternative, ...],
    ) -> "InteractionDefinition":
        self._require_active()
        canonical = canonical_dcs_alternatives(traffic_alternatives)
        if canonical == self.traffic_alternatives:
            raise CatalogueInvariantError("traffic edit requires a semantic change")
        return replace(
            self,
            traffic_alternatives=canonical,
            version=self.version + 1,
        )

    def retired(self, *, retirement_provenance_reference: str) -> "InteractionDefinition":
        self._require_active()
        return replace(
            self,
            lifecycle_state=CatalogueLifecycleState.RETIRED,
            retirement_provenance_reference=_required(
                retirement_provenance_reference,
                field_name="retirement_provenance_reference",
            ),
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class ApplicationDeployment:
    application_deployment_id: UUID
    application_id: UUID
    company_reference: str
    environment: str
    scope_reference: str
    provenance_reference: str
    lifecycle_state: CatalogueLifecycleState = CatalogueLifecycleState.ACTIVE
    retirement_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        for field_name in (
            "company_reference",
            "environment",
            "scope_reference",
            "provenance_reference",
        ):
            object.__setattr__(
                self,
                field_name,
                _required(getattr(self, field_name), field_name=field_name),
            )
        _validate_retirement(
            lifecycle_state=self.lifecycle_state,
            retirement_provenance_reference=self.retirement_provenance_reference,
            entity_name="Application Deployment",
        )
        if self.version < 1:
            raise CatalogueInvariantError("version must be >= 1")

    def _require_active(self) -> None:
        if self.lifecycle_state is CatalogueLifecycleState.RETIRED:
            raise CatalogueInvariantError("Retired Application Deployment is immutable")

    def changed_context(
        self,
        *,
        company_reference: str,
        environment: str,
        scope_reference: str,
    ) -> "ApplicationDeployment":
        self._require_active()
        company = _required(company_reference, field_name="company_reference")
        environment_value = _required(environment, field_name="environment")
        scope = _required(scope_reference, field_name="scope_reference")
        if (
            company == self.company_reference
            and environment_value == self.environment
            and scope == self.scope_reference
        ):
            raise CatalogueInvariantError("context edit requires a semantic change")
        return replace(
            self,
            company_reference=company,
            environment=environment_value,
            scope_reference=scope,
            version=self.version + 1,
        )

    def retired(self, *, retirement_provenance_reference: str) -> "ApplicationDeployment":
        self._require_active()
        return replace(
            self,
            lifecycle_state=CatalogueLifecycleState.RETIRED,
            retirement_provenance_reference=_required(
                retirement_provenance_reference,
                field_name="retirement_provenance_reference",
            ),
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class DeploymentInteraction:
    deployment_interaction_id: UUID
    application_deployment_id: UUID
    interaction_definition_id: UUID
    provenance_reference: str
    lifecycle_state: CatalogueLifecycleState = CatalogueLifecycleState.ACTIVE
    retirement_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        _required(self.provenance_reference, field_name="provenance_reference")
        _validate_retirement(
            lifecycle_state=self.lifecycle_state,
            retirement_provenance_reference=self.retirement_provenance_reference,
            entity_name="Deployment Interaction",
        )
        if self.version < 1:
            raise CatalogueInvariantError("version must be >= 1")

    def retired(self, *, retirement_provenance_reference: str) -> "DeploymentInteraction":
        if self.lifecycle_state is CatalogueLifecycleState.RETIRED:
            raise CatalogueInvariantError("Retired Deployment Interaction is immutable")
        return replace(
            self,
            lifecycle_state=CatalogueLifecycleState.RETIRED,
            retirement_provenance_reference=_required(
                retirement_provenance_reference,
                field_name="retirement_provenance_reference",
            ),
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class DeploymentInteractionCompatibility:
    deployment_interaction_id: UUID
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    current_dcs_revision_id: UUID
    version: int = 1

    def __post_init__(self) -> None:
        if self.version < 1:
            raise CatalogueInvariantError("version must be >= 1")

    def advanced_to(self, dcs_revision_id: UUID) -> "DeploymentInteractionCompatibility":
        if dcs_revision_id == self.current_dcs_revision_id:
            raise CatalogueInvariantError("compatibility revision must change")
        return replace(
            self,
            current_dcs_revision_id=dcs_revision_id,
            version=self.version + 1,
        )


@dataclass(frozen=True, slots=True)
class DeploymentInteractionResourceBinding:
    reference_id: str
    deployment_interaction_id: UUID
    side: DeploymentInteractionSide
    resource_reference: str
    valid_from: datetime
    valid_to: datetime | None
    provenance_reference: str
    end_provenance_reference: str | None = None
    version: int = 1

    def __post_init__(self) -> None:
        for field_name in (
            "reference_id",
            "resource_reference",
            "provenance_reference",
        ):
            object.__setattr__(
                self,
                field_name,
                _required(getattr(self, field_name), field_name=field_name),
            )
        _require_aware(self.valid_from, field_name="valid_from")
        if self.valid_to is not None:
            _require_aware(self.valid_to, field_name="valid_to")
            if self.valid_from >= self.valid_to:
                raise CatalogueInvariantError("valid_from must be before valid_to")
        if self.end_provenance_reference is not None:
            _required(
                self.end_provenance_reference,
                field_name="end_provenance_reference",
            )
            if self.valid_to is None:
                raise CatalogueInvariantError("end provenance requires valid_to")
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
    ) -> "DeploymentInteractionResourceBinding":
        if self.valid_to is not None:
            raise CatalogueInvariantError("resource binding is already ended")
        _require_aware(valid_to, field_name="valid_to")
        if valid_to <= self.valid_from:
            raise CatalogueInvariantError("valid_to must be after valid_from")
        return replace(
            self,
            valid_to=valid_to,
            end_provenance_reference=_required(
                end_provenance_reference,
                field_name="end_provenance_reference",
            ),
            version=self.version + 1,
        )
