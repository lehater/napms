# PLAN-039 — I25 Product Completion, Operator UX and Acceptance

Status: `active — WP2B operator realization/execution read surface`

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
- upstream product/runtime and downstream realization/execution proofs were separated by fixture/seed boundaries;
- P0 was the absence of one executable Requirement -> Decision -> Rule -> realization -> rendering -> execution -> verification acceptance proof;
- P1 gaps are downstream operator visibility and cross-chain explainability;
- P2 gaps include role/task navigation, uneven search/filtering and Web dependency lockfile reproducibility debt;
- speculative dashboards, exports and bulk operations remain unjustified.

Evidence: `docs/engineering/product-completion-gap-matrix.md`.

## WP2A — Full-chain acceptance composition/test

Status: `done`.

Implemented evidence:
- `tests/integration/postgres/test_product_completion_acceptance.py` declares a real Connectivity Requirement through its application API;
- records a real PostgreSQL-backed Connectivity Decision referencing that Requirement;
- Access Policy consumes that real Decision through `ConnectivityDecisionConsumerAdapter` and materializes the exact Rule;
- NEP placement and configured TAE evidence feed APR;
- APR derives desired policy, proves `Drift/Add`, renders the accepted target artifact;
- NEO deterministic execution returns `Verified` with matching post-state digest;
- exact Requirement/Decision/Rule and APR rule-reference continuity is asserted;
- no production-domain change or copied cross-context persistence was introduced.

Verification:
- PostgreSQL suite passed after aligning the expected APR provenance reference to canonical `access-rule:<uuid>` form;
- harness passed after restoring the mandatory plan exit-criteria section.

## WP2B — Network-operator realization/execution read model and HTTP surface

Status: `active`.

Purpose:
provide the smallest truthful read surface for placement, reconciliation, rendering and operation evidence without turning NEP/TAE/APR/NEO into generic CRUD workspaces.

Discovered runtime constraint:
- the current HTTP runtime has no selected source for a `ManagedReconciliationScopeContract` or configured TAE evidence selection;
- NEO is not wired to HTTP and its current operation repository is process-local/in-memory;
- therefore an operator view must not manufacture `Satisfied/Drift`, configured-state or execution history when those inputs are unavailable.

Required semantics:
- owner-preserving composition only;
- distinguish `Available`, `NotAvailable` and `Unknown/Ambiguous` rather than interpreting absence as a fact;
- desired policy/placement/rendering may be shown when their owning inputs are available;
- reconciliation is shown only when an explicit configured-evidence selection and managed-scope contract are available;
- operation result is shown only from an actual NEO operation record/result, never inferred from rendering;
- local deterministic technical fixtures may make the demo executable but remain bootstrap/demo facts, not production truth.

Exit:
- accepted requirement/architecture contract for the operator projection;
- framework-free read composition with tests for available and fail-closed unavailable/unknown inputs;
- authenticated HTTP read surface over that projection;
- no new authoritative cross-context table.

## WP3 — Explainability and operator Web journey

Status: `blocked on WP2B`.

Connect existing Requirement/Decision/Rule provenance to the downstream operator projection and provide bounded role/task navigation without inventing new IAM semantics.

## WP4 — Search/filter/bounded operator productivity

Status: `blocked on WP3 evidence`.

Improve only concrete task bottlenecks. Bulk actions and extra serializers remain closed unless the operator journey demonstrates a consumer need.

## WP5 — End-to-end local acceptance chain

Status: `executable core chain proven by WP2A; final product acceptance blocked on WP3 explainability`.

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

Status: `blocked on WP2B-WP6`.

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

No external infrastructure blocks WP2B. The main semantic constraint is internal: configured reconciliation and operation history can only be presented when their actual owning inputs/results exist. Real Cisco/device access, corporate identity and enterprise sources remain optional.

## Next

Define and accept the owner-preserving network-operator projection contract, including explicit unavailable/unknown states for missing configured evidence/managed-scope contract/operation result, then implement its framework-free read composition before adding HTTP or Web presentation.