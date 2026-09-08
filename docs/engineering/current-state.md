# Current implementation state

Status: `I3 PASS — I4 effective desired-policy refinement may begin under the active plan`.

Date: 2026-09-08.

Current execution is owned by `docs/plans/active/README.md`; do not mirror its work-package status here.

## Completed through I3

- accepted Wave-1 product/quality/acceptance baseline;
- accepted Strategic DDD baseline and Access Policy tactical model;
- accepted target architecture and ADRs;
- I1 Access Policy materialization Domain/Application/Ports core;
- I2 PostgreSQL authoritative uniqueness/concurrency/rollback proof;
- stable non-identity `RuleGovernanceScope` established from accepted proposal authority scope;
- authorized `SetRuleOperationalState` application behavior with no caller-supplied mutation scope;
- explicit `AlreadyInRequestedState` non-transition semantics;
- immutable business operational-state audit carrying Rule/from/to/actor/effective time/governance scope/authority provenance;
- denied/unknown mutation authority fails closed without state/audit mutation;
- RuleId, RuleSemanticIdentity, RuleGovernanceScope and Connectivity Decision correlation survive state transitions unchanged;
- PostgreSQL migration for append-only per-Rule transition history;
- PostgreSQL state update and transition-audit insert share one transaction;
- stale/concurrent same-target state mutation cannot create multiple accepted transitions;
- rollback reverts state and audit together;
- failed/unknown commit acknowledgement never becomes application success;
- core remains independent of PostgreSQL/framework/infrastructure imports;
- final I3 core/model/transaction/architecture review has no open P0/P1 finding;
- core, harness and PostgreSQL persistence gates passed on the I3 implementation candidate.

## I3 result

`PASS`.

The operational-state behavior is now proven both as infrastructure-independent Domain/Application semantics and against PostgreSQL transaction/concurrency behavior.

## Current infrastructure boundary

Access Policy materialization and operational-state mutation persistence are admitted and proven.

HTTP and real Authority/Catalogue/Connectivity Decision adapters are still not implied by I3.

I4 returns to domain/application-first work: effective desired-policy semantics and declarative conditions must be refined and proven in core before new persistence/query infrastructure is allowed to shape them.
