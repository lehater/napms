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

## Completed slice S4

- Make `runtime/http_support.py` own shared HTTP transport primitives.
- Bind semantic-owner adapters directly to `napms.runtime.http_support`.
- Prevent semantic module adapters from depending on process HTTP assembly.

## Completed slice S5

- Replace the legacy HTTP monolith with a process-only runtime shell.
- Keep only session, middleware/error boundary, logging, liveness/readiness and executable HTTP assembly in process runtime.
- Localize feature exception mappings in semantic-owner adapters.
- Register owner-local error handlers and routers from process composition.
- Remove the legacy HTTP module and migration filtering mechanism.

## Completed slice S6

- Keep `runtime/http_support.py` limited to genuinely shared process/transport helpers.
- Move Catalogue-specific validation and mutation mapping to owner-local Application Catalogue and Resource Catalogue HTTP support modules.
- Preserve the existing HTTP contracts, status codes, messages and application/domain semantics.
- Keep Application Catalogue and Resource Catalogue separate; intentional small duplication does not establish a shared Catalogue owner.
- Do not perform size-based refactoring of other HTTP adapters.

## Explicit non-goals

- Do not change product, domain, API, session, cookie, correlation, logging, readiness or persistence semantics.
- Do not expand architectural scope beyond HTTP ownership/locality cleanup.

## Exit criteria

- `src/napms/runtime/http_support.py` contains only shared process/transport support and no Catalogue-specific validation or mutation mapping.
- Application Catalogue and Resource Catalogue adapters import Catalogue-specific helpers from their respective owner-local support modules.
- Architecture guards protect both owner-local support locations and the runtime boundary.
- `make check` passes.

## Blockers

None known.

## Next

Coordinator review; select the next evidence-backed slice before further implementation.
