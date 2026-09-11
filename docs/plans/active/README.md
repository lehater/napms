# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M5 — implementation and architectural review complete; final PostgreSQL evidence before milestone PR.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: `docs/requirements/application-catalogue-target.md`.

## Blockers

None.

## Gate

The accepted M5 scope is only the Application Catalogue capability split into `curation / discovery / target`. Architectural review passed: final root topology is explicit, legacy flat modules are absent, cross-capability direction is enforced, and Resource Catalogue was deliberately left unsplit because current change locality does not justify extra package boundaries. Validation already passed: targeted ACC 151, architecture 67, `make test` 810 with 141 deselected, harness and knowledge checks.

A real PostgreSQL integration run without skips is still required before the final M5 PR. Hosted gates remain deferred until that evidence is green.

## Next

Run `make postgres-test` against configured PostgreSQL. If all integration tests pass without skips, open the final M5 milestone PR and run hosted gates. Do not start M6 before M5 is merged.
