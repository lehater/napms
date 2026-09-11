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

M3 is one milestone PR. Each workflow move is an atomic commit; generic `composition/` is drained only after ownership is explicitly classified. Hosted gates run once on the final M3 PR.

Accepted workflows:

1. `requirement_policy_alignment`
2. `policy_export`
3. `scoped_connectivity_inventory`
4. `network_operator_view`
5. `traffic_analysis`

Rules:
- workflow application orchestration -> `workflows/<workflow>/application/`;
- inbound HTTP -> `workflows/<workflow>/presentation/http/`;
- workflow-owned outbound/cross-context adapters -> `workflows/<workflow>/infrastructure/`;
- pure executable dependency assembly is not workflow infrastructure; it moves from generic `composition/` to `platform/bootstrap/`;
- process-level migration mechanics move to `platform/database/`;
- context-owned integrations/read models move to the owning context infrastructure only when the ownership is explicit;
- no generic `composition/` remains at M3 exit;
- do not redesign product/domain semantics.

### Current M3 work package

Move four structurally simple workflows as four atomic commits:

1. `requirement_policy_alignment`
2. `policy_export`
3. `scoped_connectivity_inventory`
4. `network_operator_view`

For this package only repair imports in existing `composition/` wiring as needed. Do not yet drain or relocate `composition/`; do not move `traffic_analysis`.

Target shapes:

```text
workflows/requirement_policy_alignment/
  application/
  presentation/http/

workflows/policy_export/
  application/
  presentation/http/

workflows/scoped_connectivity_inventory/
  application/
  presentation/http/

workflows/network_operator_view/
  application/
  presentation/http/
```

`network_operator_view/application.py` becomes an application package module without semantic change.

## Exit criteria

M3 closes when all five accepted workflows are under `napms.workflows`, legacy top-level workflow packages are absent, generic `napms.composition` is deleted, wiring/query ownership is explicit, architecture guards prohibit workflow persistence bypass, full local/integration checks pass, and one final M3 PR passes required hosted gates.

## Blockers

None.

## Next

Complete the four-workflow package above as four atomic commits, run targeted/architecture tests after each workflow and full core/harness/knowledge checks after the package, push, and stop for architectural review. Do not start `traffic_analysis`, drain `composition/`, or start M4 before that review.
