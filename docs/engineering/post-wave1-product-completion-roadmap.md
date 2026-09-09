# Post-Wave-1 product completion roadmap

Status: `accepted ordered sequencing baseline after I13`.

Date: 2026-09-09.

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
- I1-I13;
- Wave 1 proposal -> Connectivity Decision seam -> Access Rule -> effective desired policy -> coherent normalized policy;
- PostgreSQL persistence;
- Web/HTTP runtime;
- Dockerized local runtime;
- human-readable catalogue UX.

Wave 1 intentionally stopped before Connectivity Requirements runtime participation; I13 now closes the first Connectivity Requirements core/runtime/workspace slice.

Still deferred:
- Requirement-to-Policy Alignment;
- Connectivity Decision internals/workflow;
- Network Enforcement Placement;
- Technical Access Evidence;
- Access Policy Realization/reconciliation;
- vendor rendering;
- device/provider execution;
- production identity/deployment/integration.

## Ordered increments

### I13 — Connectivity Requirements Core

Status: `done`.

Goal:
establish the Tactical DDD and first executable core for the already-accepted **Connectivity Requirements** bounded context.

Must establish before infrastructure:
- exact ConnectivityRequirement identity;
- RequiredSemanticInteraction representation;
- Dependent/reference semantics;
- applicability and temporal semantics;
- justification/provenance;
- create/change/retire lifecycle;
- authority actions for declaring/reading/changing requirements;
- invariant that `Required != Authorized`.

Exit direction:
an authorized responsible actor can persist and inspect a connectivity need without creating, allowing or changing an Access Rule.

Detailed execution was completed and absorbed into canonical truth; the active I13 plan is removed after merge.

### I14 — Requirement-to-Policy Alignment

Status: `next after I13`.

Goal:
compare accepted Connectivity Requirements with current Access Policy without making either context own the other.

Expected outcomes:
- requirement is covered by current authorized/effective policy;
- requirement is not covered;
- policy exists without a corresponding current requirement where the selected view needs to expose that fact;
- exact correlation/evidence remains explainable.

Guardrails:
- `Required != Authorized`;
- alignment is composition, not a new peer semantic owner unless evidence later proves otherwise;
- no Connectivity Decision workflow is invented here.

Primary product surface:
owner/responsible-user view showing each declared need and its current policy-coverage state.

### I15 — Connectivity Decision Domain Closure

Status: `planned after I14`.

Goal:
promote the currently deferred Connectivity Decision research only when Requirement and current-policy semantics are concrete enough to answer why/how a proposal becomes `Allowed | NotAllowed`.

Must resolve:
- semantic owner/bounded-context disposition;
- decision identity and subject;
- reasons/policies/facts used;
- human/automatic/mixed mechanism;
- participating roles and Authority actions;
- SoD/quorum if actually required;
- decision validity/effective time;
- reconsideration/supersession;
- reason/provenance model;
- exact relationship to Connectivity Requirement and Access Rule Proposal.

Exit:
accepted Strategic/Tactical DDD + requirements + ADR/architecture contract for a durable non-local Decision provider.

### I16 — Connectivity Decision Runtime and Workflow

Status: `planned after I15`.

Goal:
replace the `local-dev:allowed` provider with the accepted real Decision-domain application/runtime slice.

Expected scope:
- submit/obtain decision for exact proposal subject;
- decision work queue only if I15 accepts one;
- Allowed/NotAllowed reason/provenance presentation;
- authorized actor/action boundaries;
- idempotency/concurrency/audit;
- Web UI for decision participants where applicable;
- Docker demo using the real accepted decision mechanism.

Exit:
no local deterministic allow adapter is required for the normal product journey.

### I17 — Technical Access Evidence Core

Status: `planned after Decision runtime`.

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

Status: `planned after I17`.

Goal:
implement the shared resolution capability inside **Access Policy Realization**.

Expected semantics:
- map one normalized Technical Access Predicate against RC + ACC + effective time;
- exact/coverage/partial/ambiguous/unresolved outcomes as accepted by Tactical DDD;
- same resolution semantics for proposal/reconciliation consumers;
- preserve unresolved technical remainder and provenance.

Exit:
technical evidence can be explained in domain interaction terms without consumer-specific meaning.

### I19 — Network Enforcement Placement

Status: `planned after I18`.

Goal:
implement the **Network Enforcement Placement** context needed to answer where traffic is actually subject to enforcement.

Must establish:
- normalized forwarding/path knowledge;
- Logical Firewall identity/correspondence;
- Enforcement Selection;
- Enforcement Attachment;
- temporal/provider-realization relationships;
- separation of Logical Firewall from provider/device identity.

Exit:
NAPMS can derive/explain enforcement placement for domain traffic without embedding vendor syntax.

### I20 — Desired-vs-Configured Reconciliation and Enforcement Policy Derivation

Status: `planned after I19`.

Goal:
complete the central **Access Policy Realization** outcome.

Expected outcomes:
- derive the business-correct/preferred enforcement policy from desired Access Policy + placement;
- compare desired realization against Technical Access Evidence;
- classify semantic delta such as add/remove/replace/no-op only after Tactical DDD accepts the exact algebra;
- expose extra/missing/partial/ambiguous configured access;
- preserve exact domain/evidence/placement provenance.

Exit:
NAPMS can truthfully answer whether configured enforcement realizes desired policy and what semantic delta remains.

### I21 — Configuration Rendering

Status: `planned after I20`.

Goal:
translate accepted vendor-neutral enforcement intent into target-specific configuration representation.

Guardrails:
- rendering is downstream of normalized/realization semantics;
- renderer must not broaden/narrow desired traffic;
- target grouping/order/objects are technical representation, not Access Rule identity;
- target-specific disable/remove/recreate mechanics are introduced only here when required.

Expected deliverables:
- renderer port/contracts;
- at least one concrete target/vendor adapter selected by product need;
- rendered-artifact provenance;
- semantics-equivalence tests.

### I22 — Network Environment Operations

Status: `planned after I21`.

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
  -> I16 Connectivity Decision Runtime
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
