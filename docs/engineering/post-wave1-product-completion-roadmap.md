# Post-Wave-1 product completion roadmap

Status: `accepted ordered sequencing baseline; I21 complete, I22 next`.

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
- I1-I21;
- Wave 1 proposal -> Connectivity Decision seam -> Access Rule -> effective desired policy -> coherent normalized policy;
- PostgreSQL persistence;
- Web/HTTP runtime;
- Dockerized local runtime;
- human-readable catalogue UX;
- Technical Access Evidence Tactical DDD, durable source-qualified persistence and strict local/import proof;
- Access Policy Realization through technical-to-domain resolution, enforcement placement consumption, desired-vs-configured reconciliation and first target-specific configuration rendering.

Wave 1 intentionally stopped before Connectivity Requirements runtime participation; I13 now closes the first Connectivity Requirements core/runtime/workspace slice.

Still deferred:
- device/provider execution;
- production identity/deployment/integration.

## Ordered increments

### Completed increments — I13 through I21

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

Detailed completed execution is not roadmap state. Durable outcomes live in current requirements/domain/architecture/engineering artifacts; Git history preserves the execution record.

### I17 — Technical Access Evidence Core

Status: `done / absorbed into canonical truth`.

Goal:
implement the accepted **Technical Access Evidence** bounded context.

First scope:
- source-qualified evidence identity;
- `Configured | TrafficDerived | Imported`;
- normalized technical predicate semantics;
- provenance/source/time;
- freshness/coverage/confidence vocabulary where accepted;
- ingestion adapters kept outside domain meaning.

Exit:
NAPMS can persist/query technical evidence without treating evidence as authorization.

### I18 — Technical-to-Domain Access Resolution

Status: `done / absorbed into canonical truth`.

Goal:
implement the shared resolution capability inside **Access Policy Realization**.

Accepted/implemented semantics:
- map one normalized Technical Access Predicate against effective RC + ACC knowledge at explicit `asOf`;
- pairwise `Exact | Covers | CoveredBy | PartialOverlap | None`;
- resolution `Exact | Covered | Partial | Ambiguous | Unresolved | Unknown`;
- same resolution semantics for proposal/reconciliation consumers;
- exact unresolved technical remainder for supported exact-protocol predicates;
- ambiguity keeps all competing Domain Interactions and selects no winner;
- predicate-relevant missing/untranslatable knowledge fails closed as Unknown;
- Protocol Any remains Unknown until a protocol-wide applicability/difference model is accepted;
- one-way TAE projection preserves source-qualified provenance without authorization meaning.

Implemented:
- framework-free APR Domain/Application/Ports;
- predicate-aware RC/ACC outer adapter using owner repositories;
- TAE -> APR outer projection adapter;
- no APR persistence or public workflow;
- durable PostgreSQL proof of exact resolution, effective-time change, ambiguity and zero Access Rule/Decision side effects.

Exit achieved:
technical evidence can be explained in domain interaction terms without consumer-specific meaning.

### I19 — Network Enforcement Placement

Status: `done / absorbed into canonical truth`.

Goal achieved:
implement the **Network Enforcement Placement** context needed to answer where traffic is actually subject to enforcement.

Accepted/implemented semantics:
- exact source/destination IP Traffic Relation for the first executable slice;
- normalized ordered Forwarding Path or positive temporal NoForwardingPath fact;
- stable Logical Firewall identity independent from provider/device realization and Resource identity;
- temporal Logical Firewall Correspondence and Enforcement Attachment;
- `Placed | NoEnforcement | NoForwardingPath | Ambiguous | Unknown` selection;
- explicit offset-aware `asOf`, path/attachment/correspondence provenance and fail-closed material uncertainty;
- unsupported forwarding dimensions/multipath remain explicit Unknown rather than guessed.

Implemented:
- framework-free NEP Domain/Application/Ports;
- strict local knowledge import preserving explicit source knowledge gaps;
- immutable relation-scoped NEP-owned PostgreSQL captures and tracked migration;
- deterministic ordered placement with no ambiguity winner;
- operation-scoped PostgreSQL composition;
- durable temporal-switch/domain-attributable proof with no Access Rule, Connectivity Decision or TAE side effects.

Exit achieved:
NAPMS can derive/explain enforcement placement for domain-attributable traffic without embedding vendor syntax or I20 realization semantics.

### I20 — Desired-vs-Configured Reconciliation and Enforcement Policy Derivation

Status: `done / absorbed into canonical truth`.

Goal achieved:
complete the central **Access Policy Realization** outcome.

Accepted/implemented semantics:
- derive vendor-neutral desired enforcement intent only from effective Access Policy + shared I18 domain resolution + complete NEP placement at explicit `asOf`;
- preserve Enforcement Target identity as Logical Firewall + Enforcement Attachment;
- compare only one explicitly selected TAE Configured capture whose source contract proves the same managed policy partition, effective Permit-set meaning, exact evidence time and completeness;
- preserve exact canonical `common = D ∩ C`, `missing = D - C`, `extra = C - D` witnesses;
- classify complete semantic delta as `No-op | Add | Remove | Replace`;
- preserve `Satisfied | Drift | Ambiguous | Unknown` and fail closed on incomplete scope/time/source/evaluation/domain/placement knowledge;
- reuse I18 Technical-to-Domain Resolution unchanged for desired quality and configured attribution.

