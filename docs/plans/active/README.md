# Active execution

Current: `PLAN-I32-code-structure-refactoring.md`
Goal: align physical code ownership with the accepted context-first Clean/Hexagonal architecture without changing product/domain semantics.
Current task: WP-3 — execute the M6 Connectivity Requirements API locality pilot.

## Working set

Read first:
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`
- `web/src/api.ts`
- `web/src/features/requirements/ConnectivityRequirementsPage.tsx`
- `web/src/features/requirements/ConnectivityRequirementDetailsPage.tsx`

Expand only to shared Web transport/types and relevant Web/browser tests required by this extraction. Do not refactor `App.tsx` or other feature pages by size alone.

## Blockers

None known.

## Gate

Requirement-specific API implementation must become feature-local without API/UX behavior changes. Root `api.ts` may retain compatibility exports and genuinely shared transport/types, but no Requirement implementation. Web checks, Harness and relevant browser journeys must remain green.

## Next

Create the feature-local Requirements API boundary, reduce root `api.ts` to shared/compatibility responsibility for this slice, add a locality guard, then validate the pilot before considering any other M6 hotspot.
