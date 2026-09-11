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

Outcome: completed and integrated through PR #64.

## WP-1 — backend structural migration

Outcome: completed through PR #65 (`a90b866`). M1-M4 aligned feature HTTP ownership and established `napms.bootstrap` as the executable composition root.

## WP-2 — demonstrated backend granularity

Outcome: completed through PR #66 (`62c77f6`). The mixed Application/Component structure mutation hotspot was split by owner; no second backend split was justified by evidence.

## WP-3 — demonstrated Web locality

M6 is executed incrementally only where root/shared files still own feature-specific API responsibility.

Completed slice: Connectivity Requirements, PR #67 (`e59bb4d`). Requirement DTO/query/command/alignment implementation is now under `features/requirements`; shared request/error handling lives in `lib/api.ts`; root `api.ts` retains compatibility exports only for that slice. Core, Web, Harness, Docker and browser gates were green.

Current slice: Connectivity Decisions.
- Decision DTOs, queries and commands still live in root `web/src/api.ts`;
- both pages under `web/src/features/decisions/` consume those operations;
- move Decision-specific implementation beside the feature using the proven shared-transport + compatibility-export pattern;
- preserve API/UX behavior and avoid page rewrites unrelated to ownership.

Equivalent remaining root API slices (Rules, Policy, scoped Connectivity, Proposals/Auth) are not part of this increment and must be evaluated separately after Decisions.

`App.tsx` routing remains a legitimate application-composition responsibility and is not selected by size alone.

## Exit criteria

The current slice exits when Decision-specific DTO/query/command implementation is feature-local, root `api.ts` contains compatibility exports but no Decision implementation, locality protection is executable, and applicable Web/Harness/Core/browser/runtime gates are green.

I32 completes only when remaining root API responsibilities are either feature-local or explicitly justified as genuinely shared/application-level.

## Blockers

None known.

## Next

On `i32/web-decisions-api-locality`, move Decision-specific API implementation into `web/src/features/decisions/api.ts`, extend the Web locality guard, validate the final gates, then evaluate the next remaining root API slice.
