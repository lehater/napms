# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M4 — consolidate legacy bootstrap/runtime under `napms.platform`.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None.

## Gate

M3 is complete in PR #75 / `18787e3f`; all required hosted gates passed. M4 must remove top-level `napms.bootstrap` and `napms.runtime`, keep core independent from platform, and preserve all runtime/entrypoint behavior.

## Next

Execute the M4 platform consolidation work package, run local/full/PostgreSQL checks, push, and stop for architectural review. Do not start M5 or create a PR before that review.
