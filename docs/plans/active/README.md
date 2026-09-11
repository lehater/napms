# Active execution

Current: `PLAN-I32-code-structure-refactoring.md`
Goal: align physical code ownership with the accepted context-first Clean/Hexagonal architecture without changing product/domain semantics.
Current task: WP-1 — execute backend structural migration stages M1-M4 in one Draft PR, starting with the Application Catalogue HTTP pilot.

## Working set

Read first:
- `docs/architecture/code-structure.md`
- `docs/engineering/code-structure-refactoring-roadmap.md`
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`
- `src/napms/runtime/composition.py`
- `tests/architecture/test_dependency_rules.py`

Expand only to the current stage's owner-local HTTP/adapters/tests and the smallest runtime/composition files needed to preserve wiring. Do not load M5/M6 work by default.

## Blockers

None known.

## Gate

Current local gate is M1: move the two I31 target Catalogue HTTP routers to ACC-owned HTTP adapters with no behavior/API change, update imports/tests, add executable architecture protection, and validate the smallest applicable core/PostgreSQL/HTTP/E2E plus Harness/knowledge checks available in the environment. Do not continue M2 if the pilot creates worse indirection or unresolved P0/P1 findings.

M1-M4 accumulate in one Draft PR. Final hosted gates run once on the complete Ready-for-review backend diff before squash integration.

## Next

Move `runtime/catalogue_target_http.py` and `runtime/catalogue_target_retirement_http.py` into `application_catalogue/adapters/http/`, update their internal/runtime/test imports and architecture rules, then evaluate the M1 locality result before classifying remaining Catalogue HTTP for M2.
