# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M2 — migrate `technical_access_evidence` and `network_enforcement_placement` as separate atomic commits in the existing M2 branch.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if the architectural decision rationale is needed: `docs/decisions/ADR-014-target-code-structure-taxonomy.md`.

## Blockers

None.

## Gate

For each context: final `napms.contexts` namespace only, all consumers updated, architecture boundary enforced, targeted tests green. After both contexts: `make test`, harness/knowledge checks and applicable PostgreSQL tests must pass.

Hosted PR gates are deferred until the complete M2 milestone is ready for one final PR.

## Next

Execute `technical_access_evidence`, commit and test it; then execute `network_enforcement_placement` as a second commit. Push and stop for architectural review. Do not start another context or M3.
