from uuid import UUID

import pytest

from napms.contexts.network_environment_operations.infrastructure.stubs import (
    AllowAllMutationAuthority,
    DenyAllMutationAuthority,
    DeterministicTargetStub,
    InMemoryOperationRepository,
    StubScenario,
)
from napms.contexts.network_environment_operations.application.command import (
    ExecuteNetworkOperationCommand,
)
from napms.contexts.network_environment_operations.application.execute import (
    ExecuteNetworkOperation,
)
from napms.contexts.network_environment_operations.domain.model import (
    OperationOutcome,
    OperationTarget,
)


TARGET = OperationTarget(UUID(int=22001), UUID(int=22002))
CONTENT = "access-list NAPMS extended permit tcp host 10.0.0.1 host 192.0.2.1 eq 443\n"
DIGEST = "sha256:artifact-a"


def command(operation_id="op-1", *, digest=DIGEST, expected=None):
    return ExecuteNetworkOperationCommand(
        operation_id=operation_id,
        target=TARGET,
        renderer_name="cisco-asa-extended-acl",
        renderer_contract_version="1",
        artifact_content=CONTENT,
        artifact_digest=digest,
        actor_id="actor-i22",
        authority_scope="scope-i22",
        expected_pre_revision=expected,
    )


def use_case(stub, *, authority=None, repository=None):
    return ExecuteNetworkOperation(
        authority=authority or AllowAllMutationAuthority(),
        target=stub,
        operations=repository or InMemoryOperationRepository(),
    )


def test_success_is_verified_after_post_check():
    stub = DeterministicTargetStub(TARGET)
    result = use_case(stub).execute(command())

    assert result.outcome is OperationOutcome.VERIFIED
    assert result.pre_state is not None
    assert result.post_state is not None
    assert result.post_state.artifact_digest == DIGEST
    assert stub.apply_calls == 1
    assert stub.acquire_calls == 2


def test_authority_denial_prevents_acquire_and_apply():
    stub = DeterministicTargetStub(TARGET)
    result = use_case(stub, authority=DenyAllMutationAuthority()).execute(command())

    assert result.outcome is OperationOutcome.PRECONDITION_FAILED
    assert stub.acquire_calls == 0
    assert stub.apply_calls == 0


def test_stale_expected_revision_prevents_apply():
    stub = DeterministicTargetStub(TARGET, revision=3)
    result = use_case(stub).execute(command(expected="2"))

    assert result.outcome is OperationOutcome.PRECONDITION_FAILED
    assert stub.apply_calls == 0


def test_concurrent_change_before_apply_is_precondition_failure():
    stub = DeterministicTargetStub(TARGET, scenario=StubScenario.CONCURRENT_CHANGE)
    result = use_case(stub).execute(command())

    assert result.outcome is OperationOutcome.PRECONDITION_FAILED
    assert stub.apply_calls == 1


def test_explicit_rejection_is_not_verified():
    stub = DeterministicTargetStub(TARGET, scenario=StubScenario.REJECT)
    result = use_case(stub).execute(command())

    assert result.outcome is OperationOutcome.REJECTED
    assert result.post_state is None


def test_unknown_apply_is_not_retried_or_post_checked():
    stub = DeterministicTargetStub(TARGET, scenario=StubScenario.UNKNOWN_APPLY)
    result = use_case(stub).execute(command())

    assert result.outcome is OperationOutcome.UNKNOWN
    assert stub.apply_calls == 1
    assert stub.acquire_calls == 1


def test_post_apply_drift_is_explicit():
    stub = DeterministicTargetStub(TARGET, scenario=StubScenario.POST_APPLY_DRIFT)
    result = use_case(stub).execute(command())

    assert result.outcome is OperationOutcome.DRIFT
    assert result.post_state is not None
    assert result.post_state.artifact_digest != DIGEST


def test_identical_operation_retry_is_idempotent():
    repository = InMemoryOperationRepository()
    stub = DeterministicTargetStub(TARGET)
    execute = use_case(stub, repository=repository)

    first = execute.execute(command())
    second = execute.execute(command())

    assert second == first
    assert stub.apply_calls == 1


def test_operation_id_reuse_with_different_artifact_conflicts():
    repository = InMemoryOperationRepository()
    stub = DeterministicTargetStub(TARGET)
    execute = use_case(stub, repository=repository)
    execute.execute(command())

    with pytest.raises(ValueError, match="different intent"):
        execute.execute(command(digest="sha256:artifact-b"))
