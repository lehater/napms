# Active execution

Current: `PLAN-034-i20-realization-reconciliation.md`
Goal: Complete I20 desired-vs-configured reconciliation and enforcement-policy derivation without pulling I21 rendering or I22 execution forward.
Current task: WP-0 — Tactical DDD, managed-scope/evidence semantics and architecture closure.

Working mode: domain re-entry; primary Skill `domain-model-change`.

## Working set

Read first:
- `docs/plans/active/PLAN-034-i20-realization-reconciliation.md`
- `docs/domain/access-policy-realization/tactical-model.md`

Expand only if needed:
- `docs/domain/technical-access-evidence/tactical-model.md`
- `docs/domain/network-enforcement-placement/tactical-model.md`
- `docs/domain/semantic-ownership.md`
- `docs/domain/ubiquitous-language.md`
- `docs/requirements/policy-export-core.md`
- `src/napms/access_policy_realization/`
- `src/napms/policy_export/`

Recovery facts:
- I19 is complete; I20 remains inside Access Policy Realization rather than creating a new Bounded Context.
- Comparing all TAE `Configured` entries directly with desired policy is unsafe: TAE does not itself claim currentness, coverage completeness or Logical Firewall correspondence.
- `Remove`/complete `No-op` additionally require proof that desired policy and configured evidence cover the same managed enforcement-policy partition.
- I18 Technical-to-Domain Resolution remains the shared matcher for configured-domain attribution.
- I21 rendering and I22 provider/device execution remain downstream.

## Blockers

WP-0 must resolve managed-scope equivalence, configured source completeness/effective-policy semantics, enforcement-target granularity and explicit evidence-time selection before core implementation.

## Gate

WP-0 passes when those semantic choices are accepted with fail-closed Unknown/ambiguity behavior and encoded in Tactical DDD, requirements and architecture.

## Next

Complete I20 WP-0, including the stale I19 strategic-model repair; only then implement the framework-free APR core.
