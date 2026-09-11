# Active execution

Current: `PLAN-target-code-structure-migration.md`
Goal: migrate NAPMS to the accepted final backend and Web taxonomy without product/domain semantic change.
Current task: M6 architectural review complete; final hosted PR gates pending.

## Working set

Read first:
- `docs/plans/active/PLAN-target-code-structure-migration.md`
- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`

## Blockers

None.

## Gate

M6 implementation and architectural review are complete. Final Web taxonomy is `app / features / components/ui / lib`; the legacy root API/application files and feature-specific root components are absent. Architecture guards pass. Validation: `make web-check` passed; architecture 72 passed; `make test` 815 passed with 141 deselected; harness and knowledge checks passed; local Docker browser journeys 3 passed. The J03 change only synchronizes with the existing debounce search request and preserves all journey assertions.

## Next

Open the final M6 milestone PR, mark it ready once, run required hosted gates, and squash-merge if green. Do not start M7 before M6 is merged.
