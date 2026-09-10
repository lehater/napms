# Post-Wave-1 product completion roadmap

Status: `accepted ordered sequencing baseline; I24 complete, I25 next`.

Date: 2026-09-10.

## Purpose

Track the ordered path from the completed Wave-1 product slice to the current strategic-model notion of a complete NAPMS product.

This roadmap is durable engineering truth, not the mutable current execution plan.

Execution rule:

```text
roadmap increment selected
    -> create one active PLAN under docs/plans/active/
    -> resolve domain/requirement/architecture unknowns first
    -> implement one coherent semantic stage
    -> final gates
    -> absorb durable outcomes into canonical truth
    -> remove completed active PLAN
    -> promote the next roadmap increment
```

The roadmap may be refined when new accepted domain evidence changes boundaries or sequencing. Do not silently implement a later context because an earlier semantic dependency is still unknown.

## Baseline

Completed:
- I1-I24;
- Wave 1 proposal -> Connectivity Decision seam -> Access Rule -> effective desired policy -> coherent normalized policy;
- PostgreSQL persistence;
- Web/HTTP runtime;
- Dockerized local runtime;
- local username/password authentication with server-side sessions;
- human-readable catalogue UX;
- Technical Access Evidence Tactical DDD, durable source-qualified persistence and strict local/import proof;
- Access Policy Realization through technical-to-domain resolution, enforcement placement consumption, desired-vs-configured reconciliation and first target-specific configuration rendering;
- Network Environment Operations stub-first execution semantics through controlled pre-check, conditional apply and post-check verification;
- optional source-neutral external identity/source extension boundaries without changing the local-first runtime;
- local deployment hardening with PostgreSQL password/SCRAM authentication, repeatable non-mutating startup, logical backup/clean restore, forward migration/recovery procedure, local status diagnostics and low-risk container hardening.

Current product direction:
- local deployment and local data remain the supported operating model;
- real provider/device transport and lab validation remain optional future integrations;
- external identity/source integrations are optional extension work, not a prerequisite for product completion;
- deterministic stubs are sufficient where an extension seam needs executable proof;
- product-completion work now focuses on operator UX, explainability and end-to-end acceptance of the supported local chain.

Still deferred unless explicitly selected by a future requirement:
- real provider/device transport and lab validation;
- crash-durable execution audit and production rollback;
- external identity providers, directories, CMDB/catalogue sources and Legacy/MSSQL bridges;
- enterprise HA, public TLS automation, external secret stores and multi-node topology;
- performance/SLA claims without an accepted workload target.

## Ordered increments

### Completed increments — I13 through I24

Status: `done / absorbed into canonical truth`.

- I13 — Connectivity Requirements Core: durable Requirement identity/lifecycle/authority with `Required != Authorized`.
- I14 — Requirement-to-Policy Alignment: derived `Covered | Uncovered | NotCurrent | Unknown` composition without peer persistence.
- I15 — Connectivity Decision Domain Closure: first-class final Decision semantics, authority, validity, reason/provenance and supersession; ADR-005 supersedes the historical deferred port.
- I16A — Scoped Connectivity Workspace Foundation: Resource Scope Affiliation, `ReadScopedConnectivity`, owner-preserving inventory composition, authenticated HTTP read surface, resource-centric Web workspace and contextual Request access for existing exact ACC interactions.
- I16B — Connectivity Decision Runtime and Workflow: durable immutable Decision persistence/selection, independent Decide/Read authority, Access Policy and Scoped Connectivity integration, authorized Decision Web/HTTP workspace, and local Docker runtime without deterministic allow plumbing.
- I17 — Technical Access Evidence Core: accepted Tactical DDD, immutable source-qualified evidence identity/time/provenance, framework-free core, TAE-owned PostgreSQL persistence, strict local/import normalization and dedicated durable record/readback proof without authorization or realization leakage.
- I18 — Technical-to-Domain Access Resolution: accepted consumer-independent APR correspondence algebra, exact remainder/ambiguity/Unknown semantics, predicate-aware RC/ACC + TAE adapters and durable PostgreSQL resolution proof without authorization, placement or reconciliation leakage.
- I19 — Network Enforcement Placement: accepted exact endpoint-pair first slice, normalized forwarding/path knowledge, stable Logical Firewall identity, temporal provider correspondence/Enforcement Attachments, fail-closed placement selection and NEP-owned durable PostgreSQL proof without I20 reconciliation or vendor execution.
- I20 — Desired-vs-Configured Reconciliation and Enforcement Policy Derivation: accepted APR-managed-scope/effective-Permit contract, exact desired/configured policy algebra, owner-preserving AP/RC/ACC/NEP/TAE adapters and durable PostgreSQL proof of No-op/Add/Remove/Replace with fail-closed uncertainty.
- I21 — Configuration Rendering: accepted APR-owned rendering semantics, first Cisco Secure Firewall ASA CLI extended ACL renderer, deterministic fail-closed output, statement provenance, independent semantic projection/equivalence proof and PostgreSQL owner-preserving derive -> render integration without provider/device mutation.
- I22 — Network Environment Operations: separate NEO semantic module, NEO-owned `OperationTarget`, mutation authority port, operation-id idempotency, optimistic target-revision concurrency, explicit apply/final outcomes, post-check verification, deterministic target stub and end-to-end desired -> rendered -> stub-applied -> verified composition proof. No real Cisco transport is claimed.
- I23 — Optional Integration Extension Skeleton: local login and local Authority/ACC/Resource state remain primary; a dormant provider-qualified external identity -> actor resolution seam and context-owned future source-adapter boundaries are defined; deterministic tests prove fail-closed mapping without OIDC, IdP, CMDB, MSSQL or external synchronization dependencies.
- I24 — Local Deployment and Operational Hardening: supported Compose no longer uses PostgreSQL network trust; fresh volumes use SCRAM host auth; ephemeral DB credentials are rotated safely across preserved volumes; startup is non-mutating/repeatable; logical backup/validated clean restore and forward-upgrade recovery are supported; migration replay is proven no-op; local status diagnostics and reversible container hardening are present; enterprise topology/performance claims remain explicitly deferred without accepted requirements.

