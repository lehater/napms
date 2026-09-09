# Active execution

Current: `PLAN-033-i19-network-enforcement-placement.md`
Goal: Complete I19 Network Enforcement Placement without pulling I20 reconciliation or vendor/device mechanics forward.
Current task: WP-4 — hosted gate, canonical absorption and roadmap promotion.

Working mode: review/closure; primary Skill `architecture-review`.

## Working set

Read first:
- `docs/plans/active/PLAN-033-i19-network-enforcement-placement.md`
- `docs/architecture/network-enforcement-placement-boundary.md`

Expand only if needed:
- `src/napms/network_enforcement_placement/domain/model.py`
- `src/napms/network_enforcement_placement/domain/selection.py`
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
- PR #43 is Ready. Knowledge gate is green; harness first attempt failed only because this capsule exceeded its Read-first context budget and is being corrected.

## Blockers

I19 cannot be marked complete or I20 promoted until final hosted gates are green.

## Gate

WP-4 passes when required Actions are green, then canonical roadmap/current-state truth is updated and the plan is absorbed.

## Next

Re-run/observe hosted Actions after the capsule fix. On green evidence, absorb I19 into canonical state, promote I20 and squash-merge PR #43.
