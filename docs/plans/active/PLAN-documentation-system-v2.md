# PLAN — Documentation System v2

Status: active

## Goal

Design and validate a replacement documentation/artifact system incrementally, without changing current canonical product truth until an explicit cutover.

## Inputs

- current lifecycle/process/Harness conventions;
- `docs-v2/README.md` charter;
- `docs-v2/spec/*` design specifications;
- `docs-v2/migration/plan.md` migration roadmap;
- `docs-v2/review/harness-conformance-review.md` pre-pilot review/conformance matrix.

## Exit criteria

- M1-M6 specifications complete;
- pre-pilot P0/P1 conformance findings resolved and minimum mechanized Harness suite green;
- one M7 pilot completed and findings absorbed;
- v2 readiness review passes;
- migration/cutover can proceed without ambiguous canonical ownership.

## Progress

- M0 foundation: complete.
- M1 lifecycle contract: complete.
- M2 artifact model: complete; pre-pilot ownership correction required.
- M3 repository layout: complete.
- M4 agent execution model: complete; pilot-grade capsule validation required.
- M5 validation model: complete; conformance mapping required.
- M6 migration plan: complete.
- Pre-pilot review/conformance gate: in progress.
- M7 bounded pilot: paused pending gate.

## Blockers

M7 artifact migration is blocked by P1 findings recorded in `docs-v2/review/harness-conformance-review.md`.

## Next

Resolve pre-pilot P1 findings and implement the minimum Harness conformance checks through the existing `make harness-check` / `harness.yml` path. Reconcile with current `main` and require the suite to pass before starting M7 artifact migration.
