# Network Environment Operations architecture boundary

Status: `accepted I22 stub-first architecture`.

Date: 2026-09-10.

## Decision

I22 is implemented as a separate framework-free semantic module with Domain + Application + consumer-owned ports. Provider/device transports and the deterministic stub are outer adapters.

```text
I21 RenderedConfiguration
    -> NEO Application: ExecuteNetworkOperation
        -> AuthorityPort
        -> OperationRepository
        -> TargetExecutionPort
            <- deterministic target stub first
            <- real Cisco adapter later when selected by evidence
```

Network Environment Operations (NEO) owns operation identity, mutation workflow state, execution outcome and execution audit semantics. It does not own rendered configuration semantics or Enforcement Target identity.

## Stub-first constraint

No real lab is currently available. Therefore the first transport adapter is an in-process deterministic target simulator. It must expose the same acquisition/apply contracts needed by a future real adapter while making its non-production status explicit in naming and composition.

Passing stub tests proves only NEO orchestration semantics.

## Ports

Application owns:
- `MutationAuthorityPort` — action-specific admission for network mutation;
- `TargetExecutionPort` — acquire current target state and apply one artifact under expected revision;
- `OperationRepository` — reserve/load/store operation identity/result for idempotency.

No device SDK, SSH client, REST client, database or framework type enters Domain/Application.

## Concurrency/idempotency

Operation id is the command idempotency key. Target revision is the optimistic concurrency token.

The application sequence is:
1. validate/reserve operation identity;
2. authorize mutation;
3. acquire pre-state;
4. compare expected revision if supplied;
5. apply against acquired revision;
6. on definite apply success, reacquire post-state;
7. compare post-state artifact digest;
8. persist final operation result.

A target adapter must make an apply call conditional on the supplied expected revision. If it cannot provide that guarantee, the adapter contract is insufficient for `Verified` and must map uncertainty explicitly.

## Failure boundary

Transport exceptions/timeouts are mapped by adapters into explicit `Rejected` or `Unknown` apply outcomes. Application code must not infer success from submission or connection state.

Unknown apply outcome terminates the first-slice operation as `Unknown`; no automatic retry/rollback is attempted.

## Persistence

The first slice uses an in-memory operation repository. This is sufficient to prove lifecycle/idempotency in-process, not crash recovery. Durable operation persistence is a later I22 stage only if selected before final absorption.

## Authority

Authority Management remains semantic owner of action eligibility. The first executable stub composition may use a deterministic authority adapter for tests, but the application dependency remains an explicit port so mutation authority cannot be bypassed by a real transport adapter.
