# Active execution

Current: `PLAN-I32-code-structure-refactoring.md`
Goal: align physical code ownership with the accepted context-first Clean/Hexagonal architecture without changing product/domain semantics.
Current task: WP-2 — finalize and integrate the completed M5 backend granularity pilot in PR #66.

## Working set

Read first:
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`
- `src/napms/application_catalogue/application/structure_curation.py`
- `tests/architecture/test_application_catalogue_granularity.py`

Expand only to PR #66 gate failures if any. Do not start another backend split or M6 Web work in this PR.

## Blockers

None known.

## Gate

The M5 pilot is implemented and evaluated. Application vs Component structure mutation implementation is owner-specific; the compatibility facade contains no use-case implementation. Core, PostgreSQL, Harness and browser journey gates must be green on the final Ready-for-review head before squash integration.

## Next

Squash-integrate PR #66 when the final gate is green. Then evaluate M6 Web locality separately and select a Web pilot only from concrete misplaced-responsibility evidence.
