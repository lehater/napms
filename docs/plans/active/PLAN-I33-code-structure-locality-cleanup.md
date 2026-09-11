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

## Completed slice S3

- Move Policy Export JSON serialization from process `runtime` to the `policy_export` semantic owner.
- Bind all production consumers and serializer tests directly to the owner-local adapter.
- Add an architecture guard that protects the owner-local serializer location.

## Current slice S4

- Make `runtime/http_support.py` own the shared HTTP transport primitives
  `SESSION_COOKIE_NAME` and `PublicApiError`.
- Keep the temporary `runtime/http_api.py` compatibility surface while binding
  semantic-owner adapters directly to `napms.runtime.http_support`.
- Add an architecture guard preventing first-class semantic module adapters from
  depending on process HTTP assembly.

Goal: owner-local HTTP adapters no longer depend on `runtime.http_api` process
assembly for transport primitives.

## S4 explicit non-goals

- Do not remove `legacy_http_api.py`.
- Do not change routes, error JSON or session behavior.
- Do not move `HttpApiDependencies`.
- Do not rework logging or middleware.
- Do not change domain/application semantics.

## Exit criteria

- `http_support.py` owns `SESSION_COOKIE_NAME` and `PublicApiError` without
  importing `napms.runtime.http_api`.
- `legacy_http_api.py` and the temporary `http_api.py` compatibility surface use
  those shared primitives.
- Semantic-owner adapters do not import `napms.runtime.http_api`, enforced by an
  architecture test.
- Runtime behavior remains unchanged under targeted tests.
- `make check` passes.

## Blockers

None known.

## Next

Coordinator reviews the pushed S4 branch and selects the next evidence-backed slice.
