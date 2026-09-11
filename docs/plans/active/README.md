# Active execution

Current: `PLAN-I32-code-structure-refactoring.md`
Goal: align physical code ownership with the accepted context-first Clean/Hexagonal architecture without changing product/domain semantics.
Current task: WP-0 — establish the code-structure contract, roadmap and durable Harness recovery state.

## Working set

Read first:
- `docs/architecture/code-structure.md`
- `docs/engineering/code-structure-refactoring-roadmap.md`
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`
- `docs/engineering/current-state.md`

Expand to current `runtime/`, `composition/` or architecture-test code only when validating a concrete structural claim. Do not begin production-code relocation during WP-0.

## Blockers

None known.

## Gate

WP-0 is documentation/Harness-state only. Require architecture/roadmap/plan consistency plus green `make harness-check` and `make knowledge-check`, or inspected equivalent hosted evidence if local execution is unavailable.

## Next

Finish WP-0 self-review and validation, then integrate it through one squash PR. After integration select M1: move the two I31 target Catalogue HTTP routers into `application_catalogue/adapters/http/` without behavior change and add an executable architecture guard.
