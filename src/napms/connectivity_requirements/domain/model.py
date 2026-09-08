from dataclasses import dataclass, replace
from datetime import datetime
from enum import Enum
from uuid import UUID


class RequirementInvariantError(Exception):
    """Raised when Connectivity Requirements state is structurally invalid."""


def _require_non_empty(value: str, *, field_name: str) -> None:
    if not value or not value.strip():
        raise RequirementInvariantError(f"{field_name} must be non-empty")


def _require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise RequirementInvariantError(f"{field_name} must be offset-aware")


@dataclass(frozen=True, slots=True)
class RequiredSemanticInteraction:
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    dcs_contract_revision_id: UUID

    def contains_deployment(self, deployment_id: UUID) -> bool:
        return deployment_id in (
            self.source_component_deployment_id,
            self.destination_component_deployment_id,
        )


class RequirementApplicabilityKind(str, Enum):
    ONGOING = "Ongoing"
    ABSOLUTE_WINDOW = "AbsoluteWindow"


@dataclass(frozen=True, slots=True)
class RequirementApplicability:
    kind: RequirementApplicabilityKind
    start: datetime | None = None
    end: datetime | None = None

    def __post_init__(self) -> None:
        if self.kind is RequirementApplicabilityKind.ONGOING:
            if self.start is not None or self.end is not None:
                raise RequirementInvariantError(
                    "Ongoing applicability cannot have start/end"
                )
            return

        if self.start is None or self.end is None:
            raise RequirementInvariantError(
                "AbsoluteWindow applicability requires start and end"
            )
        _require_aware(self.start, field_name="RequirementApplicability.start")
        _require_aware(self.end, field_name="RequirementApplicability.end")
        if self.start >= self.end:
            raise RequirementInvariantError(
                "RequirementApplicability requires start < end"
            )

    @classmethod
    def ongoing(cls) -> "RequirementApplicability":
        return cls(RequirementApplicabilityKind.ONGOING)

    @classmethod
    def absolute_window(
        cls,
        *,
        start: datetime,
        end: datetime,
    ) -> "RequirementApplicability":
        return cls(
            RequirementApplicabilityKind.ABSOLUTE_WINDOW,
            start=start,
            end=end,
        )

    def applies_at(self, as_of: datetime) -> bool:
        _require_aware(as_of, field_name="as_of")
        if self.kind is RequirementApplicabilityKind.ONGOING:
            return True
        assert self.start is not None
        assert self.end is not None
        return self.start <= as_of < self.end


class RequirementLifecycleState(str, Enum):
    ACTIVE = "Active"
    RETIRED = "Retired"


@dataclass(frozen=True, slots=True)
class RequirementSemanticKey:
    governance_scope: str
    dependent_component_deployment_id: UUID
    required_interaction: RequiredSemanticInteraction

    def __post_init__(self) -> None:
        _require_non_empty(self.governance_scope, field_name="governance_scope")
        if not self.required_interaction.contains_deployment(
            self.dependent_component_deployment_id
        ):
            raise RequirementInvariantError(
                "dependent Component Deployment must participate in required interaction"
            )


@dataclass(frozen=True, slots=True)
class RequirementDeclarationProvenance:
    actor_id: str
    effective_time: datetime
    governance_scope: str
    authority_reference: str
    catalogue_reference: str | None = None

    def __post_init__(self) -> None:
        _require_non_empty(self.actor_id, field_name="actor_id")
        _require_aware(self.effective_time, field_name="effective_time")
        _require_non_empty(self.governance_scope, field_name="governance_scope")
        _require_non_empty(
            self.authority_reference,
            field_name="authority_reference",
        )
        if self.catalogue_reference is not None:
            _require_non_empty(
                self.catalogue_reference,
                field_name="catalogue_reference",
            )


@dataclass(frozen=True, slots=True)
class RequirementApplicabilityChange:
    requirement_id: UUID
    previous_applicability: RequirementApplicability
    new_applicability: RequirementApplicability
    actor_id: str
    effective_time: datetime
    governance_scope: str
    authority_reference: str


@dataclass(frozen=True, slots=True)
class RequirementJustificationChange:
    requirement_id: UUID
    previous_justification: str
    new_justification: str
    actor_id: str
    effective_time: datetime
    governance_scope: str
    authority_reference: str


@dataclass(frozen=True, slots=True)
class RequirementLifecycleTransition:
    requirement_id: UUID
    from_state: RequirementLifecycleState
    to_state: RequirementLifecycleState
    actor_id: str
    effective_time: datetime
    governance_scope: str
    authority_reference: str


