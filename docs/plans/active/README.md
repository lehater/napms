# Active execution

Current: `I32 M0 — Code Structure Refactoring / structure contract`.

Detailed plan: `docs/plans/active/PLAN-I32-code-structure-refactoring.md`.
Roadmap: `docs/engineering/code-structure-refactoring-roadmap.md`.
Architecture contract: `docs/architecture/code-structure.md`.

## Current task

Establish the canonical code-structure target and staged migration sequence before any production-code relocation.

## Working set

- `docs/architecture/code-structure.md`;
- `docs/engineering/code-structure-refactoring-roadmap.md`;
- `docs/plans/active/PLAN-I32-code-structure-refactoring.md`;
- architecture/plans navigation;
- Harness/process rules only if a concrete inconsistency requires correction.

Current runtime truth remains `docs/engineering/current-state.md`.

## Blockers

None known.

## Gate

M0 is documentation/Harness-state only. Require architecture/roadmap/plan consistency plus green `make harness-check` and `make knowledge-check` (or inspected equivalent hosted evidence if local execution is unavailable).

## Next

Finish M0 navigation and self-review, validate the applicable gates, then integrate M0 through one squash PR. After integration select M1: move the two I31 target Catalogue HTTP routers into `application_catalogue/adapters/http/` without behavior change and add an executable architecture guard.
