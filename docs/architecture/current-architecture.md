# Current target architecture

Status: `accepted current target through I19 plus I20 WP-0 Desired-vs-Configured Reconciliation and Enforcement Policy Derivation boundary`.

Date: 2026-09-09.

## Purpose

Define the cross-cutting architecture that current feature boundaries must preserve.

This file owns target structural/runtime constraints. Product behavior is owned by requirements; domain identity/ownership is owned by DDD; consequential architecture choices are owned by ADRs.

## Architecture drivers

Priority order:

1. semantic correctness of authoritative domain state, including idempotency/concurrency invariants;
2. coherent logical-time reads and fail-closed handling when required facts cannot be established;
3. end-to-end provenance/explainability;
4. explicit semantic ownership and action-scoped authority;
5. simplest reversible topology consistent with current evidence.

No accepted workload/SLA currently justifies service-per-context distribution or arbitrary numeric latency/availability targets.

## Structural style

NAPMS is a modular application with explicit semantic modules and ports/adapters.

```text
Domain
  <- Application / consuming ports
      <- Adapters / composition / runtime
```

Rules:
- Domain depends only on language/runtime primitives and domain code;
- Application depends inward on Domain and consumer-owned ports;
- adapters translate persistence, HTTP, external source and runtime mechanics;
- composition wires modules without becoming a semantic owner;
- framework/database/transport/configuration/logging/DI-container types do not enter Domain;
- constructor injection is the default; no service locator/global mutable dependency registry.

A Bounded Context is a semantic boundary, not automatically a service, database, team or deployment unit.

ADR-001 owns the selected modular-application decision.

## Semantic and persistence ownership

Each module owns access to its authoritative data and exposes application/port contracts to consumers.

A shared physical PostgreSQL instance may host several module-owned schemas/datasets. Physical colocation does not transfer semantic ownership.

Cross-module direct table reads/writes are prohibited when they bypass an owning application/port contract.

Persistence constraints enforce domain invariants but do not define their meaning.

Cross-context read compositions may correlate owner facts without creating copied peer business truth. Persist a composite read model only when measured workload/consistency evidence justifies it.

## Current semantic modules and compositions

Current first-class contexts include:
- Access Policy;
- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue;
- Connectivity Requirements;
- Connectivity Decision;
- Technical Access Evidence;
- Access Policy Realization;
- Network Enforcement Placement.

Current non-peer application/read compositions include:
- Requirement-to-Policy Alignment;
- policy export/snapshot normalization;
- Scoped Connectivity Inventory.

Scoped Connectivity Inventory is implemented as an owner-preserving application composition with Resource Scope Affiliation, `ReadScopedConnectivity`, module-owned adapters and no independent persistence.

I20 extends Access Policy Realization with the accepted managed-scope desired/configured reconciliation boundary. I21 rendering and I22 execution remain downstream. Runtime/deployment decomposition remains evidence-driven.

## Current runtime boundary

Implemented local/development topology:

```text
browser
  -> nginx / React Web UI
  -> FastAPI HTTP outer adapter
  -> framework-free application/domain modules
  -> module-owned PostgreSQL repositories
```

The normal local topology exposes one public nginx endpoint. PostgreSQL and FastAPI remain internal to the local Compose topology.

This is a development/runtime boundary, not a production deployment/SLA claim.

Web is an outer adapter. It presents backend-owned truth and must not create alternate authority, lifecycle or domain state.

## Authority and trust boundaries

Authenticated actor identity originates from the server/session boundary, not request payloads.

Application use cases evaluate action-specific Authority Management admission. Read authority and mutation authority remain independent.

Unknown/ambiguous required authority fails closed.

Client-side hidden/disabled controls are presentation only.

Business audit/provenance is authoritative business evidence; operational logging/correlation supports runtime diagnosis and does not replace it.

## Connectivity Decision

ADR-005 is current: Connectivity Decision is a first-class Bounded Context owning immutable final `Allowed | NotAllowed` Decisions, validity, reasons/evidence/provenance and supersession semantics.

ADR-003 is historical and superseded. The former external/deferred Decision seam is not current target architecture.

The implemented runtime persists Decision history in Decision-owned PostgreSQL storage. Selection is exact by RuleSemanticIdentity + governance scope + logical `asOf` and fails closed on absence, expiry, ambiguity or persistence uncertainty.

Access Policy consumes a consumer-owned effective Decision projection and continues to own Access Rule identity/state. Decision expiry or supersession does not silently mutate an existing Access Rule.

Scoped Connectivity consumes only the accepted coarse `Allowed | NotAllowed | NoFinalDecision | Unknown` Decision summary. Detailed reason/evidence/provenance remains behind independent `ReadConnectivityDecision` authority.

Normal local composition uses the durable Decision runtime; no deterministic allow adapter is selected by the product journey.

## Technical Access Evidence

Technical Access Evidence is a first-class bounded context owning immutable source-qualified technical evidence, not authorization or realization truth.

The implemented I17 boundary is:

```text
strict source/import adapter
  -> source-neutral RecordEvidenceSet
  -> framework-free TAE Application/Domain
  -> TAE-owned PostgreSQL repository/schema
```

