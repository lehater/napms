# I32 Code Structure Refactoring

Status: `active`

Date: 2026-09-11.

## Goal

Align physical code ownership with the accepted context-first Clean/Hexagonal architecture so humans and agents can locate changes from their semantic owner, without changing product/domain semantics.

## Inputs

Canonical architecture and execution inputs:
- `docs/architecture/current-architecture.md`;
- `docs/architecture/code-structure.md`;
- `docs/engineering/current-state.md`;
- `docs/engineering/code-structure-refactoring-roadmap.md`;
- `AGENTS.md`, `src/AGENTS.md`, `web/AGENTS.md`;
- `docs/process/working-loop.md`.

## WP-0 — structure contract

Outcome: completed and integrated through PR #64. The repository has a canonical context-first / layers-second code-structure contract and ordered I32 roadmap.

## WP-1 — backend structural migration

Outcome: completed and squash-integrated through PR #65 (`a90b866`). M1-M4 moved feature HTTP beside semantic owners, reduced active runtime HTTP to process assembly, and established `napms.bootstrap` as the executable composition root. Final Core, Harness, PostgreSQL, Docker runtime and browser journey gates were green.

## WP-2 — demonstrated backend granularity

Responsibility: execute M5 only where post-WP-1 evidence shows unrelated use cases still share an editing/search context.

Selected pilot:
- `src/napms/application_catalogue/application/structure_curation.py` mixes Application mutation/lifecycle use cases with Component mutation/lifecycle use cases, including commands/results and idempotency replay;
- split those responsibilities into Application-specific and Component-specific modules;
- retain only genuinely shared mutation plumbing in a small application-local module;
- preserve domain, API, persistence, authority, concurrency and idempotency semantics.

Stop condition: do not split other large files merely by size. Continue M5 only when a candidate has equivalent change-coupling evidence and the pilot demonstrably improves locality without compensating indirection.

M6 Web locality remains separate and is not part of WP-2.

## Exit criteria

WP-2 exits when the selected pilot has owner-specific use-case modules, imports/tests/composition follow those owners, behavior is unchanged, and applicable Core/PostgreSQL/Harness gates pass. Remaining backend large files must be either locally coherent or separately justified before further M5 work.

I32 remains open for separately selected M6 only if post-WP-2 evidence shows useful Web locality improvement.

## Blockers

None known.

## Next

On `i32/backend-granularity`, split `structure_curation.py` by Application vs Component mutation responsibility, update only required imports/tests/composition, validate the smallest applicable deterministic gates, and stop before any second hotspot until this pilot is evaluated.
