# PLAN — Target Code Structure Migration

Status: `active`

## Goal

Move NAPMS to the accepted final physical taxonomy without product/domain semantic change:

```text
backend/src/napms/
  contexts/
  workflows/
  platform/
```

## Inputs

- `docs/architecture/code-structure.md`
- `docs/engineering/target-code-structure-migration-roadmap.md`
- `docs/decisions/ADR-014-target-code-structure-taxonomy.md`

## Execution order

```text
M1 backend repository boundary
-> M2 bounded contexts + final Clean layers
-> M3 workflows + remove generic composition
-> M4 platform consolidation
-> M5 capability-oriented internals where justified
-> M6 Web final locality
-> M7 compatibility purge + final enforcement
```

The long-range roadmap owns detailed stage rules. The active capsule selects the current task.

## M1 — Repository backend boundary

Status: `complete` in `f0e281e`.

Scope is mechanical only:

```text
pyproject.toml -> backend/pyproject.toml
Dockerfile     -> backend/Dockerfile
src/           -> backend/src/
tests/         -> backend/tests/
```

Update in the same stage:
- root Makefile commands while keeping Makefile as the stable repository entry point;
- Compose/backend build paths;
- `.github/workflows/` backend path filters and commands;
- repository tooling/config that references `src/`, `tests/`, `pyproject.toml` or backend Dockerfile;
- AGENTS/Skills path guidance only where paths become stale.

Do not in M1:
- move semantic modules under `contexts/` yet;
- rename `adapters`;
- change application/domain semantics;
- refactor implementation while moving files.

Procedure:
1. Inventory exact repository references to the four moved backend paths.
2. Move backend files/directories mechanically.
3. Repair root Makefile/tool/Compose/CI references.
4. Run/import-check the same backend test commands from the new location.
5. Update architecture tests only for repository path changes, not future M2 rules.
6. Validate applicable local checks and final hosted PR gates.
7. Update the active capsule: mark M1 complete and select the first M2 context slice.

## Exit criteria

M1 is complete only when:
- backend imports resolve from `backend/src`;
- product/core tests pass;
- harness and knowledge checks pass;
- Docker/integration checks affected by build-path changes pass;
- hosted final PR gates for affected paths pass;
- no product/domain behavior changed.

After M1, inspect actual dependency/import fan-out and select the least-coupled bounded context for the first M2 slice. Do not preselect from intuition.

## M2 — First bounded-context slice

Move only `network_environment_operations` to
`backend/src/napms/contexts/network_environment_operations/` with its final
Domain/Application/Infrastructure layers. Preserve behavior, update all consumers and
tests, prohibit the legacy package, and leave the composition stub in place until M3.

Do not select or start another context in this slice.

## Blockers

None.

## Next

Complete, commit and push the first M2 `network_environment_operations` slice. Await
owner direction before selecting the next context.
