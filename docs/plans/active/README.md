# Active execution

Current: `PLAN-I32-code-structure-refactoring.md`
Goal: align physical code ownership with the accepted context-first Clean/Hexagonal architecture without changing product/domain semantics.
Current task: WP-3 — finish Policy + scoped Connectivity Web API locality and close I32.

## Working set

Read first:
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`
- `web/src/features/policy/api.ts`
- `web/src/features/connectivity/api.ts`
- `tests/architecture/test_web_feature_locality.py`

Expand only to root `web/src/api.ts`, canonical engineering docs needed for I32 closure, or failed gates. Do not refactor proposal/auth/App routing without new evidence.

## Blockers

None known.

## Gate

Policy and scoped Connectivity endpoint implementation must be feature-local. Root API may keep genuinely shared DTOs, proposal capability and application-level auth/session. Web, Harness, Core, Docker runtime and browser journeys must be green before I32 closure and squash integration.

## Next

Validate the final locality slice. On green gates, absorb completion into canonical engineering docs, clear active execution, rerun the final hosted gate, then squash-integrate.
