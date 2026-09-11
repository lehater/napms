# Active execution

Current: `PLAN-I32-code-structure-refactoring.md`
Goal: align physical code ownership with the accepted context-first Clean/Hexagonal architecture without changing product/domain semantics.
Current task: WP-2 — execute the M5 backend granularity pilot for Application Catalogue structure curation.

## Working set

Read first:
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`
- `src/napms/application_catalogue/application/structure_curation.py`
- `tests/application_catalogue/test_structure_curation.py`

Expand only to direct imports/composition/HTTP adapters required by this split. Do not load other backend hotspots or M6 Web work by default.

## Blockers

None known.

## Gate

Preserve domain/API/persistence/authority/concurrency/idempotency semantics. Split only by demonstrated Application vs Component mutation responsibility. Applicable Core, PostgreSQL and Harness checks must remain green; do not continue to a second M5 hotspot unless this pilot improves locality without compensating indirection.

## Next

Split `structure_curation.py` into Application-specific and Component-specific mutation modules with minimal shared application-local plumbing, then update only direct imports/tests/composition and evaluate the pilot.
