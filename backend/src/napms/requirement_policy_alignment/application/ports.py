from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Protocol
from uuid import UUID

from napms.requirement_policy_alignment.application.model import (
    AlignmentSemanticIdentity,
    RequirementAlignmentSnapshot,
)


class RequirementAlignmentReadOutcome(str, Enum):
    FOUND = "Found"
    NOT_FOUND = "NotFound"
    AUTHORITY_DENIED = "AuthorityDenied"
    AUTHORITY_UNKNOWN = "AuthorityUnknown"
    UNAVAILABLE = "Unavailable"


@dataclass(frozen=True, slots=True)
class RequirementAlignmentReadResult:
    outcome: RequirementAlignmentReadOutcome
    snapshot: RequirementAlignmentSnapshot | None = None
    read_authority_reference: str | None = None


class PolicyCoverageOutcome(str, Enum):
    COVERED = "Covered"
    UNCOVERED = "Uncovered"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class RequirementAlignmentSnapshotPage:
    snapshots: tuple[RequirementAlignmentSnapshot, ...]
    page: int
    page_size: int
    has_more: bool
    ambiguous_scopes: tuple[str, ...] = ()


class RequirementAlignmentListOutcome(str, Enum):
    AVAILABLE = "Available"
    UNAVAILABLE = "Unavailable"


@dataclass(frozen=True, slots=True)
class RequirementAlignmentListResult:
    outcome: RequirementAlignmentListOutcome
    page: RequirementAlignmentSnapshotPage | None = None


class AuthorizedRequirementAlignmentPort(Protocol):
    def get_for_alignment(
        self,
        *,
        requirement_id: UUID,
        actor_id: str,
        as_of: datetime,
    ) -> RequirementAlignmentReadResult: ...


class EffectivePolicyCoveragePort(Protocol):
    def check_exact_coverage(
        self,
        *,
        semantic_identity: AlignmentSemanticIdentity,
        as_of: datetime,
    ) -> PolicyCoverageOutcome: ...



class AuthorizedRequirementAlignmentListPort(Protocol):
    def list_for_alignment(
        self,
        *,
        actor_id: str,
        as_of: datetime,
        page: int,
        page_size: int,
    ) -> RequirementAlignmentListResult: ...
