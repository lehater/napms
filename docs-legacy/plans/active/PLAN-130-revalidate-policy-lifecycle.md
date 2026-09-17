# PLAN-130 — Revalidate deployment and policy lifecycle semantics

Status: `active`

## Goal

Converge the target requirements, Domain Design and Architecture around concrete Component Deployment endpoints, one Policy Rule lifecycle, evidence-derived access candidates, and a deliberately minimal policy-decision model that does not embed customer-specific approval workflow.

## Inputs

- `docs/requirements/application-catalogue-domain-target.md`
- `docs/requirements/access-governance-g1.md`
- `docs/requirements/access-policy-core.md`
- `docs/requirements/first-mvp-vendor-neutral-policy-export.md`
- `docs/requirements/business-connectivity-g1.md`

## Exit criteria

- concrete Component Deployment has one coherent semantic owner, identity and Resource relation;
- proposal/change history and current effective policy have one coherent lifecycle owner;
- one formal RuleChange decision outcome is sufficient for MVP (`Pending -> Accepted | Rejected`), with organization-specific approval procedures outside the domain baseline;
- no source/destination bilateral approval algebra or Responsibility Scope resolution is required merely to decide a RuleChange;
- actor authority may protect propose/decide/withdraw actions without modelling the external organizational process that produced the decision;
- ACC revision, RC Resource, Business Connectivity and TAE recognition relationships use explicit public semantic contracts;
- vendor-neutral export consumes only published owner truth;
- G1, G2 and G3 are re-evaluated in order after this simplification, with no P0/P1 contradiction;
- no production implementation starts before G4.

## Blockers

None currently.

## Next

Reopen S1 for policy-decision semantics, re-run G1 and dependent S2/G2, then return to S3 and remove architecture dependencies that existed solely for bilateral approval/scope-resolution behavior.
