# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M2 — migrate only `access_policy_realization` as one atomic context commit on the milestone branch.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if the architectural decision rationale is needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None for the current slice. Configured PostgreSQL execution remains required before final M2 closure.

## Gate

`access_policy_realization` must exist only under `napms.contexts`, all adapters must be classified into explicit infrastructure responsibilities, all consumers must use the final namespace, architecture tests must enforce the boundary, and targeted/core/harness/knowledge checks must pass.

Hosted PR gates remain deferred until the complete M2 milestone is ready for one final PR.

## Next

Migrate only `access_policy_realization`, push the branch, and stop for architectural review. Do not start `application_catalogue`, `access_policy`, or M3.
