# Active execution

Current: `PLAN-033-i19-network-enforcement-placement.md`
Goal: Complete I19 Network Enforcement Placement without pulling I20 reconciliation or vendor/device mechanics forward.
Current task: WP-1 — implement framework-free NEP Domain/Application/Ports and executable core semantics.

Working mode: implementation slice; primary Skill `implement-slice`.

## Working set

Read first:
- `docs/plans/active/PLAN-033-i19-network-enforcement-placement.md`
- `docs/domain/network-enforcement-placement/tactical-model.md`
- `docs/architecture/network-enforcement-placement-boundary.md`

Expand only if needed:
- `docs/requirements/network-enforcement-placement-core.md`
- `src/AGENTS.md`
- `tests/architecture/test_dependency_rules.py`
- `src/napms/access_policy_realization/`
- `src/napms/technical_access_evidence/`

Recovery facts:
- WP-0 is accepted: exact endpoint-pair first slice, zero/one complete path, unsupported multipath/discriminators -> Unknown.
- Logical Firewall identity is independent from provider realization; attachments require matching effective correspondence.
- Selection states are `Placed | NoEnforcement | NoForwardingPath | Ambiguous | Unknown`.
- I20 reconciliation/policy derivation and vendor/provider execution remain out of scope.

## Blockers

None for WP-1.

## Gate

WP-1 passes when Domain/Application/Ports implement the accepted selection semantics with deterministic fail-closed tests and no peer/infrastructure dependency.

## Next

Implement NEP core + architecture tests, then advance to WP-2 durable PostgreSQL/import proof only after the core gate is coherent.
