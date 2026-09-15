# PLAN-130 — Revalidate deployment and policy lifecycle semantics

Status: `active`

## Goal

Revalidate the first-MVP product contracts after stakeholder clarification of concrete component deployment identity, policy-rule change behavior, and evidence-derived access proposals before reopening Strategic/Tactical DDD.

## Inputs

- `docs/requirements/application-catalogue-domain-target.md`
- `docs/requirements/access-governance-g1.md`
- `docs/requirements/access-policy-core.md`
- `docs/requirements/first-mvp-vendor-neutral-policy-export.md`
- `docs/requirements/business-connectivity-g1.md`

## Exit criteria

- affected observable requirements no longer depend on logical whole-Application deployment + placement-set semantics;
- pending/rejected access changes cannot silently replace current effective policy;
- evidence-derived recognition/proposal behavior is explicit without promoting evidence to authorization;
- G1 is re-evaluated for the affected slice;
- accepted requirements are sufficient to enter S2 without inventing product behavior.

## Blockers

None currently. Strategic ownership of proposal/change-request versus current policy remains an S2 question after G1.

## Next

Update the smallest affected G1 requirement owners, evaluate G1, then enter Strategic DDD only for the affected context relationships.
