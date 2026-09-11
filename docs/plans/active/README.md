# Active execution

Current: `PLAN-I32-code-structure-refactoring.md`
Goal: align physical code ownership with the accepted context-first Clean/Hexagonal architecture without changing product/domain semantics.
Current task: WP-3 — localize the Connectivity Decisions Web API slice.

## Working set

Read first:
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`
- `web/src/api.ts`
- `tests/architecture/test_web_feature_locality.py`

Expand only to `web/src/features/decisions/`, shared Web transport/types, or failed gates required by this slice. Do not load Rules/Policy/Connectivity or `App.tsx` by default.

## Blockers

None known.

## Gate

Decision-specific DTO/query/command implementation must be feature-local. Root `api.ts` may retain compatibility exports and genuinely shared types but no Decision implementation. Preserve API/UX behavior; Web, Harness, Core and relevant browser/runtime gates must remain green.

## Next

Create `features/decisions/api.ts`, remove Decision implementation from root `api.ts`, extend locality protection, and validate before selecting another M6 slice.
