from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class DecisionInvariantError(Exception):
    """Raised when Connectivity Decision state is structurally invalid."""


def _require_non_empty(value: str, *, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise DecisionInvariantError(f"{field_name} must be non-empty")
    return normalized


def _require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise DecisionInvariantError(f"{field_name} must be offset-aware")


@dataclass(frozen=True, slots=True)
class DecisionSubject:
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    dcs_contract_revision_id: UUID


class DecisionOutcome(str, Enum):
    ALLOWED = "Allowed"
    NOT_ALLOWED = "NotAllowed"


@dataclass(frozen=True, slots=True)
class DecisionValidity:
    valid_from: datetime
    valid_until: datetime | None = None

    def __post_init__(self) -> None:
        _require_aware(self.valid_from, field_name="valid_from")
        if self.valid_until is not None:
            _require_aware(self.valid_until, field_name="valid_until")
            if self.valid_from >= self.valid_until:
                raise DecisionInvariantError("valid_from must be before valid_until")

    def contains(self, as_of: datetime) -> bool:
        _require_aware(as_of, field_name="as_of")
        return self.valid_from <= as_of and (
            self.valid_until is None or as_of < self.valid_until
        )


@dataclass(frozen=True, slots=True)
class DecisionEvidenceReference:
    kind: str
    reference: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "kind", _require_non_empty(self.kind, field_name="kind"))
        object.__setattr__(
            self,
            "reference",
            _require_non_empty(self.reference, field_name="reference"),
        )


@dataclass(frozen=True, slots=True)
class DecisionProvenance:
    actor_id: str
    decided_at: datetime
    authority_reference: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "actor_id",
            _require_non_empty(self.actor_id, field_name="actor_id"),
        )
        _require_aware(self.decided_at, field_name="decided_at")
        object.__setattr__(
            self,
            "authority_reference",
            _require_non_empty(
                self.authority_reference,
                field_name="authority_reference",
            ),
        )


@dataclass(frozen=True, slots=True)
class ConnectivityDecision:
    decision_id: UUID
    subject: DecisionSubject
    governance_scope: str
    outcome: DecisionOutcome
    validity: DecisionValidity
    reason_code: str
    reason_text: str
    evidence_references: tuple[DecisionEvidenceReference, ...]
    provenance: DecisionProvenance
    supersedes_decision_id: UUID | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "governance_scope",
            _require_non_empty(
                self.governance_scope,
                field_name="governance_scope",
            ),
        )
        object.__setattr__(
            self,
            "reason_code",
            _require_non_empty(self.reason_code, field_name="reason_code"),
        )
        object.__setattr__(
            self,
            "reason_text",
            _require_non_empty(self.reason_text, field_name="reason_text"),
        )
        if self.supersedes_decision_id == self.decision_id:
            raise DecisionInvariantError("decision cannot supersede itself")

    def is_effective_at(self, as_of: datetime) -> bool:
        return self.validity.contains(as_of)

    def has_same_intent(
        self,
        *,
        subject: DecisionSubject,
        governance_scope: str,
        outcome: DecisionOutcome,
        validity: DecisionValidity,
        reason_code: str,
        reason_text: str,
        evidence_references: tuple[DecisionEvidenceReference, ...],
    ) -> bool:
        return (
            self.subject == subject
            and self.governance_scope == governance_scope.strip()
            and self.outcome is outcome
            and self.validity == validity
            and self.reason_code == reason_code.strip()
            and self.reason_text == reason_text.strip()
            and self.evidence_references == evidence_references
        )
