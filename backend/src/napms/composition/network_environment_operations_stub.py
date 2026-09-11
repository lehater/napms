from dataclasses import dataclass

from napms.contexts.access_policy_realization.domain.realization import EnforcementTarget
from napms.contexts.network_environment_operations.infrastructure.stubs import (
    AllowAllMutationAuthority,
    DeterministicTargetStub,
    InMemoryOperationRepository,
    StubScenario,
)
from napms.contexts.network_environment_operations.application.execute import (
    ExecuteNetworkOperation,
)
from napms.contexts.network_environment_operations.domain.model import OperationTarget


@dataclass(slots=True)
class NetworkEnvironmentOperationsStubScope:
    execute: ExecuteNetworkOperation
    target_stub: DeterministicTargetStub
    operations: InMemoryOperationRepository
    target: OperationTarget


def project_operation_target(target: EnforcementTarget) -> OperationTarget:
    return OperationTarget(
        logical_firewall_id=target.logical_firewall_id,
        enforcement_attachment_id=target.enforcement_attachment_id,
    )


def open_network_environment_operations_stub_scope(
    *,
    target: EnforcementTarget,
    scenario: StubScenario = StubScenario.SUCCESS,
) -> NetworkEnvironmentOperationsStubScope:
    operation_target = project_operation_target(target)
    target_stub = DeterministicTargetStub(
        target=operation_target,
        scenario=scenario,
    )
    operations = InMemoryOperationRepository()
    return NetworkEnvironmentOperationsStubScope(
        execute=ExecuteNetworkOperation(
            authority=AllowAllMutationAuthority(),
            target=target_stub,
            operations=operations,
        ),
        target_stub=target_stub,
        operations=operations,
        target=operation_target,
    )
