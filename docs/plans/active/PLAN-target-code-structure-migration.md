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

M2 is integrated as one milestone PR. Contexts are migrated incrementally in the same branch.

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

1. `network_environment_operations` — `8dac6ff40fc82732b14ec7aeca80dabc84af062a`.
2. `technical_access_evidence` — `3dd64d4167838bcd3f90933f6aef54940f6ef88b`.
3. `network_enforcement_placement` — `a17ba404496932d70ee21ccb3ff7806ca52e7344`.
4. `connectivity_requirements` — `a8842d21eeaa7da22993d9af7ae2dd71a16de82d`.
5. `connectivity_decision` — `7c75e448c755a37774dd7bbd4d5ff09708559eac`.

All five use the final `napms.contexts` namespace; legacy implementation packages are removed. Existing `composition/*` wiring remains transitional until M3 and only import/path references are updated during M2.

### Current M2 work package

Migrate as two separate commits and in this order:

1. `authority_management`
2. `resource_catalogue`

For both contexts:
- preserve existing domain/application semantics;
- HTTP inbound code moves under `presentation/http/`;
- owner PostgreSQL persistence moves under `infrastructure/persistence/postgres/`;
- adapters serving other contexts/workflows move under `infrastructure/integrations/`;
- owner-local support code that is not HTTP/persistence/integration should live under a capability-named `infrastructure/` package rather than a generic adapter bucket;
- do not move workflow ownership or generic `composition` files yet; M3 owns that cleanup;
- update package-data/migration references and all repository consumers;
- remove legacy namespaces and add architecture guards.

Run targeted tests after each context. After both commits run `make test`, `make harness-check`, and `make knowledge-check`. Run PostgreSQL tests only if a configured environment is available; absence of local PostgreSQL is not a blocker for continuing M2, but configured PostgreSQL evidence is mandatory before final M2 closure.

## Exit criteria

M2 closes only when all accepted bounded contexts are under `napms.contexts`, legacy top-level context packages are absent, architecture guards enforce the new boundaries, full local checks pass, PostgreSQL integration evidence is exercised in a configured environment, and one final M2 PR passes the required hosted gates.

## Blockers

None for the current work package. Configured PostgreSQL execution remains a deferred milestone-exit requirement.

## Next

Complete `authority_management` and `resource_catalogue` as separate atomic commits, push the milestone branch, and stop for architectural review. Do not start another context or M3 before that review.
