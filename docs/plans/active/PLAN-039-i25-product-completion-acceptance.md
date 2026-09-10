# PLAN-039 — I25 Product Completion, Operator UX and Acceptance

Status: `active — WP3 explainability and operator Web journey`

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
- current Web/HTTP product surface was complete through Connectivity, Needs, Decisions, Rules, Effective Desired Policy and Normalized Policy;
- NEP/TAE/APR/NEO were executable internally but had no human-facing operator surface;
- upstream product/runtime and downstream realization/execution proofs were separated by fixture/seed boundaries;
- P0 was the absence of one executable Requirement -> Decision -> Rule -> realization -> rendering -> execution -> verification acceptance proof;
- P1 gaps were downstream operator visibility and cross-chain explainability;
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

## WP2B — Network-operator realization/execution read model and HTTP surface

Status: `done`.

Implemented:
- accepted requirement `docs/requirements/network-operator-realization-view.md` and architecture boundary `docs/architecture/network-operator-realization-view.md`;
- framework-free `src/napms/network_operator_view/application.py` with authority-first admission and stage availability `Available | NotAvailable | Unknown`;
- dedicated Authority Management adapter/action `ReadNetworkOperatorRealization`;
- PostgreSQL composition reusing APR owner-preserving services rather than cross-context table reads;
- PostgreSQL integration proof that desired/placement/rendering can be available while unselected configured/operation inputs remain explicitly `NotAvailable`;
- separate runtime router `src/napms/runtime/network_operator_view_http.py`;
- local-demo authority seed includes the explicit operator-view read action;
- HTTP DTO preserves owner references/target/render metadata and never infers reconciliation or operation success.

Verification:
- core gate passed;
- PostgreSQL persistence gate passed;
- harness gate passed;
- knowledge gate passed;
- Docker local runtime gate passed.

## WP3 — Explainability and operator Web journey

Status: `active`.

Purpose:
connect the proven operator DTO to one bounded Web workspace and make owner references navigable without introducing new semantic ownership or mutation authority.

Current slice:
- add one `Realization` navigation target under Operations;
- show desired/placement, reconciliation, rendering and controlled-operation stages with the backend-provided availability unchanged;
- expose rendered artifact content only when returned by the backend;
- link contributing `access-rule:<uuid>` references to the existing authoritative Rule detail page;
- keep reconciliation/operation visibly unavailable when the runtime has no selected configured input or actual operation result;
- no mutation buttons, generic role model, dashboard or duplicated semantic calculation in Web.

Exit:
- Web build/runtime gate proves the workspace compiles and is served;
- operator can inspect the downstream stage chain for one scope/as-of and navigate to contributing Rule detail;
- Web does not broaden authority or semantic certainty beyond the HTTP projection.

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

Status: `blocked on WP3-WP6`.

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

No external infrastructure blocks WP3. Configured reconciliation and operation history remain unavailable in the runtime until actual owning inputs/results are supplied; Web must preserve that fact.

## Next

Verify the new Realization Web workspace through the repository gate cycle. If green, assess the remaining explainability gap against Requirement -> Decision -> Rule navigation and only add the smallest missing cross-link.