# Post-Wave-1 product completion roadmap

Status: `accepted ordered sequencing baseline; I22 complete, I23 lightweight extension skeleton active`.

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
- I1-I22;
- Wave 1 proposal -> Connectivity Decision seam -> Access Rule -> effective desired policy -> coherent normalized policy;
- PostgreSQL persistence;
- Web/HTTP runtime;
- Dockerized local runtime;
- local username/password authentication with server-side sessions;
- human-readable catalogue UX;
- Technical Access Evidence Tactical DDD, durable source-qualified persistence and strict local/import proof;
- Access Policy Realization through technical-to-domain resolution, enforcement placement consumption, desired-vs-configured reconciliation and first target-specific configuration rendering;
- Network Environment Operations stub-first execution semantics through controlled pre-check, conditional apply and post-check verification.

Current product direction:
- local deployment and local data remain the supported operating model;
- real provider/device transport and lab validation remain optional future integrations;
- external identity/source integrations are optional extension work, not a prerequisite for product completion;
- deterministic stubs are sufficient where an extension seam needs executable proof.

Still deferred unless explicitly selected by a future requirement:
- real provider/device transport and lab validation;
- crash-durable execution audit and production rollback;
- external identity providers, directories, CMDB/catalogue sources and Legacy/MSSQL bridges.

## Ordered increments

### Completed increments — I13 through I22

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

Detailed completed execution is not roadmap state. Durable outcomes live in current requirements/domain/architecture/engineering artifacts; Git history preserves the execution record.

### I17 — Technical Access Evidence Core

Status: `done / absorbed into canonical truth`.

Goal:
implement the accepted **Technical Access Evidence** bounded context.

Exit achieved:
NAPMS can persist/query technical evidence without treating evidence as authorization.

### I18 — Technical-to-Domain Access Resolution

Status: `done / absorbed into canonical truth`.

Exit achieved:
technical evidence can be explained in domain interaction terms without consumer-specific meaning.

### I19 — Network Enforcement Placement

Status: `done / absorbed into canonical truth`.

Exit achieved:
NAPMS can derive/explain enforcement placement for domain-attributable traffic without embedding vendor syntax or realization semantics.

### I20 — Desired-vs-Configured Reconciliation and Enforcement Policy Derivation

Status: `done / absorbed into canonical truth`.

Exit achieved:
NAPMS can truthfully answer whether complete configured effective-Permit evidence realizes desired policy for one proven managed enforcement scope and what exact semantic delta remains.

### I21 — Configuration Rendering

Status: `done / absorbed into canonical truth`.

Exit achieved:
NAPMS can produce a deterministic, provenance-preserving Cisco ASA representation for the supported desired enforcement subset and prove that the representation is semantically exact.

### I22 — Network Environment Operations

Status: `done / absorbed into canonical truth`.

Goal achieved:
model controlled provider/device-facing operation semantics downstream of rendering without inventing unavailable real-lab integration details.

Accepted/implemented semantics:
- Network Environment Operations is a separate semantic module with its own operation identity/outcome/concurrency/provenance responsibility;
- NEO Domain owns `OperationTarget` and has no APR domain dependency; APR Enforcement Target is projected only at composition;
- `operation_id` binds one target + artifact digest; identical retry is idempotent and conflicting reuse fails closed;
- mutation admission is an explicit authority port;
- pre-check/current revision plus conditional apply provide optimistic concurrency;
- apply result is distinct from final verification;
- apply states are `Applied | PreconditionFailed | Rejected | Unknown`;
- final outcomes are `Verified | PreconditionFailed | Rejected | Drift | Unknown`;
- `Verified` requires post-check evidence whose artifact digest matches the requested artifact;
- Unknown apply is never converted into success and is not blindly retried;
- first executable target adapter is a deterministic in-process stub because no real Cisco lab is available;
- first operation repository is in-memory and therefore does not claim crash-durable audit.

Implemented:
- framework-free NEO Domain/Application/consumer-owned ports;
- deterministic target stub scenarios for success/reject/unknown-apply/concurrent-change/post-apply-drift;
- unit proofs for authority denial, stale revision, concurrency, rejection, uncertainty, drift, idempotent retry and operation-id conflict;
- PostgreSQL-backed integration from desired policy -> Cisco ASA rendering -> NEO target projection -> stub apply -> post-check Verified;
- adversarial integration proving no blind retry after Unknown and no false Verified under concurrent target change;
- no Access Policy, NEP or TAE owner-state mutation from the execution flow.

Exit achieved:
NAPMS has an executable, fail-closed network-operation semantic loop through a deterministic stub, while explicitly deferring real Cisco transport validation until a lab/provider contract exists.

### I23 — Optional Integration Extension Skeleton

Status: `active; lightweight scope`.

Goal:
keep the local-first product unchanged while establishing only minimal dormant extension seams for possible future external identity/source adapters.

Required scope:
- retain local username/password authentication as the primary runtime path;
- retain local Authority/ACC/Resource data as the supported current source of truth;
- keep a source-neutral optional external-identity -> NAPMS-actor mapping seam;
- keep identity separate from Authority Management authorization;
- document where future source adapters would terminate at context-owned import/projection boundaries;
- use deterministic in-process stubs only where an executable seam proof is useful.

Explicitly not required:
- OIDC/OAuth2;
- corporate IdP or directory integration;
- external Authority administration;
- real ACC/Resource/CMDB synchronization;
- Legacy/MSSQL;
- external-source schedulers, transports, freshness/completeness/deletion protocols;
- replacing the current local login/session path.

Exit:
NAPMS remains fully usable in local mode, while future integrations have bounded extension points that do not pollute Domain or alter semantic ownership.

Guardrail:
real external integration is future optional work triggered only by a concrete accepted requirement. It is not a mandatory predecessor for later roadmap increments.

### I24 — Local Deployment and Operational Hardening

Status: `planned after I23 skeleton`.

Goal:
make the supported local deployment more robust and supportable without assuming an enterprise production topology.

Expected scope, selected only where useful for the local target environment:
- local TLS/secure ingress options where required;
- secret/configuration handling;
- PostgreSQL authentication and migration/upgrade procedure;
- backup/restore;
- metrics/monitoring/logging appropriate to the local deployment;
- dependency/container hardening;
- recovery procedure;
- accepted workload envelope and performance validation.

External HA, enterprise secret stores, corporate identity, multi-node capacity topology and similar infrastructure remain deferred until a concrete target environment requires them.

### I25 — Product Completion, Operator UX and Acceptance

Status: `planned final integration increment`.

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
