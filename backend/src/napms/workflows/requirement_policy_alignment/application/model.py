from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from uuid import UUID


class AlignmentInvariantError(Exception):
    """Raised when an alignment query/value is structurally invalid."""


def require_aware(value: datetime, *, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise AlignmentInvariantError(f"{field_name} must be offset-aware")


@dataclass(frozen=True, slots=True)
class AlignmentSemanticIdentity:
    source_component_deployment_id: UUID
    destination_component_deployment_id: UUID
    dcs_contract_revision_id: UUID


class AlignmentRequirementLifecycle(str, Enum):
    ACTIVE = "Active"
    RETIRED = "Retired"


class AlignmentApplicabilityKind(str, Enum):
    ONGOING = "Ongoing"
    ABSOLUTE_WINDOW = "AbsoluteWindow"


@dataclass(frozen=True, slots=True)
class AlignmentApplicability:
    kind: AlignmentApplicabilityKind
    start: datetime | None = None
    end: datetime | None = None

    def __post_init__(self) -> None:
        if self.kind is AlignmentApplicabilityKind.ONGOING:
            if self.start is not None or self.end is not None:
                raise AlignmentInvariantError(
                    "Ongoing applicability cannot have start/end"
                )
            return
        if self.start is None or self.end is None:
            raise AlignmentInvariantError(
                "AbsoluteWindow applicability requires start and end"
            )
        require_aware(self.start, field_name="applicability.start")
        require_aware(self.end, field_name="applicability.end")
        if self.start >= self.end:
            raise AlignmentInvariantError(
                "AbsoluteWindow applicability requires start < end"
            )

    def applies_at(self, as_of: datetime) -> bool:
        require_aware(as_of, field_name="as_of")
        if self.kind is AlignmentApplicabilityKind.ONGOING:
            return True
        assert self.start is not None
        assert self.end is not None
        return self.start <= as_of < self.end


@dataclass(frozen=True, slots=True)
class RequirementAlignmentSnapshot:
    requirement_id: UUID
    semantic_identity: AlignmentSemanticIdentity
    lifecycle: AlignmentRequirementLifecycle
    applicability: AlignmentApplicability


class AlignmentStatus(str, Enum):
    COVERED = "Covered"
    UNCOVERED = "Uncovered"
    NOT_CURRENT = "NotCurrent"
    UNKNOWN = "Unknown"