@dataclass(frozen=True, slots=True)
class ConnectivityRequirement:
    requirement_id: UUID
    governance_scope: str
    dependent_component_deployment_id: UUID
    required_interaction: RequiredSemanticInteraction
    applicability: RequirementApplicability
    justification: str
    lifecycle_state: RequirementLifecycleState
    declaration_provenance: RequirementDeclarationProvenance
    applicability_history: tuple[RequirementApplicabilityChange, ...] = ()
    justification_history: tuple[RequirementJustificationChange, ...] = ()
    lifecycle_history: tuple[RequirementLifecycleTransition, ...] = ()
    version: int = 1

    def __post_init__(self) -> None:
        _require_non_empty(self.governance_scope, field_name="governance_scope")
        _require_non_empty(self.justification, field_name="justification")
        if self.version < 1:
            raise RequirementInvariantError("version must be >= 1")
        if self.declaration_provenance.governance_scope != self.governance_scope:
            raise RequirementInvariantError(
                "declaration provenance scope must match Requirement governance scope"
            )
        if not self.required_interaction.contains_deployment(
            self.dependent_component_deployment_id
        ):
            raise RequirementInvariantError(
                "dependent Component Deployment must participate in required interaction"
            )

    @property
    def semantic_key(self) -> RequirementSemanticKey:
        return RequirementSemanticKey(
            governance_scope=self.governance_scope,
            dependent_component_deployment_id=self.dependent_component_deployment_id,
            required_interaction=self.required_interaction,
        )

    @classmethod
    def declared(
        cls,
        *,
        requirement_id: UUID,
        semantic_key: RequirementSemanticKey,
        applicability: RequirementApplicability,
        justification: str,
        provenance: RequirementDeclarationProvenance,
    ) -> "ConnectivityRequirement":
        _require_non_empty(justification, field_name="justification")
        if provenance.governance_scope != semantic_key.governance_scope:
            raise RequirementInvariantError(
                "declaration provenance scope must match semantic key scope"
            )
        return cls(
            requirement_id=requirement_id,
            governance_scope=semantic_key.governance_scope,
            dependent_component_deployment_id=(
                semantic_key.dependent_component_deployment_id
            ),
            required_interaction=semantic_key.required_interaction,
            applicability=applicability,
            justification=justification.strip(),
            lifecycle_state=RequirementLifecycleState.ACTIVE,
            declaration_provenance=provenance,
        )

    def _require_active(self) -> None:
        if self.lifecycle_state is RequirementLifecycleState.RETIRED:
            raise RequirementInvariantError(
                "Retired Connectivity Requirement is immutable"
            )

    def with_applicability(
        self,
        *,
        applicability: RequirementApplicability,
        actor_id: str,
        effective_time: datetime,
        authority_reference: str,
    ) -> "ConnectivityRequirement":
        self._require_active()
        if applicability == self.applicability:
            raise RequirementInvariantError(
                "applicability change requires a different value"
            )
        change = RequirementApplicabilityChange(
            requirement_id=self.requirement_id,
            previous_applicability=self.applicability,
            new_applicability=applicability,
            actor_id=actor_id,
            effective_time=effective_time,
            governance_scope=self.governance_scope,
            authority_reference=authority_reference,
        )
        return replace(
            self,
            applicability=applicability,
            applicability_history=self.applicability_history + (change,),
            version=self.version + 1,
        )

    def with_justification(
        self,
        *,
        justification: str,
        actor_id: str,
        effective_time: datetime,
        authority_reference: str,
    ) -> "ConnectivityRequirement":
        self._require_active()
        _require_non_empty(justification, field_name="justification")
        normalized = justification.strip()
        if normalized == self.justification:
            raise RequirementInvariantError(
                "justification change requires a different value"
            )
        change = RequirementJustificationChange(
            requirement_id=self.requirement_id,
            previous_justification=self.justification,
            new_justification=normalized,
            actor_id=actor_id,
            effective_time=effective_time,
            governance_scope=self.governance_scope,
            authority_reference=authority_reference,
        )
        return replace(
            self,
            justification=normalized,
            justification_history=self.justification_history + (change,),
            version=self.version + 1,
        )

    def retired(
        self,
        *,
        actor_id: str,
        effective_time: datetime,
        authority_reference: str,
    ) -> "ConnectivityRequirement":
        self._require_active()
        transition = RequirementLifecycleTransition(
            requirement_id=self.requirement_id,
            from_state=self.lifecycle_state,
            to_state=RequirementLifecycleState.RETIRED,
            actor_id=actor_id,
            effective_time=effective_time,
            governance_scope=self.governance_scope,
            authority_reference=authority_reference,
        )
        return replace(
            self,
            lifecycle_state=RequirementLifecycleState.RETIRED,
            lifecycle_history=self.lifecycle_history + (transition,),
            version=self.version + 1,
        )