Implemented:
- framework-free APR Domain/Application/consumer-owned ports;
- owner-preserving Access Policy/Policy Export, RC/ACC, NEP and TAE outer adapters with explicit correlation checks;
- derived-on-demand desired/configured/reconciliation results with no APR persistence;
- PostgreSQL composition over existing owner repositories/use cases;
- hosted executable proof of No-op/Add/Remove/Replace, incomplete-contract Unknown and temporal NEP target movement;
- no vendor rendering, provider/device mutation or public operator workflow.

Exit achieved:
NAPMS can truthfully answer whether complete configured effective-Permit evidence realizes desired policy for one proven managed enforcement scope and what exact semantic delta remains.

### I21 — Configuration Rendering

Status: `done / absorbed into canonical truth`.

Goal achieved:
translate accepted vendor-neutral enforcement intent into target-specific configuration representation without changing desired traffic semantics.

Accepted/implemented semantics:
- rendering remains a downstream capability inside Access Policy Realization, not a separate Bounded Context;
- rendered configuration is derived on demand and has no independent persistence lifecycle;
- first renderer contract is Cisco Secure Firewall ASA CLI extended ACL version `1`;
- supported first slice is IPv4 Permit TCP/UDP with numeric exact/inclusive source/destination ports and exact address-range decomposition into host/CIDR statements;
- deterministic output for identical semantic input and renderer contract;
- `Rendered | Unsupported | Unknown`; failed rendering exposes no partial executable-looking artifact;
- statement provenance preserves Enforcement Target, contributing Access Rules, Domain Interactions, placement provenance and renderer contract;
- successful output requires independent semantic projection back to normalized Permit regions with exact equality to desired regions.

Implemented:
- framework-free APR rendering value/result model and application-owned `ConfigurationRenderer` port;
- `RenderConfiguration` application use case;
- Cisco ASA extended ACL outer adapter;
- independent ASA supported-subset semantic projector;
- positive and adversarial equivalence tests detecting broadening, narrowing and omission;
- PostgreSQL APR composition proof deriving desired policy from owner contexts, rendering ASA ACL, proving exact equivalence and verifying no Access Policy/NEP/TAE state mutation;
- no device/provider acquisition, apply, retry, rollback, concurrency or execution audit.

Exit achieved:
NAPMS can produce a deterministic, provenance-preserving Cisco ASA representation for the supported desired enforcement subset and prove that the representation is semantically exact.

### I22 — Network Environment Operations

Status: `next; not yet selected for execution`.

Goal:
manage provider/device-facing acquisition and mutation.

Expected scope:
- fetch/current-state acquisition adapters;
- pre-check;
- apply change;
- post-check;
- execution result/audit;
- partial/unknown outcomes;
- retry/recovery/rollback semantics;
- safe concurrency/idempotency.

Exit:
one supported enforcement target can complete desired -> rendered -> applied -> verified flow with explicit failure semantics.

### I23 — Enterprise Identity and Authoritative Source Integration

Status: `planned after executable network loop`.

Goal:
replace local/demo runtime dependencies with selected enterprise sources.

Expected areas:
- OIDC/OAuth2/corporate IdP;
- production session/authentication topology;
- real Authority source/administration;
- real Application Communication Catalogue source;
- real Resource Catalogue source;
- Decision/provider integrations accepted by prior increments;
- optional Legacy bridge only if an explicit transition requirement selects it.

Guardrail:
Legacy/MSSQL is not introduced by default.

### I24 — Production Deployment and Operational Hardening

Status: `planned after I23`.

Goal:
make the selected production topology supportable.

Expected scope:
- TLS;
- secret management;
- hardened PostgreSQL authentication;
- backup/restore and migration/upgrade procedure;
- metrics/monitoring/alerts;
- log retention/correlation;
- vulnerability/dependency/container hardening;
- disaster/recovery procedure;
- accepted workload/SLA/SLO envelope and performance validation;
- capacity/availability topology only from accepted evidence.

### I25 — Product Completion, Operator UX and Acceptance/Cutover

Status: `planned final integration increment`.

Goal:
close the remaining product-operability surface and prove the complete NAPMS chain.

Expected scope:
- role-appropriate workspaces for requirement owner, decision participant, security/network operator;
- dashboard only from real use-case/read models;
- mature search/filtering and bounded bulk operations where accepted;
- global explainability/audit navigation;
- export serializers such as CSV/XLSX only if a real consumer needs them;
- end-to-end acceptance from Connectivity Requirement through decision, Access Rule, realization, rendering, execution and post-check evidence;
- operational/runbook documentation;
- cutover/rollback criteria for the selected environment;
- explicit closure of remaining deferrals or documented exclusions.

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
  -> I23 Enterprise Identity / Sources
  -> I24 Production Hardening
  -> I25 Product Completion / Acceptance / Cutover
```

## Tracking rules

- Only the selected current increment gets a detailed `PLAN-*.md` under `docs/plans/active/`.
- This roadmap carries future ordering/status; it does not duplicate dynamic work-package state.
- When an increment completes, update this file in the same semantic stage:
  - mark it `done`;
  - record any accepted split/resequence;
  - promote the next selected increment.
- If a future increment becomes too large, split it before implementation and update the sequence here.
- Domain unknowns remain unknown until their owning canonical artifacts accept them.
- No future stage may be pulled forward merely to make a current implementation convenient.

## Product-completion criterion

For this roadmap, “product complete” means the selected target environment can demonstrate, with accepted semantics and operational evidence:

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

plus the production identity, deployment, recovery, observability and acceptance controls required for that selected environment.
