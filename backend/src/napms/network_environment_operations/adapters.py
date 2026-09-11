from dataclasses import dataclass
from enum import Enum

from napms.network_environment_operations.domain import (
    ApplyResult,
    ApplyStatus,
    NetworkOperationResult,
    OperationTarget,
    TargetState,
)


class StubScenario(str, Enum):
    SUCCESS = "success"
    REJECT = "reject"
    UNKNOWN_APPLY = "unknown-apply"
    CONCURRENT_CHANGE = "concurrent-change"
    POST_APPLY_DRIFT = "post-apply-drift"


class AllowAllMutationAuthority:
    def may_execute(
        self,
        *,
        actor_id: str,
        authority_scope: str,
        target: OperationTarget,
    ) -> bool:
        return bool(actor_id and authority_scope and target)


class DenyAllMutationAuthority:
    def may_execute(
        self,
        *,
        actor_id: str,
        authority_scope: str,
        target: OperationTarget,
    ) -> bool:
        return False


class InMemoryOperationRepository:
    def __init__(self) -> None:
        self._items: dict[str, NetworkOperationResult] = {}

    def get(self, operation_id: str) -> NetworkOperationResult | None:
        return self._items.get(operation_id)

    def save(self, result: NetworkOperationResult) -> None:
        self._items[result.operation_id] = result


@dataclass(slots=True)
class DeterministicTargetStub:
    target: OperationTarget
    scenario: StubScenario = StubScenario.SUCCESS
    revision: int = 1
    artifact_digest: str | None = None
    apply_calls: int = 0
    acquire_calls: int = 0

    def acquire(self, *, target: OperationTarget) -> TargetState:
        self._require_target(target)
        self.acquire_calls += 1
        return TargetState(
            revision=str(self.revision),
            artifact_digest=self.artifact_digest,
            provenance_reference=f"stub:acquire:{self.acquire_calls}:rev:{self.revision}",
        )

    def apply(
        self,
        *,
        target: OperationTarget,
        artifact_content: str,
        artifact_digest: str,
        expected_revision: str,
        operation_id: str,
    ) -> ApplyResult:
        self._require_target(target)
        self.apply_calls += 1
        if self.scenario is StubScenario.CONCURRENT_CHANGE:
            self.revision += 1
        if str(self.revision) != expected_revision:
            return ApplyResult(
                status=ApplyStatus.PRECONDITION_FAILED,
                operation_reference=f"stub:apply:{operation_id}:revision-conflict",
                reason="target revision changed before apply",
            )
        if self.scenario is StubScenario.REJECT:
            return ApplyResult(
                status=ApplyStatus.REJECTED,
                operation_reference=f"stub:apply:{operation_id}:rejected",
                reason="stub rejected mutation",
            )
        if self.scenario is StubScenario.UNKNOWN_APPLY:
            return ApplyResult(
                status=ApplyStatus.UNKNOWN,
                operation_reference=f"stub:apply:{operation_id}:unknown",
                reason="stub simulated timeout after submission",
            )
        self.revision += 1
        self.artifact_digest = artifact_digest
        if self.scenario is StubScenario.POST_APPLY_DRIFT:
            self.revision += 1
            self.artifact_digest = "stub-drifted-artifact"
        return ApplyResult(
            status=ApplyStatus.APPLIED,
            operation_reference=f"stub:apply:{operation_id}:applied",
        )

    def _require_target(self, target: OperationTarget) -> None:
        if target != self.target:
            raise ValueError("stub target mismatch")
