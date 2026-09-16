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
- M5 validation model: next.

## Blockers

None for M5.

## Next

Complete M5 validation model only: define validation layers/profiles, artifact syntax/structure/consistency checks, gate evidence checks, CI/local responsibilities and failure routing. Do not implement the full validator suite or migrate product documentation during M5.
