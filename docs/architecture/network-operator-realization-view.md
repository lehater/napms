# Network Operator Realization View Boundary

Status: `accepted I25 architecture contract`.

Date: 2026-09-10.

## Purpose

Define one read-only application composition that presents downstream realization/execution state without turning the presentation layer into a semantic owner and without introducing direct cross-context table access.

## Place in the chain

```text
Access Policy owner port
NEP owner port
TAE owner port
APR application services
NEO operation result source
        |
        v
Network Operator Realization View application composition
        |
        +-> HTTP DTO
        +-> Web operator workspace
```

The composition coordinates existing owner/application contracts. It does not own Access Rules, placement, evidence, reconciliation, rendered configuration or network operations.

## Input

First slice:
- authenticated `actor_id`;
- `governance_scope`;
- timezone-aware `as_of`;
- optional selected configured-evidence descriptor;
- optional managed-scope reconciliation contract;
- optional NEO operation-result source/reference.

Configured-evidence/contract inputs are optional at the composition boundary because the current supported runtime has no universal selected source for them. Missing optional inputs produce projection-level `NotAvailable`; they are not silently synthesized.

## Output

`NetworkOperatorRealizationView` is presentation/composition data with:
- desired stage;
- placement/target stage;
- configured/reconciliation stage;
- rendering stage;
- operation stage;
- ordered diagnostic/gap references.

Each stage carries a composition-level availability enum:
`Available | NotAvailable | Unknown`.

When `Available`, the stage carries only owner/application values already safe to expose through this use case. When `Unknown`, it carries a stable semantic reason/code rather than raw adapter exceptions or source payloads.

## Authority

The view has its own read admission at the application boundary. Authority Management remains the authority source. Mutation authority is not implied.

The composition may either consume a dedicated view-read authority port or be wired from an accepted existing read admission only if the owning requirement explicitly states equivalence. I25 must not infer permission from UI navigation or from unrelated Rule-read authority.

## Desired / placement / rendering

APR already consumes Access Policy, RC/ACC and NEP through owner-preserving adapters. The view should reuse APR derivation/rendering rather than reimplement placement or rendering logic.

Mapping:
- APR `Derived` => desired `Available`;
- APR `Ambiguous | Unknown` => desired `Unknown` with existing gap/provenance references;
- enforcement targets come only from derived APR intents/placement projection;
- rendering comes only from APR rendering result; unsupported/unknown rendering remains explicit and is not converted to an empty configuration.

## Configured evidence / reconciliation

Reconciliation requires two selected inputs:
1. an actual TAE configured evidence set;
2. an explicit `ManagedReconciliationScopeContract` describing which technical state is complete for the managed target/scope.

Rules:
- either missing => reconciliation `NotAvailable`;
- evidence/contract present but incomplete/ambiguous/unknown => `Unknown` or APR-owned unknown result;
- only APR reconciliation may produce `Satisfied | Drift` and `NoOp | Add | Remove | Replace` semantics;
- the view never treats an empty evidence set as complete unless the supplied managed-scope contract explicitly says it is complete.

## Operation evidence

Rendering does not imply execution.

The view may present a NEO `NetworkOperationResult` only when supplied/resolved from an actual NEO operation source. It preserves NEO outcome and pre/apply/post evidence without reinterpretation.

Current I22 in-memory NEO repository is sufficient for process-local local-demo operation presentation but does not become crash-durable audit. If no operation source/result is wired, operation availability is `NotAvailable`.

## Persistence

No new cross-context persistence is allowed for this view.

If later query performance requires caching/projection persistence, that requires a separate accepted decision describing freshness, ownership, rebuild semantics and failure behavior.

## Runtime adapters

HTTP maps projection values to transport DTOs only. HTTP does not inspect NEP/TAE/APR tables directly.

Web renders stage status/provenance and may trigger navigation to existing Requirement/Decision/Rule views. Web does not recompute reconciliation or execution status.

## Local deterministic fixtures

The local demo may seed/import deterministic NEP and TAE facts and supply a deterministic managed-scope contract where necessary to demonstrate the accepted product chain. Those inputs are local bootstrap fixtures, not enterprise source claims.

NEO controlled execution may use the accepted deterministic target stub. The UI must label that local execution target according to product presentation requirements and must not describe it as real Cisco application.

## Failure rules

- missing optional input => `NotAvailable`;
- ambiguous/incomplete selected semantic input => `Unknown`;
- dependency failure => fail closed, no partial stage promoted to `Available` beyond what can be independently established;
- no rendered artifact => no executable operation target inferred;
- no actual NEO result => no execution success inferred;
- exceptions/source payloads/credentials remain outside user-facing output.

## Dependency direction

The new composition may depend on APR/NEO application/domain projection types at the composition/application edge, but existing semantic modules do not gain dependencies on the operator view.

No Domain package imports runtime/HTTP/Web types.
