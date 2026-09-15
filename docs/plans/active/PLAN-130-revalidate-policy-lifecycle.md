# PLAN-130 — Revalidate deployment and policy lifecycle semantics

Status: `active`

## Goal

Converge the target Strategic/Tactical DDD after G1 revalidation established concrete Component Deployment endpoints, current-vs-proposed rule revision behavior, and evidence-derived access proposals.

## Inputs

- `docs/requirements/application-catalogue-domain-target.md`
- `docs/requirements/access-governance-g1.md`
- `docs/requirements/access-policy-core.md`
- `docs/requirements/first-mvp-vendor-neutral-policy-export.md`
- `docs/requirements/business-connectivity-g1.md`

## Exit criteria

- concrete Component Deployment has one coherent semantic owner, identity and Resource relation;
- proposal/change history and current effective policy have one coherent lifecycle owner without duplicated authority;
- ACC revision, RC Resource, Business Connectivity and TAE recognition relationships use explicit public semantic contracts;
- affected Tactical identities/lifecycles/invariants are explicit;
- vendor-neutral export consumes only published owner truth;
- G2 is re-evaluated for the affected slice with no P0/P1 semantic contradiction.

## Blockers

None currently. The principal Strategic question is whether the existing Access Governance / Access Policy split still represents independent semantic lifecycles or artificially splits one Access Rule lifecycle.

## Next

Challenge the affected Strategic boundaries and public contracts, update canonical Strategic artifacts, then revalidate only the dependent Tactical models and evaluate G2.
