# PLAN — Documentation System v2

Status: active

## Goal

Design and validate a replacement documentation/artifact system incrementally, without changing current canonical product truth until an explicit cutover.

## Inputs

- current lifecycle/process/Harness conventions;
- `docs-v2/README.md` charter;
- `docs-v2/spec/*` design specifications;
- `docs-v2/migration/plan.md` iteration roadmap.

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
- M6 migration plan: next.

## Blockers

None for M6.

## Next

Complete M6 migration plan only: inventory/map current `docs/` and Harness/CI ownership to v2 artifact types and profiles, define migration batches, pilot selection criteria, canonical-truth safeguards, cutover/rollback procedure and retirement of old documentation. Do not perform the migration during M6.
