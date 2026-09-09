from typing import Protocol

from napms.access_policy_realization.domain.realization import EnforcementTarget
from napms.network_environment_operations.domain import (
    ApplyResult,
    NetworkOperationResult,
    TargetState,
)


class MutationAuthorityPort(Protocol):
    def may_execute(
        self,
        *,
        actor_id: str,
        authority_scope: str,
        target: EnforcementTarget,
    ) -> bool: ...


class TargetExecutionPort(Protocol):
    def acquire(self, *, target: EnforcementTarget) -> TargetState: ...

    def apply(
        self,
        *,
        target: EnforcementTarget,
        artifact_content: str,
        artifact_digest: str,
        expected_revision: str,
        operation_id: str,
    ) -> ApplyResult: ...


class OperationRepository(Protocol):
    def get(self, operation_id: str) -> NetworkOperationResult | None: ...

    def save(self, result: NetworkOperationResult) -> None: ...
