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

Outcome: completed through PR #64.

## WP-1 — backend structural migration

Outcome: completed through PR #65 (`a90b866`).

## WP-2 — demonstrated backend granularity

Outcome: completed through PR #66 (`62c77f6`).

## WP-3 — demonstrated Web locality

Completed slices:
- Connectivity Requirements — PR #67 (`e59bb4d`);
- Connectivity Decisions — PR #68 (`a8eb8c0`);
- Access Rules — PR #69 (`e38ffb3`).

Final selected slice: Policy + scoped Connectivity.
- Policy view/query implementation belongs under `features/policy`;
- scoped Connectivity inventory/query implementation belongs under `features/connectivity`;
- shared DTOs (`ProposalScope`, `ProposalInteraction`, `RuleDto`, catalogue/port types), generic transport, auth/session and proposal capability remain shared/application-level;
- proposal operations are intentionally not moved under `features/proposals` because they are also consumed by `features/connectivity`;
- auth/session remains root application orchestration because `App.tsx` owns session bootstrap/logout flow;
- `App.tsx` routing remains legitimate application composition and is not selected by size alone.

## Exit criteria

I32 completes when:
- Policy and scoped Connectivity endpoint implementation is feature-local;
- root `web/src/api.ts` contains no remaining feature-specific endpoint implementation from Requirements, Decisions, Rules, Policy or scoped Connectivity;
- remaining root responsibilities are explicitly shared/application-level;
- locality protection is executable;
- Web, Harness, Core, Docker runtime and browser journey gates are green;
- durable outcomes are absorbed into canonical engineering docs and active execution is cleared.

## Blockers

None known.

## Next

On `i32/web-final-api-locality`, validate Policy + scoped Connectivity extraction and locality guards. If gates are green, absorb I32 completion into canonical engineering docs, clear active execution, rerun the final hosted gate, and squash-integrate the completion PR.
