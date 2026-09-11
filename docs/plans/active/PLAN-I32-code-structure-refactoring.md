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

Outcome: completed and squash-integrated through PR #65 (`a90b866`). M1-M4 aligned feature HTTP ownership and established `napms.bootstrap` as the executable composition root.

## WP-2 — demonstrated backend granularity

Outcome: completed and squash-integrated through PR #66 (`62c77f6`). The mixed Application/Component structure mutation hotspot was split by owner; no second M5 split was justified by evidence.

## WP-3 — demonstrated Web locality

Responsibility: execute M6 only where a concrete feature still depends on root/shared files because feature-specific responsibility is misplaced.

Selected pilot: Connectivity Requirements API ownership.
- `web/src/api.ts` currently owns Requirement DTOs, commands, queries and Requirement↔Policy alignment operations together with unrelated Decisions, Rules, Policy and Connectivity APIs;
- `web/src/features/requirements/` has pages but no feature-local API/model boundary;
- moving Requirement-specific API implementation beside the feature means future Requirement API changes no longer require editing root `api.ts`;
- generic HTTP error/request behavior and genuinely cross-feature interaction DTOs may remain shared;
- compatibility exports are allowed when they avoid unrelated churn, provided Requirement implementation itself is feature-local.

`App.tsx` routing is not selected merely because it is large: process-level route composition is a legitimate root responsibility unless a concrete feature-routing concern proves otherwise.

## Exit criteria

WP-3 exits when Requirement-specific DTO/query/command/alignment implementation is owned under `features/requirements`, root `api.ts` contains no Requirement implementation, behavior is unchanged, feature/root boundaries are executable where useful, and Web plus relevant browser journeys are green.

I32 completes after WP-3 if no further Web hotspot has equivalent misplaced-responsibility evidence.

## Blockers

None known.

## Next

On `i32/web-requirements-api-locality`, move Requirement-specific API implementation from root `web/src/api.ts` into `web/src/features/requirements/`, retain only shared transport/types at shared scope, add the smallest locality guard, and validate Web/browser gates before considering any other Web hotspot.