Architecture rules:
- TAE Domain/Application imports no peer bounded context and no infrastructure framework;
- one Evidence Set represents one immutable source capture/import episode;
- source + capture reference is retry/idempotency identity;
- source evidence time is distinct from NAPMS RecordedAt;
- duplicate source entries remain evidence and are not content-deduplicated;
- persistence is append-only and fails closed on corrupt/uncertain state;
- source-specific syntax/parser/provider mechanics remain adapters;
- no current/fresh winner, authorization, domain interaction mapping, enforcement placement or desired-vs-configured reconciliation is computed by TAE;
- the first local JSON import path is trusted composition plumbing, not a public human API or Authority Management workflow;
- TAE uses a dedicated PostgreSQL composition scope so ordinary HTTP requests do not allocate an unused TAE connection;
- strict local JSON parsing rejects duplicate object fields and unsupported fields rather than accepting ambiguous last-write-wins source syntax.

Access Policy Realization consumes TAE in I18 through a consumer-owned projection/port; TAE does not depend on that consumer.

## Network Enforcement Placement

The implemented I19 boundary is a first-class NEP module with framework-free Domain/Application/Ports and outer source/persistence adapters.

First-slice architecture:

```text
provider/network path source
    -> strict outer adapter
    -> NEP-owned normalized forwarding/path + correspondence + attachment facts
    -> NEP-owned PostgreSQL
    -> SelectEnforcement(exact source/destination pair, asOf)
```

Architecture rules:
- NEP Domain/Application import no peer bounded context;
- Logical Firewall identity is independent from provider/device realization and Resource identity;
- provider/path references are opaque normalized correspondence/provenance values;
- one complete path or positive no-route fact is required for a complete first-slice result;
- unsupported forwarding dimensions or multipath fail closed as `Unknown`;
- an Enforcement Attachment supports placement only with a matching effective Logical Firewall/provider correspondence;
- no cross-context SQL;
- no I20 desired-vs-configured semantics, vendor rendering or execution enter I19.

APR may consume NEP later through an APR-owned projection/port. NEP must not depend on APR to make that consumer work.

## Access Policy Realization — I20 derivation/reconciliation

The accepted first I20 boundary remains framework-free APR Domain/Application with outer owner adapters.

```text
effective Access Policy + RC/ACC
    -> APR-owned desired technical projection
    -> shared I18 domain-resolution quality check
    -> NEP placement projection
    -> Desired Enforcement Intent by Logical Firewall + Enforcement Attachment

explicit TAE Configured Evidence Set
    + trusted same-managed-scope/source contract
    -> source-specific effective-Permit projection
    -> shared I18 configured-domain attribution
    -> Configured Enforcement Snapshot

desired vs configured
    -> exact common/missing/extra
    -> Satisfied | Drift | Ambiguous | Unknown
    -> No-op | Add | Remove | Replace only when complete
```

Architecture rules:
- one explicit `asOf`; first complete configured slice requires `EvidenceTime.Instant == asOf`;
- TAE does not become a current/complete-policy service;
- configured completeness and target/policy-partition equivalence come from an explicit consumer/source contract;
- Enforcement Target preserves Logical Firewall + Enforcement Attachment granularity;
- raw vendor Block/order/default/zone semantics are interpreted only by source-specific outer adapters capable of producing exact effective Permit regions;
- I18 correspondence algebra is reused unchanged;
- desired/configured reconciliation remains derived on demand with no APR persistence requirement;
- I21 owns rendering and I22 owns device/provider operations.

Feature contract: `docs/architecture/access-policy-realization-reconciliation-boundary.md`.

## Coherent policy export

ADR-002 owns the logical export snapshot consistency boundary.

For one export `asOf`, the application must establish complete correlated Access Policy, ACC and Resource Catalogue facts before normalization succeeds.

The architecture does not require one global database transaction across all semantic owners. Source-specific adapters may use temporal queries, version tokens, immutable captures or equivalent evidence-preserving mechanisms.

Best-effort incomplete data is not a successful normalized export.

## Cross-context application compositions

A composition:
- consumes explicit owner/application ports;
- owns orchestration/query semantics only;
- does not create copied business truth or a new lifecycle by convenience;
- uses one explicit logical time when correlating temporal facts;
- represents missing/ambiguous contributors explicitly rather than converting uncertainty into false absence.

Requirement-to-Policy Alignment, policy export and Scoped Connectivity Inventory follow this pattern.

## Transition and external sources

Legacy/MSSQL, Word/Excel request structures, vendor rendering and provider/device execution are not target semantic dependencies by default.

If a selected integration requires a legacy/enterprise source:
- adapt it at the infrastructure boundary;
- preserve source/provenance;
- fail closed when target-required identity/validity cannot be established;
- keep a concrete retirement/replacement trigger.

Do not let a transition schema redefine target domain identity or ownership.

## Security/integrity guardrails

Architecture must preserve:
- exact proposal/Decision/Rule subject correlation;
- authoritative Rule uniqueness/idempotency;
- module-owned persistence boundaries;
- trusted catalogue/source correlation;
- explicit logical-time validity where required;
- no silent semantic broadening/narrowing in normalization;
- no protected business-detail leakage through a broader catalogue/read composition;
- explicit degraded/error outcomes instead of convenient permission or absence.

## Revisit triggers

Revisit topology or add infrastructure only when accepted evidence requires it, such as:
- independent scale/release/security/trust/availability constraints;
- concrete source integration mechanics;
- measured read-model performance needs;
- production identity/deployment requirements;
- later roadmap execution/rendering/realization semantics.

Do not add distribution or generic platforms merely to anticipate future complexity.

## Canonical references

- semantic ownership: `docs/domain/semantic-ownership.md`;
- Access Policy tactical model: `docs/domain/access-policy/tactical-model.md`;
- current product requirements: `docs/requirements/`;
- feature architecture: `docs/architecture/`;
- ADRs: `docs/decisions/`;
- runtime/engineering state: `docs/engineering/current-state.md`;
- current execution only: `docs/plans/active/README.md`.
