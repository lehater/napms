# PLAN-039 — I25 Product Completion, Operator UX and Acceptance

Status: `active — WP1 completion audit and acceptance map`

Date: 2026-09-10.

## Goal

Close the remaining supported-local-product gaps and prove the complete NAPMS chain through role-appropriate operator surfaces, explainability and executable end-to-end acceptance without inventing enterprise integrations or new domain semantics merely for presentation convenience.

## Inputs

Canonical inputs:
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/engineering/current-state.md`;
- `docs/architecture/current-architecture.md`;
- current Web/HTTP workspaces and product read models;
- accepted requirements and domain ownership contracts for the existing I1-I24 chain.

## WP1 — Product completion audit and acceptance map

Status: `active`.

Purpose:
- inventory current human-facing workspaces, HTTP surfaces and executable end-to-end proofs;
- map the roadmap product-completion criterion from declared connectivity need through decision, Access Rule, realization, rendering, controlled execution, post-check evidence and explainability;
- identify gaps by operator role and stage without promoting optional enterprise/provider integrations to mandatory scope;
- classify findings P0/P1/P2/P3 and distinguish semantic gaps from presentation/acceptance gaps.

Exit:
- one repository-owned completion matrix names every mandatory local-chain stage, its current evidence and remaining gap;
- each proposed I25 implementation item has a concrete user/operator need and owning semantic source;
- no dashboard, bulk operation, export or new persistence is added without a demonstrated gap.

## WP2 — Role-appropriate workflow closure

Status: `blocked on WP1`.

Scope candidate, selected only from WP1 evidence:
- requirement owner workflow;
- decision participant workflow;
- security/network operator workflow;
- bounded navigation/actions needed to move between existing authoritative stages.

Do not create generic role models or IAM semantics; use existing Authority actions and accepted read/mutation surfaces.

## WP3 — Explainability and audit navigation

Status: `blocked on WP1`.

Scope candidate:
- connect existing provenance/decision/Rule/realization/execution evidence into navigable explanations;
- expose only evidence already authoritative or derivable through owner-preserving composition;
- keep operational logs separate from business provenance/audit truth.

## WP4 — Search/filter/bounded operator productivity

Status: `blocked on WP1-WP2`.

Scope candidate:
- improve search/filtering where current result sets make operator work materially difficult;
- add bounded bulk operations only where semantics and authority are already explicit;
- add CSV/XLSX or similar serializers only if WP1 identifies a concrete consumer need.

## WP5 — End-to-end local acceptance chain

Status: `blocked on WP1-WP3`.

Build executable acceptance evidence for the supported local product criterion:

```text
declared connectivity need
    -> connectivity decision
    -> authoritative desired Access Rule
    -> effective desired policy
    -> enforcement placement / technical realization
    -> desired-vs-configured conclusion
    -> target rendering
    -> controlled execution
    -> post-change technical evidence
    -> explainable end-to-end provenance
```

The accepted local NEO deterministic target stub may satisfy controlled-execution semantics; no real Cisco transport claim is required.

## WP6 — Operator runbook and explicit exclusions

Status: `blocked on WP2-WP5`.

Scope:
- consolidate the supported local operating journey across startup, recovery, upgrade and product workflows;
- record remaining product exclusions/deferred integrations explicitly;
- keep enterprise IdP/source integrations, real provider transport, HA and external secret infrastructure optional unless a concrete accepted requirement selects them.

## WP7 — Final product verification and roadmap closure

Status: `blocked on WP1-WP6`.

Run repository gates and end-to-end acceptance evidence, absorb durable outcomes into canonical current-state/architecture/roadmap truth, retire PLAN-039 and mark the current post-Wave-1 product-completion roadmap complete for the supported local target.

## Gate

WP1 is analysis/documentation only. No implementation work beyond completion evidence may begin until the audit identifies a concrete gap, its owning semantic source and the smallest user-facing closure.

## Blockers

None for WP1. Real Cisco/device access, corporate identity, external authoritative sources and enterprise infrastructure remain explicitly non-blocking optional extensions.

## Next

Audit current Web/HTTP surfaces and existing executable proofs against the product-completion chain and role needs. Produce the completion matrix and ranked gap list before selecting WP2/WP3 implementation slices.
