# PLAN — Documentation System v2

Status: active

## Goal

Design and validate a replacement documentation/artifact system incrementally, without changing current canonical product truth until an explicit cutover.

## Inputs

- current lifecycle/process/Harness conventions;
- `docs-v2/README.md` charter;
- `docs-v2/spec/*` design specifications;
- `docs-v2/migration/plan.md` migration roadmap.

## Exit criteria

- M1-M6 specifications complete;
- one M7 pilot completed and findings absorbed;
- v2 readiness review passes;
- migration/cutover can proceed without ambiguous canonical ownership.

## Progress

- M0 foundation: complete.
- M1 lifecycle contract: complete.
- M2 artifact model: complete.
- M3 repository layout: complete.
- M4 agent execution model: complete.
- M5 validation model: complete.
- M6 migration plan: complete.
- M7 bounded pilot: next.

## Blockers

None for pilot selection.

## Next

M7 task 1 only: select one already-implemented representative product slice using the criteria in `docs-v2/migration/plan.md`, inventory its current requirements/domain/architecture/contracts/tests, and record the pilot scope plus legacy-to-v2 disposition map. Do not migrate the slice until that bounded inventory/selection task is complete.
