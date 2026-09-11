# Active execution

Current: `PLAN-I33-code-structure-locality-cleanup.md`
Goal: I33 Code Structure Locality Cleanup removes proven residual compatibility/locality debt after completed I32 without changing product, domain, API or persistence semantics.
Current task: S2 — removal of residual Catalogue HTTP compatibility facades.

Working branch: `refactor/code-structure-locality`.

## Working set

Read first:
- `docs/plans/active/PLAN-I33-code-structure-locality-cleanup.md`
- `tests/application_catalogue/test_temporal_curation_http.py`
- `tests/resource_catalogue/test_temporal_curation_http.py`
- `tests/architecture/test_dependency_rules.py`

Expand only to the PostgreSQL integration consumer and failures directly caused by S2. Do not redesign HTTP APIs, change route contracts or application/domain semantics, resize legacy owner modules, or touch other runtime modules.

## Blockers

None known.

## Gate

The two Catalogue HTTP facades must be absent, imports and tests must bind directly to semantic owners, owner-local tests must pass, the architecture guard must prevent all `runtime/catalogue_*_http.py` facades, and `make check` must pass.

## Next

Execute S2, validate, push, then coordinator review.
