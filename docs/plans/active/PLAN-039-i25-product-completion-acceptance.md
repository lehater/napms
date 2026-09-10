# PLAN-039 — I25 Product Completion, Operator UX and Acceptance

Status: `active — WP7 final verification and closure`

Date: 2026-09-10.

## Goal

Close the remaining supported-local-product gaps and prove the complete NAPMS chain through bounded operator surfaces, explainability and executable end-to-end acceptance without inventing enterprise integrations or new domain semantics for presentation convenience.

## Inputs

Canonical inputs:
- `docs/engineering/post-wave1-product-completion-roadmap.md`;
- `docs/engineering/current-state.md`;
- `docs/architecture/current-architecture.md`;
- `docs/engineering/product-completion-gap-matrix.md`;
- accepted requirements and domain ownership contracts for the existing I1-I24 chain.

## WP1 — Product completion audit and acceptance map

Status: `done`.

The audit identified one P0 full-chain proof gap, P1 downstream operator visibility/explainability gaps, and P2 usability/reproducibility debt. Speculative dashboards, exports and bulk operations were not justified.

Evidence: `docs/engineering/product-completion-gap-matrix.md`.

## WP2A — Full-chain acceptance composition/test

Status: `done`.

`tests/integration/postgres/test_product_completion_acceptance.py` proves one owner-preserving Requirement -> Decision -> Access Rule -> NEP/TAE/APR -> rendering -> deterministic NEO execution -> `Verified` chain with exact identity/provenance continuity and no copied cross-context persistence.

## WP2B — Network-operator realization/execution read model and HTTP surface

Status: `done`.

Implemented and verified:
- accepted `network-operator-realization-view` requirement/architecture contract;
- framework-free owner-preserving read composition;
- dedicated `ReadNetworkOperatorRealization` Authority action;
- PostgreSQL composition and authenticated HTTP router;
- explicit `Available | NotAvailable | Unknown` stage availability;
- no inference of configured state, reconciliation success or operation result when owning inputs/results are absent.

## WP3 — Explainability and operator Web journey

Status: `done`.

Implemented and verified:
- one read-only `Realization` workspace;
- desired/placement, reconciliation, rendering and controlled-operation stages render backend availability unchanged;
- rendered content appears only when returned by the backend;
- explainability navigation closes the existing chain `Realization -> Access Rule -> Connectivity Decision -> Connectivity Requirement` through owner pages and their existing read authorization;
- no duplicated semantic calculation, new IAM role model or mutation controls were added.

## WP4 — Search/filter/bounded operator productivity

Status: `done — reassessed and bounded`.

No operator evidence justified global search, bulk actions, dashboards or additional serializers. Those surfaces remain closed. The concrete P2 Web reproducibility debt was closed with package-manager-generated `web/package-lock.json`; Web CI and Docker builds use `npm ci`.

## WP5 — End-to-end local acceptance chain

Status: `done`.

The supported local product has executable evidence for:

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

The full controlled-execution chain is acceptance evidence. The interactive runtime remains truthful: reconciliation/operation stages are `NotAvailable` until actual configured-evidence/managed-scope inputs or NEO operation results exist.

## WP6 — Operator runbook and explicit exclusions

Status: `done`.

Added `docs/engineering/local-product-operator-runbook.md`, consolidating local startup/status, product journey, explainability navigation, backup/restore/upgrade references, locked Web dependency behavior and explicit exclusions.

## WP7 — Final product verification and roadmap closure

Status: `active`.

Remaining steps:
- absorb I25 into canonical current-state/architecture/roadmap truth;
- update the active resume capsule;
- run final core/PostgreSQL/Web/harness/knowledge/Docker gates on the absorption candidate;
- review the PR diff for semantic/infrastructure overreach;
- retire PLAN-039 and merge the completed I25 change by squash once the final candidate is green.

## Exit criteria

I25 exits when:
- the full PostgreSQL-backed acceptance chain remains green;
- the owner-preserving operator projection and Web journey remain green;
- unsupported runtime stages remain explicitly unavailable/unknown rather than inferred successful;
- the local product runbook and exclusions are current;
- Web dependency resolution is reproducible through the repository lockfile and `npm ci`;
- core, PostgreSQL persistence, Web, harness, knowledge and Docker/runtime gates pass on the final merge candidate;
- durable I25 outcomes are absorbed into canonical truth and PLAN-039 is retired.

## Blockers

No external blocker. Real Cisco/device transport, enterprise identity/sources, crash-durable NEO history and enterprise infrastructure remain optional/deferred and are not I25 exit requirements.

## Next

Finish canonical absorption, run the final gate cycle, review the PR, retire this plan and squash merge I25 if the candidate remains green.