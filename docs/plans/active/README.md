# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M5 — split Application Catalogue application layer into `curation / discovery / target` capabilities.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: `docs/requirements/application-catalogue-target.md`.

## Blockers

None.

## Gate

The ACC slice must be structural only: mapped flat application modules move under `curation`, `discovery`, or `target`; root `application/ports.py` remains the shared context-wide contract surface; old flat mapped modules disappear; no compatibility facades remain. `target` may depend on root ports/domain but not `curation` or `discovery`; `curation` and `discovery` must not import `target`. All consumers/tests use final imports and architecture tests enforce these boundaries.

Hosted PR gates remain deferred until the complete M5 milestone review.

## Next

Execute only the Application Catalogue capability slice as one atomic commit, run targeted/architecture plus full core/harness/knowledge checks, push, and stop for architectural review. Do not start Resource Catalogue, M6, or create a PR.
