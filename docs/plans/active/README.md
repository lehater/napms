# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M2 — migrate `authority_management` and `resource_catalogue` as two atomic context commits on the milestone branch.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if the architectural decision rationale is needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None for the current work package. A configured PostgreSQL run is still required before the final M2 PR can close the milestone.

## Gate

Each context must exist only under `napms.contexts`, all consumers and migration/package-data references must use the final namespace, architecture tests must enforce the boundary, and targeted tests must pass. Run `make test`, harness and knowledge checks after the two-context package.

Hosted PR gates remain deferred until the complete M2 milestone is ready for one final PR.

## Next

Migrate `authority_management` first, then `resource_catalogue`, one atomic commit per context. Stop after the two-context package for architectural review; do not start M3.
