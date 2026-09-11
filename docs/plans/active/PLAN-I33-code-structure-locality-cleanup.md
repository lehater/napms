# I33 Code Structure Locality Cleanup

Status: `active`

Date: 2026-09-11.

## Goal

Remove proven residual compatibility/locality debt after completed I32 without changing product, domain, API or persistence semantics.

## Inputs

Canonical inputs:

- `docs/architecture/code-structure.md`
- `docs/engineering/code-structure-refactoring-roadmap.md`
- `docs/process/working-loop.md`

## Current slice S1

- Remove obsolete bootstrap compatibility facades from `src/napms/runtime/`.
- Move remaining internal imports to `napms.bootstrap`.
- Move config/composition/local-seed tests from `tests/runtime/` to `tests/bootstrap/`.
- Change the architecture guard to prevent these runtime facades from returning.

## Explicit non-goals

- Do not touch other `runtime` HTTP/auth/support files.
- Do not touch `composition/`.
- Do not change domain/application behavior.
- Do not perform other structural cleanup.

## Exit criteria

- The five facade files are absent.
- Remaining consumers use `napms.bootstrap`.
- The corresponding tests live under `tests/bootstrap/`.
- The architecture guard protects this state.
- `make check` passes.

## Blockers

None known.

## Next

Coordinator reviews the pushed branch and selects the next evidence-backed slice.
