# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M2 — migrate the final two bounded contexts, `application_catalogue` then `access_policy`, as separate atomic commits.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if the architectural decision rationale is needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None for the final context package. Configured PostgreSQL execution is required after the package before M2 can close.

## Gate

Both contexts must exist only under `napms.contexts`, all adapters must be classified into explicit presentation/infrastructure responsibilities, legacy namespaces must be absent, all consumers and package-data/migration references must use final paths, and targeted/core/harness/knowledge checks must pass.

Hosted PR gates remain deferred until final M2 architectural review and configured PostgreSQL evidence are complete.

## Next

Migrate `application_catalogue`, then `access_policy`, one atomic commit each. Push and stop for final M2 review. Do not start M3 or create the PR.
