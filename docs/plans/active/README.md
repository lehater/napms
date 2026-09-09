# Active execution

Current: `PLAN-033-i19-network-enforcement-placement.md`
Goal: Complete I19 Network Enforcement Placement without pulling I20 reconciliation or vendor/device mechanics forward.
Current task: WP-0 — close Tactical DDD, requirements and architecture semantics for path knowledge, Logical Firewall correspondence, Enforcement Attachment and Enforcement Selection.

Working mode: domain re-entry; primary Skill `domain-model-change`.

## Working set

Read first:
- `docs/plans/active/PLAN-033-i19-network-enforcement-placement.md`
- `docs/engineering/post-wave1-product-completion-roadmap.md`
- `docs/domain/resource-role-model.md`

Expand only if needed:
- `docs/domain/semantic-ownership.md`
- `docs/domain/ubiquitous-language.md`
- `docs/domain/strategic-model.md`
- `docs/architecture/current-architecture.md`
- `docs/process/decision-protocol.md`

Recovery facts:
- I18 is complete in `main`; I19 is the selected next increment.
- NEP owns path/forwarding meaning and placement; it does not own authorization, configured evidence or I20 reconciliation.
- Logical Firewall, provider/device realization, Resource and Enforcement Attachment are distinct identities.
- current `docs/architecture/current-architecture.md` has a stale status line referring to I18 as next; repair it during WP-0 propagation.

## Blockers

Implementation gate is closed until WP-0 accepts exact selection/unknown/temporal/correspondence semantics.

## Gate

WP-0 passes when canonical domain + requirements + architecture can specify an executable NEP core without inventing I20 or provider-specific meaning.

## Next

Inspect the smallest current NEP evidence set, resolve the WP-0 semantic choices, persist the accepted contract, then open WP-1 only if no blocking unknown remains.
