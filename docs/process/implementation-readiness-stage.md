# Implementation Readiness stage

## Purpose

Use this protocol for lifecycle stage `S4 Implementation Readiness` before code modification begins.

S4 answers:

> What exactly must change in the current system, in what coherent slices, with which tests/migrations/compatibility constraints, so implementation can proceed without inventing requirements, domain semantics or architecture?

S4 is still design/planning work. It does not authorize code edits until G4 passes.

## Inputs

Use the smallest applicable set of:

- accepted upstream guarantees required by the change (G1/G2/G3 as applicable);
- current architecture/ADR constraints;
- affected current code/tests/schema/configuration as implementation evidence;
- active plan/problem context;
- migration/compatibility/operational constraints relevant to the concrete change.

For a legitimately implementation-only change entering directly at S4, verify that no missing upstream semantic/architecture guarantee is required before proceeding.

## Responsibility boundary

S4 may define:

- affected modules/files/packages/contracts;
- current-to-target gap;
- implementation slices and their dependency order;
- exact code ownership location under accepted architecture;
- migrations/data backfills/compatibility steps already implied by accepted architecture;
- tests/evals/architecture checks required to prove the change;
- rollout/rollback or migration checkpoints where material;
- local risk and verification strategy;
- which existing code is replaced/removed versus retained.

S4 must not decide:

- new product behavior;
- new domain identity/lifecycle/invariant/ownership;
- new Bounded Context relationship/semantic contract;
- architecture responsibility/data-ownership/dependency-direction choices not already accepted.

If such a choice is discovered, reopen the owning upstream stage.

## Implementation-impact loop

1. **Restate target guarantees.** Identify the accepted behavior/domain/architecture guarantees the implementation must realize.
2. **Map affected current paths.** Inspect only code/tests/data/schema/configuration that can materially implement or block the target.
3. **Describe current -> target gaps.** Separate missing behavior, obsolete behavior, structural migration and test gaps.
4. **Classify each gap by owner.** If solving it requires upstream semantics/architecture, `REOPEN` rather than hiding the decision in an implementation task.
5. **Choose implementation slices.** Prefer the smallest vertical/coherent increments that can be implemented and verified independently without temporary semantic contradictions.
6. **Order only real dependencies.** Do not manufacture a long roadmap when slices are independent.
7. **Define migration/compatibility work.** State schema/data/API/adapter transitions, coexistence constraints and removal conditions when relevant.
8. **Define executable proof.** Identify unit/core/architecture/integration/E2E/harness/knowledge checks required by the affected scope.
9. **Define completion evidence.** State what observable/testable result closes each slice and the overall change.
10. **Challenge scope.** Remove speculative refactors, generic abstractions and unrelated cleanup.
11. **Challenge readiness.** Ask whether an implementer can perform each slice without making a new product/domain/architecture decision.
12. **Update active plan/working package** with the implementation scope and evaluate G4.

## Traceability check

For each material implementation slice, the chain should be recoverable:

```text
accepted requirement / problem
-> domain guarantee when applicable
-> architecture decision/constraint when applicable
-> implementation impact
-> executable proof
```

Not every trivial code line needs a traceability record. The chain is required for decisions whose ownership could otherwise be lost during implementation.

## G4 — Ready to implement

`G4 PASS` means code modification is permitted for the affected scope because:

- required upstream guarantees are accepted and applicable;
- affected code/data/contract boundaries are understood sufficiently;
- current-to-target gaps are explicit;
- implementation slices and real dependencies are identified;
- migration/compatibility constraints are known where material;
- required executable checks/evidence are identified;
- no unresolved P0/P1 upstream decision is delegated to the implementer;
- the planned implementation preserves accepted ownership/dependency direction;
- the scope is small/coherent enough to execute and review.

### G4 outcomes

- `PASS` — code change is permitted for the accepted implementation scope; route execution to the applicable implementation Skill/work package.
- `REWORK` — S4 impact/slicing/test/migration plan is insufficient but no upstream decision is missing.
- `REOPEN(S3)` — responsibility placement, data ownership, dependency direction, consistency or migration architecture is unsettled.
- `REOPEN(S2)` — semantic ownership/identity/lifecycle/invariant/contract is unsettled.
- `REOPEN(S1)` — observable behavior/quality/authority expectation is unsettled.
- `REOPEN(S0)` — the problem/evidence premise is invalid.
- `BLOCKED` — required implementation evidence/constraint is unavailable and cannot currently be derived.

## Direct-entry implementation-only changes

A task may enter at S4 when it genuinely changes only implementation realization under already accepted behavior/domain/architecture.

Before G4 PASS, explicitly verify:

- no accepted behavior changes;
- no semantic identity/lifecycle/invariant/ownership changes;
- no architecture ownership/dependency/data-boundary changes;
- existing upstream guarantees are sufficient for the change.

If any answer is uncertain and material, reopen the earliest affected stage.

## Context contract

Normal S4 startup:

```text
root AGENTS.md
-> active resume capsule
-> scoped AGENTS.md
-> this protocol while S4/G4 is active
-> smallest accepted upstream artifacts needed for the slice
-> affected code/tests/schema/config only
-> implementation Skill only after G4 PASS
```

Do not preload all upstream documentation; use accepted references/capsule facts and open canonical artifacts only when the implementation impact requires them.

After G4 PASS, compact transition context before implementation when useful: persist the accepted implementation scope, checks, blockers and next slice in the active capsule/plan, then let the implementation session load only what that slice needs.

## Relationship to implementation Skills

- `implement-slice` executes a domain/application vertical slice **after** G4; it does not replace G4.
- `execute-work-package` executes an accepted work package and likewise must not silently decide missing upstream semantics.
- implementation findings that invalidate accepted assumptions use `REOPEN(stage)` through `change-lifecycle.md`.
- `working-loop.md` owns branch/checkpoint/validation/rollover mechanics during execution.
