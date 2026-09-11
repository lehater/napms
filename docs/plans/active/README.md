# Active execution

Current: `PLAN-I32-code-structure-refactoring.md`
Goal: align physical code ownership with the accepted context-first Clean/Hexagonal architecture without changing product/domain semantics.
Current task: WP-3 — localize the Access Rules Web API slice.

## Working set

Read first:
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`
- `web/src/features/rules/api.ts`
- `tests/architecture/test_web_feature_locality.py`

Expand only to root `web/src/api.ts`, shared Web transport/types, or failed gates required by this slice. Do not load Policy/scoped Connectivity/Proposals/Auth or `App.tsx` by default.

## Blockers

None known.

## Gate

Rule-specific list/detail/query/mutation implementation must be feature-local. Shared `RuleDto` may remain shared because other features consume it. Root `api.ts` may retain compatibility exports but no Access Rule endpoint implementation. Preserve API/UX behavior; Web, Harness, Core and relevant browser/runtime gates must remain green.

## Next

Validate the Rules API extraction and locality guard; resolve only slice-specific failures, then evaluate the next remaining root API responsibility.
