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

Status: `active` on branch `refactor/m3-workflows-composition`.

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

Validation after the first package:
- targeted + architecture: 95 / 158 / 70 / 63 passed respectively;
- `make test`: 801 passed, 141 deselected;
- `make harness-check`: passed;
- `make knowledge-check`: passed.

### Final M3 work package

Move `traffic_analysis` to `napms.workflows.traffic_analysis` and fully drain `napms.composition`.

Ownership decisions:
- workflow application -> `workflows/traffic_analysis/application/`;
- workflow HTTP -> `workflows/traffic_analysis/presentation/http/`;
- workflow-owned outbound adapters -> `workflows/traffic_analysis/infrastructure/`;
- pure executable `open_*_scope` and service assembly -> `platform/bootstrap/`;
- runtime configuration currently in `composition/config.py` -> `platform/bootstrap/config.py`;
- PostgreSQL migration runner -> `platform/database/migrations.py`;
- `application_catalogue_target_dependencies.py` is ACC-owned integration logic, not platform wiring: move it under `contexts/application_catalogue/infrastructure/integrations/` and replace direct peer domain/infrastructure dependencies with explicit peer application contracts;
- `application_catalogue_target_read_postgres.py` is an ACC-owned read model: move it under `contexts/application_catalogue/infrastructure/read_models/postgres/`; remove its direct Resource Catalogue schema join by using an explicit Resource Catalogue application contract for resource display/scope filtering and paging;
- do not create a sixth workflow merely to hide these ACC concerns;
- no context may import another context's domain; cross-context use must go through application contracts/ports;
- platform bootstrap owns wiring only, not feature mapping/query behavior.

Expected pure wiring moves from `composition/`:
- `access_policy_realization_postgres.py` -> `platform/bootstrap/access_policy_realization.py`;
- `catalogue_curation_postgres.py` -> `platform/bootstrap/catalogue_curation.py`;
- `catalogue_target_postgres.py` -> `platform/bootstrap/application_catalogue_target.py`;
- `greenfield_postgres.py` -> `platform/bootstrap/greenfield.py`;
- `network_enforcement_placement_postgres.py` -> `platform/bootstrap/network_enforcement_placement.py`;
- `network_environment_operations_stub.py` -> `platform/bootstrap/network_environment_operations.py`;
- `network_operator_view_postgres.py` -> `platform/bootstrap/network_operator_view.py`;
- `technical_access_evidence_postgres.py` -> `platform/bootstrap/technical_access_evidence.py`;
- `traffic_analysis_postgres.py` -> `platform/bootstrap/traffic_analysis.py`.

The final package must delete `backend/src/napms/composition/` and the legacy top-level `traffic_analysis/` package.

## Exit criteria

M3 closes when all five workflows are under `napms.workflows`, legacy top-level workflow packages are absent, generic `napms.composition` is deleted, ACC cross-context read/dependency integrations use application contracts rather than peer domain/persistence internals, workflow application layers do not depend on outer layers, architecture tests prohibit workflow persistence bypass, full local/PostgreSQL checks pass, and one final M3 PR passes required hosted gates.

## Blockers

None. The ownership conflict exposed by the old ACC composition files is resolved by the decisions above.

## Next

Execute the final M3 work package only. Run targeted/architecture checks during the package, then full core/harness/knowledge and configured PostgreSQL checks. Push and stop for final M3 architectural review. Do not start M4 or create the PR before that review.
