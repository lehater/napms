# Current implementation state

Status: `I4 PASS — I5 Export Snapshot refinement may begin under the active plan`.

Date: 2026-09-08.

Current execution is owned by `docs/plans/active/README.md`; do not mirror its work-package status here.

## Completed through I4

- accepted Wave-1 product/quality/acceptance baseline;
- accepted Strategic DDD baseline and Access Policy tactical model;
- accepted target architecture and ADRs;
- I1 authoritative Access Rule materialization core;
- I2 PostgreSQL uniqueness/concurrency/rollback persistence proof;
- I3 authorized Active/Inactive mutation with durable business audit;
- stable non-identity `RuleGovernanceScope`;
- first supported declarative condition `EffectiveWindow(start, end)`;
- offset-aware half-open condition semantics: `start <= as-of < end`;
- recurring/calendar/cron/frequency-duration condition semantics explicitly deferred;
- authorized `SetRuleEffectiveWindow` using stored RuleGovernanceScope;
- immutable business property-change audit for accepted old/new EffectiveWindow changes;
- same-window request is an explicit non-change with no audit;
- authoritative AccessRule now enforces Allowed on every construction/hydration path;
- authorized `SelectEffectiveDesiredPolicy(scope, asOf, actor)` for one RuleGovernanceScope;
- selection checks `ReadEffectiveDesiredPolicy` authority before repository access;
- application verifies repository scope contract and evaluates Active/window semantics using explicit logical `asOf`;
- PostgreSQL persists current EffectiveWindow separately from append-only property history;
- aggregate row locking serializes state and window mutations;
- stale/concurrent snapshots cannot create multiple accepted same-property changes;
- state/window mutations can interleave while preserving both audit chains;
- rollback reverts current property and audit together;
- failed/unknown commit acknowledgement never becomes application success;
- PostgreSQL scope query supplies membership only; effectiveness remains core semantics;
- final I4 domain/application/persistence review has no open P0/P1 finding;
- core, harness and PostgreSQL persistence gates passed on the I4 implementation candidate.

## I4 result

`PASS`.

Effective desired-policy selection is now executable and persistence-backed without coupling temporal effectiveness semantics to SQL or wall-clock time.

## Current infrastructure boundary

Access Policy materialization, operational-state mutation, EffectiveWindow mutation and exact RuleGovernanceScope reads are admitted and proven.

HTTP and real Authority/Resource Catalogue/Application Communication Catalogue/Connectivity Decision adapters are still not implied by I4.

I5 returns inside-out to application composition: assemble an immutable coherent Export Snapshot from already selected effective Rules plus owner-provided catalogue facts before normalization or real catalogue integration.
