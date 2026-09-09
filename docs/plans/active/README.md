# Active execution

Current: `PLAN-033-i19-network-enforcement-placement.md`
Goal: Complete I19 Network Enforcement Placement without pulling I20 reconciliation or vendor/device mechanics forward.
Current task: WP-4 — architecture review, hosted PR gate, canonical absorption and roadmap promotion.

Working mode: review/closure; primary Skill `architecture-review`.

## Working set

Read first:
- `docs/plans/active/PLAN-033-i19-network-enforcement-placement.md`
- `docs/architecture/network-enforcement-placement-boundary.md`
- `src/napms/network_enforcement_placement/domain/model.py`
- `src/napms/network_enforcement_placement/domain/selection.py`

Expand only if needed:
- `tests/network_enforcement_placement/`
- `tests/integration/postgres/test_network_enforcement_placement*.py`
- `tests/architecture/test_network_enforcement_placement_boundary.py`
- `docs/engineering/post-wave1-product-completion-roadmap.md`
- `docs/engineering/current-state.md`

Recovery facts:
- WP-0 accepted exact endpoint-pair first-slice semantics and explicit Unknown for unsupported/missing forwarding truth.
- WP-1 core is implemented; NoForwardingPath is a temporal/provenance-bearing fact.
- WP-2 uses immutable relation-scoped captures in NEP-owned PostgreSQL; zero/overlapping effective captures fail closed instead of latest-wins.
- WP-3 adds operation-scoped composition plus domain-attributable provenance, temporal-switch and no-peer-side-effect proofs.
- Draft PR #43 is the current integration vehicle; full hosted gates have not run yet.

## Blockers

I19 cannot be marked complete or I20 promoted until final hosted gates are green and P0/P1 review findings are closed.

## Gate

WP-4 passes when architecture review has no open P0/P1, PR #43 is Ready and required Actions are green, then canonical roadmap/current-state truth is updated and the plan is absorbed.

## Next

Review the full I19 diff for P0/P1, fix findings, mark PR #43 Ready, inspect hosted Actions, then absorb/promote only on green evidence.
