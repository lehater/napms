from napms.network_environment_operations.domain import (
    ApplyStatus,
    ExecuteNetworkOperationCommand,
    NetworkOperationResult,
    OperationOutcome,
)
from napms.network_environment_operations.ports import (
    MutationAuthorityPort,
    OperationRepository,
    TargetExecutionPort,
)


class ExecuteNetworkOperation:
    def __init__(
        self,
        *,
        authority: MutationAuthorityPort,
        target: TargetExecutionPort,
        operations: OperationRepository,
    ) -> None:
        self._authority = authority
        self._target = target
        self._operations = operations

    def execute(
        self,
        command: ExecuteNetworkOperationCommand,
    ) -> NetworkOperationResult:
        existing = self._operations.get(command.operation_id)
        if existing is not None:
            if (
                existing.target != command.target
                or existing.artifact_digest != command.artifact_digest
            ):
                raise ValueError("operation id already bound to different intent")
            return existing

        if not self._authority.may_execute(
            actor_id=command.actor_id,
            authority_scope=command.authority_scope,
            target=command.target,
        ):
            return self._finish(
                command,
                outcome=OperationOutcome.PRECONDITION_FAILED,
                reason="network mutation authority denied or unknown",
                provenance=("authority:denied",),
            )

        pre = self._target.acquire(target=command.target)
        provenance = [pre.provenance_reference]
        if (
            command.expected_pre_revision is not None
            and command.expected_pre_revision != pre.revision
        ):
            return self._finish(
                command,
                outcome=OperationOutcome.PRECONDITION_FAILED,
                pre_state=pre,
                reason="expected pre-state revision does not match acquired revision",
                provenance=tuple(provenance),
            )

        applied = self._target.apply(
            target=command.target,
            artifact_content=command.artifact_content,
            artifact_digest=command.artifact_digest,
            expected_revision=pre.revision,
            operation_id=command.operation_id,
        )
        provenance.append(applied.operation_reference)
        if applied.status is ApplyStatus.PRECONDITION_FAILED:
            return self._finish(
                command,
                outcome=OperationOutcome.PRECONDITION_FAILED,
                pre_state=pre,
                apply_result=applied,
                reason=applied.reason or "target revision changed before apply",
                provenance=tuple(provenance),
            )
        if applied.status is ApplyStatus.REJECTED:
            return self._finish(
                command,
                outcome=OperationOutcome.REJECTED,
                pre_state=pre,
                apply_result=applied,
                reason=applied.reason or "target rejected mutation",
                provenance=tuple(provenance),
            )
        if applied.status is ApplyStatus.UNKNOWN:
            return self._finish(
                command,
                outcome=OperationOutcome.UNKNOWN,
                pre_state=pre,
                apply_result=applied,
                reason=applied.reason or "apply outcome is unknown",
                provenance=tuple(provenance),
            )

        post = self._target.acquire(target=command.target)
        provenance.append(post.provenance_reference)
        if post.artifact_digest != command.artifact_digest:
            return self._finish(
                command,
                outcome=OperationOutcome.DRIFT,
                pre_state=pre,
                apply_result=applied,
                post_state=post,
                reason="post-state does not match requested artifact",
                provenance=tuple(provenance),
            )
        return self._finish(
            command,
            outcome=OperationOutcome.VERIFIED,
            pre_state=pre,
            apply_result=applied,
            post_state=post,
            reason=None,
            provenance=tuple(provenance),
        )

    def _finish(
        self,
        command: ExecuteNetworkOperationCommand,
        *,
        outcome: OperationOutcome,
        reason: str | None,
        provenance: tuple[str, ...],
        pre_state=None,
        apply_result=None,
        post_state=None,
    ) -> NetworkOperationResult:
        result = NetworkOperationResult(
            operation_id=command.operation_id,
            target=command.target,
            artifact_digest=command.artifact_digest,
            outcome=outcome,
            pre_state=pre_state,
            apply_result=apply_result,
            post_state=post_state,
            reason=reason,
            provenance_references=provenance,
        )
        self._operations.save(result)
        return result
