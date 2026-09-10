# PLAN-039 — I25 Product Completion, Operator UX and Acceptance

Status: `active — WP2A full-chain acceptance proof`

Date: 2026-09-10.

## Goal

Close the remaining supported-local-product gaps and prove the complete NAPMS chain through role-appropriate operator surfaces, explainability and executable end-to-end acceptance without inventing enterprise integrations or new domain semantics merely for presentation convenience.

## Inputs

Canonical inputs:
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/engineering/current-state.md`;
- `docs/architecture/current-architecture.md`;
- `docs/engineering/product-completion-gap-matrix.md`;
- accepted requirements and domain ownership contracts for the existing I1-I24 chain.

## WP1 — Product completion audit and acceptance map

Status: `done`.

Accepted outcome:
- current Web/HTTP product surface is complete through Connectivity, Needs, Decisions, Rules, Effective Desired Policy and Normalized Policy;
- NEP/TAE/APR/NEO are executable internally but have no human-facing operator surface;
- upstream product/runtime and downstream realization/execution proofs are separated by fixture/seed boundaries;
- P0 is the absence of one executable Requirement -> Decision -> Rule -> realization -> rendering -> execution -> verification acceptance proof;
- P1 gaps are downstream operator visibility and cross-chain explainability;
- P2 gaps include role/task navigation, uneven search/filtering and Web dependency lockfile reproducibility debt;
- speculative dashboards, exports and bulk operations remain unjustified.

Evidence: `docs/engineering/product-completion-gap-matrix.md`.

## WP2A — Full-chain acceptance composition/test

Status: `active`.

Purpose:
close the P0 evidence gap before adding UI.

Required chain:
```text
real Connectivity Requirement declaration
    -> real Connectivity Decision persistence/selection
    -> Access Rule proposal/materialization using the real decision seam
    -> effective desired policy
    -> NEP placement + TAE configured evidence
    -> APR desired-vs-configured conclusion
    -> APR target rendering
    -> NEO deterministic controlled execution
    -> post-check Verified evidence
```

Rules:
- use existing application/domain APIs and context-owned repositories;
- no copied cross-context truth or new persistence;
- no `AllowedDecision` test stub at the Decision -> Access Policy handoff;
- assert exact subject/reference continuity at semantic handoffs;
- deterministic NEO target stub is accepted execution evidence and does not claim real Cisco transport.

Exit:
- one PostgreSQL integration acceptance test proves the complete supported local chain and fail-closed ownership boundaries without direct application-table mutation for lifecycle facts that already have owning APIs.

## WP2B — Network-operator realization/execution read model and HTTP surface

Status: `blocked on WP2A`.

Define the smallest read-only owner-preserving projection needed to inspect placement, reconciliation, rendering and execution evidence. Prefer one operator composition over generic CRUD surfaces per bounded context.

## WP3 — Explainability and operator Web journey

Status: `blocked on WP2B`.

Connect existing Requirement/Decision/Rule provenance to the downstream operator projection and provide bounded role/task navigation without inventing new IAM semantics.

## WP4 — Search/filter/bounded operator productivity

Status: `blocked on WP3 evidence`.

Improve only concrete task bottlenecks. Bulk actions and extra serializers remain closed unless the operator journey demonstrates a consumer need.

## WP5 — End-to-end local acceptance chain

Status: `partly advanced by WP2A; final product acceptance blocked on WP3`.

The final accepted local product criterion remains:
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

## WP6 — Operator runbook and explicit exclusions

Status: `blocked on WP3-WP5`.

Consolidate supported local startup/recovery/upgrade/product workflows and explicit remaining exclusions.

## WP7 — Final product verification and roadmap closure

Status: `blocked on WP2A-WP6`.

Run repository gates and acceptance evidence, absorb durable outcomes into canonical truth, retire PLAN-039 and mark the current post-Wave-1 roadmap complete for the supported local target.

## Exit criteria

I25 exits when:
- one executable PostgreSQL-backed acceptance proof demonstrates the mandatory Requirement -> Decision -> Rule -> realization -> rendering -> controlled execution -> Verified local chain;
- downstream placement/reconciliation/rendering/execution evidence is available through the smallest justified owner-preserving operator read surface;
- the Web product provides a bounded network/security operator journey and cross-chain explainability without introducing copied authoritative state or generic IAM roles;
- any additional search/filter/productivity work is tied to demonstrated operator needs, while unjustified dashboards/bulk/export surfaces remain excluded;
- the supported local operator runbook and explicit optional-integration exclusions are current;
- core, PostgreSQL persistence, Web, harness, knowledge and relevant Docker/runtime gates pass on the final merge candidate;
- durable I25 outcomes are absorbed into canonical current-state/architecture/roadmap truth and PLAN-039 is retired.

## Blockers

None for WP2A. Real Cisco/device access, corporate identity, external authoritative sources and enterprise infrastructure remain optional and non-blocking.

## Next

Build the real PostgreSQL-backed Requirement -> Decision -> Rule handoff, then extend the existing APR/NEP/TAE/NEO proof through reconciliation, rendering and Verified execution without using the historical `AllowedDecision` stub.