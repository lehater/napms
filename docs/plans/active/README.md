# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M3 — move `traffic_analysis` and fully eliminate generic `napms.composition` using explicit ownership.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None. The two non-wiring ACC composition files have explicit target ownership in the active plan.

## Gate

`traffic_analysis` must exist only under `napms.workflows`; generic `napms.composition` must be absent; pure assembly/config must be under `platform/bootstrap`, migration mechanics under `platform/database`, and ACC read/dependency integrations must use peer application contracts rather than peer domain or persistence internals. Full local and configured PostgreSQL checks must pass before final M3 PR review.

Hosted PR gates remain deferred until complete M3 milestone review.

## Next

Execute the final M3 package from the active plan, push, and stop for final architectural review. Do not start M4 or create the PR.
