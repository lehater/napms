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

## Completed milestones

- M1 — complete in `f0e281e`.
- M2 — complete in PR #74, squash merge `91eb009c2338697458ba3874836c93cc044f753a`; all six hosted gates passed.

## M3 — Workflows and generic composition removal

Status: `implementation and architectural review complete; final hosted PR gates pending` on branch `refactor/m3-workflows-composition`.

M3 is one milestone PR. Hosted gates run once on the complete milestone.

Accepted workflows:

1. `requirement_policy_alignment`
2. `policy_export`
3. `scoped_connectivity_inventory`
4. `network_operator_view`
5. `traffic_analysis`

Completed workflow moves:

1. `requirement_policy_alignment` — `6ea79e634a6cb03b5f2657051c9619d7834df03`
2. `policy_export` — `53177891fb94f7e93c372ae3b73110bea15b44d8`
3. `scoped_connectivity_inventory` — `5f44a077c56170c813f8300e267fa2aed3bea896`
4. `network_operator_view` — `75a7fb2934f411a20ecd4e637661b917ed2894e6`
5. `traffic_analysis` — `e17eb0b`

Composition ownership resolution:
- `application_catalogue_target_dependencies.py` moved to ACC-owned `infrastructure/integrations` and now consumes peer application contracts;
- `application_catalogue_target_read_postgres.py` moved to ACC-owned `infrastructure/read_models/postgres`;
- Resource Catalogue enrichment/filtering/paging now goes through a Resource Catalogue application contract and owner-local PostgreSQL implementation; ACC no longer reads `napms_resource_catalogue` SQL directly;
- pure executable assembly/config moved to `platform/bootstrap`;
- migration runner moved to `platform/database`;
- generic `napms.composition` is deleted.

Validation evidence before final PR:
- targeted workflow/architecture/bootstrap checks passed;
- `make test`: 806 passed;
- `make harness-check`: passed;
- `make knowledge-check`: passed;
- PostgreSQL 16 `make postgres-test`: 141 passed.

Final architectural review confirms:
- all five workflows exist only under `napms.workflows`;
- workflow application layers do not import infrastructure/presentation;
- workflows do not import context persistence internals;
- ACC target integrations use peer application contracts rather than peer domain/infrastructure;
- ACC target read-model contains no Resource Catalogue schema SQL;
- generic `napms.composition` is absent;
- platform additions in M3 are wiring/config/database mechanics only; top-level `bootstrap/` and `runtime/` remain intentionally transitional until M4.

## Exit criteria

M3 closes when the final milestone PR passes all required hosted gates and is squash-merged to `main`.

## Blockers

None.

## Next

Open the final M3 milestone PR, run required hosted gates, and squash-merge if green. Do not start M4 or make material changes after the final gate without returning the PR to draft and gating again.
