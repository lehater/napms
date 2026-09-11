# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final `contexts / workflows / platform` taxonomy without product/domain semantic change.
Current task: M5 — Application Catalogue capability slice implemented; awaiting architectural review.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

Expand only if needed: `docs/requirements/application-catalogue-target.md`.

## Blockers

None.

## Gate

The ACC application root now contains only `__init__.py`, `ports.py`, and `curation / discovery / target`; mapped flat modules are absent; all consumers use final imports; unit tests with unambiguous ownership follow the capability taxonomy. Architecture guards enforce root topology, flat-module removal, and the accepted cross-capability dependency direction. Validation: targeted Application Catalogue 151 passed; architecture 67 passed; `make test` 810 passed, 141 deselected; harness and knowledge checks passed.

Hosted PR gates remain deferred until the complete M5 milestone review.

## Next

Perform architectural review of the Application Catalogue capability slice. Do not start Resource Catalogue, M6, or create a PR before that review.
