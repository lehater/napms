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

## Completed slice S1

- Remove obsolete bootstrap compatibility facades from `src/napms/runtime/`.
- Move remaining internal imports to `napms.bootstrap`.
- Move config/composition/local-seed tests from `tests/runtime/` to `tests/bootstrap/`.
- Change the architecture guard to prevent these runtime facades from returning.

## Current slice S2

- Remove residual Catalogue HTTP compatibility facades from `src/napms/runtime/`.
- Bind production imports and tests directly to their Application Catalogue or Resource Catalogue semantic owners.
- Strengthen the architecture guard so `runtime` cannot contain `catalogue_*_http.py` facades.

## Explicit non-goals

- Do not redesign the HTTP API or change route paths/contracts.
- Do not change application/domain semantics.
- Do not refactor `legacy_curation.py` or `legacy_temporal.py` by size.
- Do not touch other runtime modules.

## Exit criteria

- The two Catalogue HTTP facade files are absent.
- Production consumers import directly from semantic owners or shared runtime support.
- Catalogue HTTP tests live under their semantic-owner test packages and use owner routers directly.
- The architecture guard prevents any `catalogue_*_http.py` facade in `runtime`.
- `make check` passes.

## Blockers

None known.

## Next

Coordinator reviews the pushed branch and selects the next evidence-backed slice.
