# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M3 — move the first four simple workflows under `napms.workflows` as atomic commits.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None.

## Gate

Each moved workflow must exist only under `napms.workflows`; HTTP must be under `presentation/http`; application orchestration stays under `application`; all consumers and tests must use final imports; architecture tests must protect the new workflow namespace. Existing `composition/` may receive import-only repairs in this package but is not relocated yet.

Hosted PR gates remain deferred until complete M3 milestone review.

## Next

Move `requirement_policy_alignment`, `policy_export`, `scoped_connectivity_inventory`, then `network_operator_view`, one atomic commit each. Run package checks, push, and stop for architectural review. Do not start `traffic_analysis`, composition drain, or M4.
