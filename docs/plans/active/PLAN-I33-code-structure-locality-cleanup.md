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

## Completed slice S2

- Remove residual Catalogue HTTP compatibility facades from `src/napms/runtime/`.
- Bind production imports and tests directly to their Application Catalogue or Resource Catalogue semantic owners.
- Strengthen the architecture guard so `runtime` cannot contain `catalogue_*_http.py` facades.

## Current slice S3

- Move Policy Export JSON serialization from process `runtime` to the `policy_export` semantic owner.
- Bind all production consumers and serializer tests directly to the owner-local adapter.
- Add an architecture guard that protects the owner-local serializer location.

## Explicit non-goals

- Do not change the JSON contract.
- Do not change application/domain types.
- Do not refactor consuming HTTP adapters.
- Do not touch `legacy_http_api.py` except for its import path.
- Do not create a shared or global infrastructure package.

## Exit criteria

- The serializer lives at `src/napms/policy_export/adapters/http_json.py`.
- The obsolete runtime serializer is absent.
- All production consumers and tests import the owner-local serializer.
- The architecture guard protects the owner-local location.
- `make check` passes.

## Blockers

None known.

## Next

Coordinator reviews the pushed branch and selects the next evidence-backed slice.
