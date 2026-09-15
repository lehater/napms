# Active execution

Current: `PLAN-130-revalidate-policy-lifecycle.md`

Goal: revalidate the selected first-MVP product contracts after clarification of concrete Component deployment identity, policy-rule change behavior, and evidence-derived access proposals.

Current task: update the affected observable requirements and evaluate G1 before changing Strategic/Tactical DDD.

Lifecycle stage: `S1`
Stage state: `IN_PROGRESS`
Lifecycle basis: stakeholder clarification conflicts with the accepted `ApplicationDeployment + ComponentPlacement` product model and governed-subject behavior in current G1 requirements; per `docs/process/change-lifecycle.md`, the earliest affected canonical layer is Requirements.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## Working set

Read first:
- `docs/plans/active/PLAN-130-revalidate-policy-lifecycle.md`
- `docs/requirements/application-catalogue-domain-target.md`
- `docs/requirements/access-governance-g1.md`
- `docs/requirements/access-policy-core.md`
- `docs/requirements/first-mvp-vendor-neutral-policy-export.md`

## Blockers

None at S1. Whether governance-change history and current Policy Rule truth remain separate Bounded Context responsibilities is deliberately deferred to S2 after G1.

## Gate

G1 — affected requirements coherent enough that S2 need not invent deployment identity, current-vs-proposed policy behavior, or evidence-derived proposal behavior.

## Next

Replace the affected G1 wording, evaluate G1, then route the accepted delta through Strategic DDD before Tactical DDD. Production-code implementation remains forbidden.
