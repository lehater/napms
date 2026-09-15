# Network Environment Operations architecture boundary

## Purpose

Realize controlled network-target mutation without leaking provider transport, persistence or framework mechanics into NEO Domain/Application semantics.

## Module boundary

NEO is a framework-independent semantic module with Domain, Application and consumer-owned ports. Provider/device transports, persistence adapters and deterministic test adapters remain outer infrastructure.

```text
TargetPolicyArtifact
    -> NEO Application: ExecuteNetworkOperation
        -> MutationAuthorityPort
        -> OperationRepository
        -> TargetExecutionPort
            <- provider/device adapter
            <- deterministic test adapter
```

Network Environment Operations owns operation identity, mutation workflow state, execution outcome and operation provenance. It does not own rendered policy meaning or enforcement-target identity.

## Ports

Application owns:

- `MutationAuthorityPort` — action-specific admission for network mutation;
- `TargetExecutionPort` — acquire operation-scoped current target state and apply one artifact under an expected revision;
- `OperationRepository` — reserve/load/store operation identity and established result for idempotency.

No device SDK, SSH/REST client, database-driver or framework type enters Domain/Application.

General technical-evidence acquisition does not use NEO as its semantic gateway. Acquisition and NEO may share lower-level provider/device client infrastructure only when Architecture chooses that realization without merging their ports or ownership.

## Concurrency and idempotency

`operationId` is the command idempotency identity. Target revision/base correlation is the optimistic-concurrency boundary.

The application sequence is:

1. validate or reserve operation identity;
2. authorize the mutation action;
3. acquire operation-scoped pre-state;
4. validate expected revision/base correlation;
5. apply against the acquired revision;
6. when apply is definitely accepted, reacquire operation-scoped post-state;
7. verify correspondence to the supplied artifact;
8. persist the final operation result.

A target adapter must make apply conditional on the supplied concurrency expectation. If the provider cannot establish that guarantee, the adapter reports the resulting uncertainty explicitly rather than manufacturing `Verified`.

Conflicting reuse of one operation ID for a different target/artifact intent fails closed. An identical retry returns the established result and does not repeat mutation.

## Failure boundary

Provider/transport failures are translated by adapters into the explicit NEO outcome vocabulary. Application code does not infer success from request submission, connection state or transport acknowledgement alone.

An unknown apply outcome remains `Unknown`; it is not blindly retried or converted to success. A stale/mismatched precondition prevents mutation.

## Persistence

`OperationRepository` is owned by NEO Application. Its concrete storage is an outer adapter. Durable persistence is required whenever the selected runtime must preserve operation idempotency/outcome across process failure; an in-memory implementation is valid only for deterministic test/composition scenarios that make the non-durable boundary explicit.

Repository mechanics do not alter NEO semantic identity or outcome rules.

## Authority

Authority Management remains the semantic owner of mutation eligibility. NEO consumes an explicit action/scope admission through `MutationAuthorityPort`.

A test composition may supply a deterministic authority adapter, but no target adapter may bypass or infer mutation authority from provider credentials, Resource metadata or transport access.

## Dependency direction

```text
NEO Domain
    ^
    |
NEO Application + NEO-owned ports
    ^
    |
persistence / authority / provider adapters / composition
```

## Architecture guardrails

- no provider SDK or transport type in Domain/Application;
- no provider policy interpretation or rendering inside NEO;
- no general TAE acquisition/read gateway hidden behind `TargetExecutionPort`;
- no mutation before explicit authority admission and precondition validation;
- no blind retry after uncertain apply outcome;
- no cross-context private-model or repository access;
- no claim of semantic convergence from transport success alone.
