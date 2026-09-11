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

Current structural evidence:
- `src/napms/runtime/`;
- `src/napms/composition/`;
- `src/napms/application_catalogue/`;
- `tests/architecture/test_dependency_rules.py`;
- `web/src/`.

## WP-0 — structure contract

Responsibility: establish the canonical structural target and bounded migration sequence before production-code moves.

Outcome: completed and integrated through PR #64. The repository now has a canonical context-first / layers-second code-structure contract and an ordered I32 roadmap.

## WP-1 — backend structural migration

Responsibility: execute roadmap stages M1-M4 in one working branch and one Draft PR while retaining stage-local gates and stop conditions.

Execution model:
- one branch / Draft PR accumulates M1-M4;
- each stage ends in a coherent checkpoint commit and the smallest applicable local validation;
- M2 begins only after M1 demonstrates better ownership locality without compensating indirection;
- M3/M4 may be revised from evidence discovered by earlier stages;
- final hosted gates validate the complete accumulated backend diff before squash integration to `main`.

Stage sequence:
1. M1 — move the two I31 target Catalogue HTTP routers into `application_catalogue/adapters/http/` and add executable boundary protection;
2. M2 — classify and relocate remaining Catalogue HTTP to ACC, RC or an explicit composition owner;
3. M3 — decompose `runtime/http_api.py` by semantic owner/read composition until feature endpoint/DTO/mapping code no longer accumulates there;
4. M4 — classify `runtime/composition.py`, `composition/*` and configuration responsibilities and converge on one obvious bootstrap/composition surface without moving accepted cross-context read composition into false ownership.

Non-goals:
- no product/domain semantic change;
- no API contract redesign for folder convenience;
- no new bounded context/service/database;
- no `src/napms/modules/` nesting;
- no arbitrary large-file splitting;
- M5 backend granularity cleanup and M6 Web locality remain separate later work.

Local exits are owned by the roadmap. A stage does not advance while it has an unresolved P0/P1 architecture finding or a failing applicable deterministic gate.

## Exit criteria

WP-1 exits when M1-M4 satisfy their roadmap local exits, the accumulated backend diff preserves current behavior, architecture tests protect migrated ownership boundaries, and applicable final hosted gates pass on the Ready-for-review PR head.

I32 as a whole remains open for separately selected M5/M6 only if evidence after WP-1 shows those stages still provide useful locality improvement.

## Blockers

None known.

## Next

Execute M1 in `i32/backend-structure-refactoring`: move the two target Catalogue HTTP routers without behavior change, update imports/tests, add the smallest architecture guard, then validate the pilot before continuing M2 in the same Draft PR.
