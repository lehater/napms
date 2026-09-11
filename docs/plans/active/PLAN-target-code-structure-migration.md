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

Scope was mechanical only:

```text
pyproject.toml -> backend/pyproject.toml
Dockerfile     -> backend/Dockerfile
src/           -> backend/src/
tests/         -> backend/tests/
```

M1 passed local and hosted gates and was squash-merged before M2 started.

## M2 — Bounded contexts

Status: `active` on branch `refactor/m2-network-environment-operations`.

M2 is integrated as one milestone PR, not one PR per context. Contexts are migrated incrementally in the same branch.

Execution policy:
- one bounded context = one atomic commit;
- never mix two context moves in one commit;
- after every context run targeted unit + architecture tests;
- run `make test` after each work package of at most 2–3 contexts and before final M2 review;
- run affected PostgreSQL/integration tests for persistence-bearing contexts and full `make postgres-test` before final M2 review;
- no hosted PR gates per context; run hosted gates once on the final M2 PR;
- after each work package, stop for architectural review before selecting the next package;
- no M3 workflow/composition ownership moves while M2 is active.

For each context:
- move it directly to `backend/src/napms/contexts/<context>/`;
- normalize outer layers to `domain / application / infrastructure / presentation` only where responsibility exists;
- update all consumers and tests;
- remove the legacy top-level implementation package;
- add architecture guards for the final namespace and dependency direction;
- preserve product/domain behavior.

### Completed M2 slices

1. `network_environment_operations` — complete in `8dac6ff40fc82732b14ec7aeca80dabc84af062a`.
   - final namespace under `napms.contexts`;
   - no compatibility facade;
   - composition stub intentionally remains for M3;
   - local core, architecture, harness, knowledge and PostgreSQL checks pass.
2. `technical_access_evidence` — complete in `3dd64d4` on the M2 milestone branch.
   - final namespace and Clean layers under `napms.contexts`;
   - all consumers and migration resource paths updated;
   - legacy package removed and architecture guards added.
3. `network_enforcement_placement` — complete in the current M2 work package.
   - final namespace and Clean layers under `napms.contexts`;
   - all consumers and migration resource paths updated;
   - legacy package removed and architecture guards added.

### Completed M2 work package

Migrated as two separate commits and in this order:

1. `technical_access_evidence`
2. `network_enforcement_placement`

No third context was selected. Existing `composition/*_postgres.py` wiring remains under `composition/` until M3; only imports required by the context moves changed.

## Exit criteria

M2 closes only when all accepted bounded contexts are under `napms.contexts`, legacy top-level context packages are absent, architecture guards enforce the new boundaries, full local checks pass, and one final M2 PR passes the required hosted gates.

## Blockers

Local PostgreSQL execution evidence is unavailable: `make postgres-test` completed successfully but skipped all 141 tests because the PostgreSQL test environment was not configured.

## Next

Review the completed two-context work package. Do not select another context or start M3 before that review.
