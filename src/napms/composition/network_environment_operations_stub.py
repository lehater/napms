from dataclasses import dataclass

from napms.access_policy_realization.domain.realization import EnforcementTarget
from napms.network_environment_operations.adapters import (
    AllowAllMutationAuthority,
    DeterministicTargetStub,
    InMemoryOperationRepository,
    StubScenario,
)
from napms.network_environment_operations.application import ExecuteNetworkOperation


@dataclass(slots=True)
class NetworkEnvironmentOperationsStubScope:
    execute: ExecuteNetworkOperation
    target_stub: DeterministicTargetStub
    operations: InMemoryOperationRepository


def open_network_environment_operations_stub_scope(
    *,
    target: EnforcementTarget,
    scenario: StubScenario = StubScenario.SUCCESS,
) -> NetworkEnvironmentOperationsStubScope:
    target_stub = DeterministicTargetStub(
        target=target,
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
    )
