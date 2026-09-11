# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M2 — first bounded-context slice, `network_environment_operations`.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if the architectural decision rationale is needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None.

## Gate

The first M2 slice is complete only when `network_environment_operations` exists solely under `napms.contexts`, all consumers use the final namespace, architecture checks enforce its Domain/Application boundary and legacy-package absence, and required local checks pass.

## Next

Finish, commit and push the `network_environment_operations` slice. Do not select or start the next context without owner direction.