Detailed completed execution is not roadmap state. Durable outcomes live in current requirements/domain/architecture/engineering artifacts; Git history preserves the execution record.

### I24 — Local Deployment and Operational Hardening

Status: `done / absorbed into canonical truth`.

Accepted outcome:
- PostgreSQL network `trust` removed from the supported local Compose path;
- fresh local volumes initialize host authentication with SCRAM-SHA-256;
- application/migration/seed database access requires an explicit password;
- supported startup generates an ephemeral DB credential and rotates the local role before dependent services start, including preserved-volume restart;
- correct-password acceptance and wrong-password rejection are executable checks;
- supported `make dev-up` uses a non-mutating readiness/login/session/read probe; the stateful mutation journey remains separate CI evidence;
- PostgreSQL custom-format logical backup is validated before publication and before destructive clean restore;
- clean-volume restore is explicit, destructive and followed by normal migration/startup verification;
- forward upgrade requires a pre-upgrade backup; migration checksum mismatch fails closed; arbitrary downgrade is not promised;
- repeated migration execution on current restored state is proven to leave the migration journal and durable Access Rule state unchanged;
- `make dev-status` checks Compose state, public live/ready and PostgreSQL queryability;
- backend/Web application containers use low-risk init/reaping and `no-new-privileges`, with backend execution remaining non-root;
- dedicated metrics, enterprise HA/TLS/secret stores and capacity/SLA claims remain deferred because the selected local target does not require or justify them.

Exit achieved:
NAPMS has an executable and verified local deployment/recovery/upgrade operating contract without inventing enterprise infrastructure or changing product/domain semantics.

### I25 — Product Completion, Operator UX and Acceptance

Status: `next; not yet selected for execution`.

Goal:
close the remaining product-operability surface and prove the complete local NAPMS chain.

Expected scope:
- role-appropriate workspaces for requirement owner, decision participant, security/network operator;
- dashboard only from real use-case/read models;
- mature search/filtering and bounded bulk operations where accepted;
- global explainability/audit navigation;
- export serializers such as CSV/XLSX only if a real consumer needs them;
- end-to-end acceptance from Connectivity Requirement through decision, Access Rule, realization, rendering, execution and post-check evidence;
- operational/runbook documentation for the selected local environment;
- explicit closure of remaining local-product deferrals or documented exclusions.

## Dependency sequence

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

External provider/identity/source integrations are not part of this mandatory dependency chain. If selected later, they receive their own increment/plan based on concrete requirements.

## Tracking rules

- Only the selected current increment gets a detailed `PLAN-*.md` under `docs/plans/active/`.
- This roadmap carries future ordering/status; it does not duplicate dynamic work-package state.
- When an increment completes, update this file in the same semantic stage: mark it `done`, record any accepted split/resequence, and promote the next roadmap increment.
- If a future increment becomes too large, split it before implementation and update the sequence here.
- Domain unknowns remain unknown until their owning canonical artifacts accept them.
- No future stage may be pulled forward merely to make a current implementation convenient.

## Product-completion criterion

For this roadmap, “product complete” means the supported local target environment can demonstrate, with accepted semantics and operational evidence:

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

plus the local authentication, deployment, recovery, observability and acceptance controls required for that selected local environment.

Real external identity, authoritative enterprise sources and provider/device transports are optional extensions and are not part of the current product-completion criterion unless a future accepted target environment explicitly selects them.
