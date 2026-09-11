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

M1 moved the backend workspace under `backend/`, preserved behavior, and passed local and hosted gates before M2 started.

## M2 — Bounded contexts

Status: `active` on branch `refactor/m2-network-environment-operations`.

M2 is integrated as one milestone PR, not one PR per context. Contexts are migrated incrementally in the same branch.

Execution policy:
- one bounded context = one atomic commit;
- never mix two context moves in one commit;
- after every context run targeted unit + architecture tests;
- run `make test` after each work package of at most 2–3 contexts and before final M2 review;
- run affected PostgreSQL/integration tests for persistence-bearing contexts and full `make postgres-test` in a configured environment before final M2 review;
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
2. `technical_access_evidence` — complete in `3dd64d4167838bcd3f90933f6aef54940f6ef88b`.
3. `network_enforcement_placement` — complete in `a17ba404496932d70ee21ccb3ff7806ca52e7344`.

All three use the final `napms.contexts` namespace; legacy implementation packages are removed. Existing `composition/*` wiring remains transitional until M3 and only import/path references are updated during M2.

### Current M2 work package

Migrate as two separate commits and in this order:

1. `connectivity_requirements`
2. `connectivity_decision`

For both contexts:
- keep existing domain/application semantics;
- HTTP inbound code moves under `presentation/http/`;
- owner persistence moves under `infrastructure/persistence/postgres/`;
- other current adapters move under capability-named `infrastructure/integrations/` when they are outbound/cross-context integrations;
- do not move workflow ownership or generic `composition` files yet; M3 owns that cleanup;
- update package-data/migration package references and all repository consumers;
- remove legacy namespaces and add architecture guards.

Run targeted tests after each context. After both commits run `make test`, `make harness-check`, and `make knowledge-check`. Run PostgreSQL tests if a configured environment is available; absence of local PostgreSQL is not a blocker for continuing M2, but a configured PostgreSQL run is mandatory before final M2 closure.

## Exit criteria

M2 closes only when all accepted bounded contexts are under `napms.contexts`, legacy top-level context packages are absent, architecture guards enforce the new boundaries, full local checks pass, PostgreSQL integration evidence is exercised in a configured environment, and one final M2 PR passes the required hosted gates.

## Blockers

None for the current two-context package. Configured PostgreSQL execution remains a deferred milestone-exit requirement.

## Next

Complete `connectivity_requirements` and `connectivity_decision` as separate atomic commits, push the milestone branch, and stop for architectural review. Do not start another context or M3 before that review.
