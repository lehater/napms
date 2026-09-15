# Implementation Readiness stage

## Purpose

Use S4 before product-code modification begins.

S4 answers:

> What exactly must change in the current system, in what coherent slices, with which migration/compatibility work and executable proof, so implementation does not invent requirements, domain semantics or architecture?

S4 is planning. Code edits remain forbidden until G4 passes for an explicit scope.

## Inputs

Load only:

- current accepted upstream guarantees required by the change;
- current architecture constraints;
- affected current code/tests/schema/configuration as implementation evidence;
- active plan/capsule when execution state matters;
- concrete operational/changeover constraints relevant to the selected slice.

A direct-entry implementation-only change may start at S4 only when no earlier guarantee needs to change.

## What S4 owns

- affected modules/files/packages/contracts;
- current-to-target implementation gaps;
- small coherent implementation slices and true dependency order;
- exact code ownership placement under current architecture;
- schema/data/API/adapter transition work already implied by accepted architecture;
- executable tests/evals/architecture/E2E/harness/knowledge checks;
- rollout/rollback/changeover checkpoints when material;
- local implementation risk;
- code to replace/remove versus retain.

S4 does not choose new product behavior, domain meaning/ownership, Bounded Context contracts or unaccepted architecture responsibility/data/dependency choices. Those reopen the owning upstream stage.

## Working loop

1. Restate the exact accepted guarantees the implementation must realize.
2. Inspect only current code/data/config/test paths that can implement or block those guarantees.
3. Describe current-to-target gaps.
4. Route any missing upstream decision through `REOPEN` instead of burying it in an implementation task.
5. Choose the smallest vertical/coherent slices that can be implemented and verified independently.
6. Order only real dependencies; do not create a long roadmap for independent work.
7. Define required schema/data/API/adapter changeover steps and removal conditions.
8. Define executable proof for every material slice.
9. Remove speculative refactors, generic abstractions and unrelated cleanup.
10. Confirm that an implementer can execute the slice without making a product/domain/architecture decision.
11. Record the exact current implementation scope in the active plan/capsule and evaluate G4.

## Traceability

For each material slice the current chain must be recoverable:

```text
accepted requirement/problem
-> domain guarantee when applicable
-> architecture constraint when applicable
-> implementation impact
-> executable proof
```

This is not a request for a historical traceability archive; current canonical references and the active implementation plan are sufficient.

## G4 — Ready to implement

`G4 PASS` means code modification is permitted only for the evaluated scope because:

- required upstream guarantees are current and accepted;
- affected boundaries are understood;
- implementation gaps/slices/dependencies are explicit;
- material changeover constraints are known;
- executable proof is identified;
- no P0/P1 upstream decision is delegated to the implementer;
- accepted ownership/dependency direction is preserved;
- the scope is coherent and reviewable.

Outcomes:

- `PASS` — create the scoped implementation lease and route to the applicable implementation Skill;
- `REWORK` — S4 planning/readiness is insufficient;
- `REOPEN(S3|S2|S1|S0)` — an upstream guarantee is missing or wrong;
- `BLOCKED` — required current implementation evidence/constraint is unavailable.

## Direct-entry implementation-only check

Before G4 on a direct S4 entry, verify that observable behavior, semantic identity/lifecycle/invariants/ownership and architecture responsibility/dependency/data boundaries do not need to change. If any material answer is uncertain, reopen the earliest affected stage.

## Context rule

Load root/scoped instructions, active capsule, this protocol while S4/G4 is active, the smallest current upstream artifacts needed for the slice, and only the affected code/tests/schema/configuration.

Implementation Skills are loaded only after G4. The active capsule then carries the exact authorization scope and basis; superseded plans/work packages are removed rather than retained as execution history.
