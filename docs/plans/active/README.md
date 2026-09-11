# Active execution

Current: `PLAN-I32-code-structure-refactoring.md`
Goal: align physical code ownership with the accepted context-first Clean/Hexagonal architecture without changing product/domain semantics.
Current task: WP-1 — validate the completed M1-M4 backend structural migration in PR #65 and fix only gate regressions.

## Working set

Read first:
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`
- `src/napms/bootstrap/composition.py`
- `tests/architecture/test_bootstrap_structure.py`

Expand only to the failing gate's owner-local HTTP/adapters/tests, `runtime/http_api.py` / `legacy_http_api.py`, or the smallest Harness file needed to diagnose a reported failure. Do not load M5/M6 work by default.

## Blockers

Final hosted gates are running; failures are treated as concrete WP-1 blockers until resolved.

## Gate

M1-M4 are implemented in PR #65 and the PR is Ready for review. The final gate is the repository's hosted Ready-for-review workflow set. Preserve behavior/API semantics and fix only failures caused by this structural migration. Harness plan validation, architecture rules, core tests, PostgreSQL persistence, Docker local runtime, and browser journey checks must be green before squash integration.

## Next

Re-run the final gate after each targeted fix. When all required hosted checks are green, record WP-1 completion and prepare the single squash integration; keep M5 backend granularity and M6 Web locality out of this PR.
