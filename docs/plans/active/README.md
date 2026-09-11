# Active execution

Current: `PLAN-I33-code-structure-locality-cleanup.md`
Goal: I33 Code Structure Locality Cleanup removes proven residual compatibility/locality debt after completed I32 without changing product, domain, API or persistence semantics.
Current task: S4 — decouple shared HTTP transport contract from process assembly.

Working branch: `refactor/code-structure-locality`.

## Working set

Read first:
- `docs/plans/active/PLAN-I33-code-structure-locality-cleanup.md`
- `src/napms/runtime/http_support.py`
- `tests/architecture/test_dependency_rules.py`

Expand only to production semantic-owner adapter consumers and failures directly caused by S4. Move only the shared transport primitive ownership and adapter import sources; do not change routes, error JSON, session behavior, `HttpApiDependencies`, logging/middleware or domain/application semantics, and do not remove `legacy_http_api.py`.

## Blockers

None known.

## Gate

`http_support.py` must own the shared primitives without importing process assembly; legacy/runtime compatibility must remain; semantic-owner adapters must not import `napms.runtime.http_api`; the architecture guard, targeted runtime tests and `make check` must pass.

## Next

Coordinator reviews the pushed S4 branch and selects the next evidence-backed slice.
