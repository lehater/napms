# Post-Wave-1 product completion roadmap

Status: `complete for the supported local target through I25`.

Date: 2026-09-10.

## Purpose

Track the ordered path from the Wave-1 product slice to the accepted supported-local notion of a complete NAPMS product.

This roadmap is durable engineering truth, not mutable execution state.

Execution rule:

```text
roadmap increment selected
    -> create one active PLAN under docs/plans/active/
    -> resolve domain/requirement/architecture unknowns first
    -> implement one coherent semantic stage
    -> final gates
    -> absorb durable outcomes into canonical truth
    -> remove completed active PLAN
```

Future work starts only from a new accepted requirement/target; it is not implicitly part of this completed roadmap.

## Completed baseline

Completed I1-I25 capabilities include:
- authoritative Access Policy, Authority Management, ACC and Resource Catalogue;
- Connectivity Requirements, requirement-to-policy alignment and first-class Connectivity Decision semantics/runtime;
- scoped Connectivity product workspace and policy export;
- Technical Access Evidence, technical-to-domain resolution and Network Enforcement Placement;
- Access Policy Realization desired/configured reconciliation and target-specific rendering;
- Network Environment Operations stub-first controlled-execution semantics;
- optional source-neutral external identity/source extension skeleton without changing local-first operation;
- hardened local deployment/recovery/upgrade contract;
- product-completion acceptance, network-operator realization view, Web explainability journey and reproducible Web dependency graph.

Current product direction remains local-first:
- local deployment and local data are the supported operating model;
- local username/password authentication with server sessions is primary;
- deterministic stubs are sufficient for currently selected optional/device seams;
- external identity/source integrations and real provider/device transport remain optional future work;
- unsupported runtime facts are represented explicitly rather than inferred.

## Ordered increments — completed

- I13 — Connectivity Requirements Core.
- I14 — Requirement-to-Policy Alignment.
- I15 — Connectivity Decision Domain Closure.
- I16A — Scoped Connectivity Workspace Foundation.
- I16B — Connectivity Decision Runtime and Workflow.
- I17 — Technical Access Evidence Core.
- I18 — Technical-to-Domain Access Resolution.
- I19 — Network Enforcement Placement.
- I20 — Desired-vs-Configured Reconciliation and Enforcement Policy Derivation.
- I21 — Configuration Rendering.
- I22 — Network Environment Operations.
- I23 — Optional Integration Extension Skeleton.
- I24 — Local Deployment and Operational Hardening.
- I25 — Product Completion, Operator UX and Acceptance.

All are `done / absorbed into canonical truth`.

## I25 — Product Completion, Operator UX and Acceptance

Accepted outcome:
- one PostgreSQL-backed owner-preserving acceptance scenario proves the complete Requirement -> Decision -> Rule -> realization -> rendering -> deterministic controlled execution -> `Verified` chain;
- a framework-free Network Operator Realization View composes owner data behind dedicated `ReadNetworkOperatorRealization` authority without independent persistence;
- the projection preserves stage availability as `Available | NotAvailable | Unknown` and does not manufacture configured/reconciliation/operation success;
- authenticated HTTP exposes transport DTOs only;
- one read-only `Realization` Web workspace presents desired/placement, reconciliation, rendering and operation evidence;
- explainability navigation closes `Realization -> Access Rule -> Connectivity Decision -> Connectivity Requirement` using existing owner references and owner authorization;
- global search, speculative dashboards, bulk mutation and extra serializers remain unimplemented because the operator journey did not demonstrate a need;
- Web dependency reproducibility debt is closed with package-manager-generated `web/package-lock.json` and `npm ci` in CI/Docker;
- `docs/engineering/local-product-operator-runbook.md` consolidates supported local startup/status/product/recovery/upgrade workflow and explicit exclusions.

I25 does not claim that the interactive runtime always has configured evidence or durable operation history. When those actual owning inputs/results are absent, the Realization view remains `NotAvailable` for the affected stages. Full controlled execution is proven by acceptance evidence using the deterministic NEO target stub; it is not a real Cisco transport claim.

## Completed dependency sequence

```text
I13 Connectivity Requirements Core
  -> I14 Requirement-to-Policy Alignment
  -> I15 Connectivity Decision Domain Closure
  -> I16A Scoped Connectivity Workspace Foundation
  -> I16B Connectivity Decision Runtime
  -> I17 Technical Access Evidence
  -> I18 Technical-to-Domain Resolution
  -> I19 Network Enforcement Placement
  -> I20 Reconciliation / Enforcement Policy
  -> I21 Configuration Rendering
  -> I22 Network Environment Operations
  -> I23 Optional Integration Skeleton
  -> I24 Local Deployment Hardening
  -> I25 Product Completion / Acceptance
```

External provider/identity/source integrations are not part of this mandatory dependency chain.

## Product-completion criterion — achieved for supported local target

The accepted criterion is executable evidence for:

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

plus the local authentication, deployment, recovery, diagnostics and acceptance controls required for the selected local environment.

This criterion is achieved by the combined I1-I25 implementation and acceptance evidence. The final I25 absorption candidate passed core, PostgreSQL persistence, Web, harness, knowledge and Docker local-runtime gates before active-plan retirement.

## Explicit future/non-current work

The completed roadmap does not require:
- real Cisco/provider/device transport or lab validation;
- crash-durable NEO operation audit or production rollback;
- external IdP, directory, CMDB/catalogue/Authority sources or Legacy/MSSQL bridge;
- enterprise HA, public TLS automation, external secret stores or multi-node topology;
- performance/SLA claims without an accepted workload target;
- global search, generic dashboards, bulk mutation or extra exports without a demonstrated consumer need.

Any of these becomes a new roadmap increment only after a concrete accepted requirement/target selects it.

## Tracking after closure

- `docs/engineering/current-state.md` is the capability snapshot;
- `docs/architecture/current-architecture.md` is the cross-cutting architecture boundary;
- `docs/requirements/` and `docs/domain/` remain semantic sources of truth;
- no active PLAN remains until new work is explicitly selected;
- completed execution detail remains in Git history rather than retained active-plan archives.