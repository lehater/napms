# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final backend and Web taxonomy without product/domain semantic change.
Current task: M6 implementation complete; awaiting architectural review.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: current `web/src` files being moved.

## Blockers

None.

## Gate

M6 Web locality is implemented in two atomic commits. The final source taxonomy and architecture guards pass, as do Web build, full non-PostgreSQL tests, harness/knowledge checks, and all three browser journeys. Architectural review remains the local exit before opening the M6 PR.

## Next

Perform the M6 architectural review. Do not open the M6 PR or start M7 before that review passes.
