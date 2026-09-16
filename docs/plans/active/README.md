# Active execution

Current: `PLAN-130-revalidate-policy-lifecycle.md`

Goal: realize the concrete Component Deployment, unified Policy Rule lifecycle and vendor-neutral export without embedding customer-specific approval workflow into the MVP domain.

Current task: revalidate the Access Policy domain model and affected context relationships after G1 accepted one formal RuleChange outcome (`Pending -> Accepted | Rejected`).

Lifecycle stage: `S2`
Stage state: `IN_PROGRESS`
Lifecycle basis: `docs/requirements/access-governance-g1.md` and `access-policy-core.md` record G1 PASS for formal-decision semantics on 2026-09-16; the previous bilateral approval/scope-resolution model is therefore DIRTY.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## Working set

Read first:
- `docs/plans/active/PLAN-130-revalidate-policy-lifecycle.md`
- `docs/domain/access-policy/tactical-model.md`
- `docs/domain/strategic-model.md`
- `docs/domain/context-map.md`
- `docs/domain/mvp-ddd-convergence-checkpoint.md`

## Blockers

None. S2 must remove approval-specific entities/invariants and any AP dependency on RC Responsibility Scope merely for deciding a RuleChange, while preserving optional action authority through Authority Management.

## Gate

G2 — PolicyRule/RuleChange identity and current-vs-proposed semantics remain coherent with one formal decision outcome, no customer-specific approval workflow is embedded, and affected public contracts have one owner.

## Next

Simplify the AP Tactical model and affected strategic contracts, evaluate G2, then return to S3 to simplify the architecture accordingly. Production-code implementation remains forbidden.
