from dataclasses import dataclass
from enum import Enum
from uuid import UUID


@dataclass(frozen=True, slots=True)
class OperationTarget:
    logical_firewall_id: UUID
    enforcement_attachment_id: UUID


class ApplyStatus(str, Enum):
    APPLIED = "Applied"
    PRECONDITION_FAILED = "PreconditionFailed"
    REJECTED = "Rejected"
    UNKNOWN = "Unknown"


class OperationOutcome(str, Enum):
    VERIFIED = "Verified"
    REJECTED = "Rejected"
    PRECONDITION_FAILED = "PreconditionFailed"
    DRIFT = "Drift"
    UNKNOWN = "Unknown"


@dataclass(frozen=True, slots=True)
class TargetState:
    revision: str
    artifact_digest: str | None
    provenance_reference: str


@dataclass(frozen=True, slots=True)
class ApplyResult:
    status: ApplyStatus
    operation_reference: str
    reason: str | None = None

    def __post_init__(self) -> None:
        if self.status is ApplyStatus.APPLIED and self.reason is not None:
            raise ValueError("Applied result cannot carry failure reason")
        if self.status is not ApplyStatus.APPLIED and (
            not self.reason or not self.reason.strip()
        ):
            raise ValueError("failed/unknown apply result requires reason")


@dataclass(frozen=True, slots=True)
class ExecuteNetworkOperationCommand:
    operation_id: str
    target: OperationTarget
    renderer_name: str
    renderer_contract_version: str
    artifact_content: str
    artifact_digest: str
    actor_id: str
    authority_scope: str
    expected_pre_revision: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("operation_id", self.operation_id),
            ("renderer_name", self.renderer_name),
            ("renderer_contract_version", self.renderer_contract_version),
            ("artifact_digest", self.artifact_digest),
            ("actor_id", self.actor_id),
            ("authority_scope", self.authority_scope),
        ):
            if not value or not value.strip():
                raise ValueError(f"{name} must be non-empty")
        if not self.artifact_content:
            raise ValueError("artifact_content must be non-empty")


@dataclass(frozen=True, slots=True)
class NetworkOperationResult:
    operation_id: str
    target: OperationTarget
    artifact_digest: str
    outcome: OperationOutcome
    pre_state: TargetState | None
    apply_result: ApplyResult | None
    post_state: TargetState | None
    reason: str | None
    provenance_references: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.outcome is OperationOutcome.VERIFIED:
            if self.pre_state is None or self.apply_result is None or self.post_state is None:
                raise ValueError("Verified requires pre/apply/post evidence")
            if self.apply_result.status is not ApplyStatus.APPLIED:
                raise ValueError("Verified requires Applied mutation")
            if self.post_state.artifact_digest != self.artifact_digest:
                raise ValueError("Verified post-state must match artifact digest")
            if self.reason is not None:
                raise ValueError("Verified cannot carry failure reason")
        elif not self.reason or not self.reason.strip():
            raise ValueError("non-Verified result requires reason")
