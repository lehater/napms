# Active execution

Current: `PLAN-I32-code-structure-refactoring.md`
Goal: align physical code ownership with the accepted context-first Clean/Hexagonal architecture without changing product/domain semantics.
Current task: WP-3 — finalize the M6 Connectivity Requirements API locality pilot in PR #67.

## Working set

Read first:
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`
- `web/src/features/requirements/api.ts`
- `tests/architecture/test_web_feature_locality.py`

Expand only to `web/src/api.ts`, shared Web transport, or failed Web/browser tests when required. Do not refactor `App.tsx` or other feature pages by size alone.

## Blockers

None known.

## Gate

Requirement-specific API implementation is feature-local. Root `api.ts` may retain compatibility exports and genuinely shared types, but no Requirement DTO/query/command implementation. Shared request/error handling lives in `web/src/lib/api.ts`. Web, Harness and relevant browser/runtime gates must be green on the final head.

## Next

Resolve only final-gate failures for PR #67, evaluate whether the pilot improves locality without compensating indirection, and do not select another M6 hotspot until that evaluation is complete.
