# Current target architecture

Status: `accepted current target through I31 Application Catalogue migration for the supported local deployment`.

Date: 2026-09-11.

## Purpose

Define the cross-cutting architecture current feature boundaries must preserve. Product behavior is owned by requirements; domain identity/ownership by DDD; feature-specific architecture by the corresponding boundary artifact/ADR.

## Architecture drivers

Priority order:
1. semantic correctness of authoritative domain state, including idempotency/concurrency invariants;
2. coherent logical-time reads and fail-closed handling;
3. end-to-end provenance/explainability;
4. explicit semantic ownership and action-scoped authority;
5. simplest reversible topology consistent with current evidence.

No accepted workload/SLA justifies service-per-context distribution or a multi-node topology.

## Structural style

NAPMS remains a modular application with explicit semantic modules and ports/adapters.

```text
Domain
  <- Application / consuming ports
      <- Adapters / composition / runtime
```

Rules:
- Domain depends only on language/runtime primitives and its own domain code;
- Application depends inward on Domain and consumer-owned ports;
- adapters translate persistence, HTTP, external-source, target-transport and runtime mechanics;
- composition wires modules without becoming a semantic owner;
- framework/database/transport/config/logging/DI-container types do not enter Domain;
- constructor injection is the default; no service locator/global mutable dependency registry.

A Bounded Context is a semantic boundary, not automatically a service, database, team or deployment unit.

## Semantic and persistence ownership

Each module owns its authoritative data and exposes application/port contracts to consumers. Cross-module direct table reads/writes are prohibited when they bypass owning contracts. Physical PostgreSQL colocation does not transfer semantic ownership.

Current first-class semantic modules include:
- Access Policy;
- Authority Management;
- Application Communication Catalogue;
- Resource Catalogue;
- Connectivity Requirements;
- Connectivity Decision;
- Technical Access Evidence;
- Access Policy Realization;
- Network Enforcement Placement;
- Network Environment Operations.

Non-peer application/read compositions include Requirement-to-Policy Alignment, policy export/snapshot normalization, Scoped Connectivity Inventory, Network Operator Realization View and Traffic Analysis Checker. I31 changes the ACC authoring/read model inside the existing bounded context; it does not introduce another bounded context.

## Current runtime boundary

Supported local topology:

```text
browser
  -> 127.0.0.1 published nginx / React Web UI
  -> FastAPI HTTP outer adapter
  -> framework-free application/domain modules
  -> module-owned PostgreSQL repositories
```

Local username/password authentication with server-side sessions remains the primary path. Authority/ACC/Resource state is locally owned. No external IdP, directory, CMDB, catalogue or MSSQL dependency is required.

Only nginx/Web is host-published in the supported Compose topology. API and PostgreSQL remain internal. PostgreSQL host access uses password authentication; fresh volumes use SCRAM-SHA-256. Startup credential preparation/rotation, health probes, backup/restore, migrations and container hardening remain outer operational concerns.

## Authority and trust boundaries

Authenticated actor identity originates from the server/session boundary, not request payloads. Application use cases evaluate action-specific Authority Management admission. Read and mutation authority remain independent; unknown/ambiguous required authority fails closed.

Authentication identity does not grant business authority. Resource responsibility/contact facts and Resource Scope Affiliation are also not authority facts.

Catalogue mutation uses fixed server-selected administrative authority contexts:

```text
ACC -> CurateApplicationCatalogue @ application-catalogue
RC  -> CurateResourceCatalogue    @ resource-catalogue
```

The caller cannot replace these with a selected Responsibility Scope. Catalogue visibility, `ReadScopedConnectivity`, Resource Scope Affiliation and Resource Responsibility do not imply either curation permission.

## Application Communication Catalogue — I31

Canonical domain model: `docs/domain/application-communication-catalogue/tactical-model.md`.
Feature boundary: `docs/architecture/application-catalogue-target-boundary.md`.

The current ACC authoring model is:

```text
Application Definition
  -> Component
  -> Interaction Definition

Application Deployment
  -> Application Definition
  -> Company / Environment / Scope context
  -> selected Deployment Interaction
      -> interaction-scoped Source Resource set
      -> interaction-scoped Destination Resource set
      -> internal compatibility projection
```

Application Definition reuses the stable Application identity. Application Deployment and Deployment Interaction are first-class current identities. Company, Environment and Scope are context/correlation values; they do not define identity or authority.

Interaction Definition owns current reusable vendor-neutral traffic intent. Deployment Interaction selects that Definition without endpoint/traffic override. Resource membership belongs to one Deployment Interaction side, so the same Component may resolve to different Resource sets in different interactions.

### Downstream compatibility boundary

Existing downstream contexts keep their semantic identity shape:

```text
sourceComponentDeploymentId
destinationComponentDeploymentId
dcsContractRevisionId
```

Each Deployment Interaction has stable internal compatibility Component Deployment identities for Source and Destination plus a current immutable DCS revision. ACC adapters expose the resulting `DirectedInteractionIdentity` to Connectivity Requirements, Connectivity Decision and Access Policy without importing target ACC domain types into those contexts.

Compatibility identities are backend implementation identities. Current Product API/Web authoring does not require users to understand or assemble them.

A permitted Interaction Definition traffic edit creates replacement immutable DCS snapshots for all Active Deployment Interactions selecting it. Previous DCS revisions and historical downstream references are preserved. Active/effective Requirement, final/effective Decision or active/effective Rule dependencies block unsafe traffic edits and relevant retirements through explicit dependency ports.

### Resource binding and read composition

Current authoring addresses Resource membership by:

```text
deploymentInteractionId + side + resourceReference
```

ACC validates Resource state through Resource Catalogue-owned contracts. The compatibility persistence adapter realizes current membership through the stable compatibility side required by existing downstream Resource resolution.

Deployment Resource-set read models may combine ACC membership with RC display/scope facts at one explicit `asOf`. This is query-only composition with server paging/search/filter/sort; it transfers no mutation or lifecycle ownership.

### Lifecycle and legacy truth

Application Definition, Component, Interaction Definition, Application Deployment and Deployment Interaction use terminal `Active -> Retired` lifecycle. Retirement is non-cascading and blocked by active dependants/references. Normal product hard delete is absent.

Existing pre-I31 Component Deployments, DCS revisions and Deployment Resource Bindings remain valid historical/legacy ACC truth. They are not automatically synthesized into Application Deployments because required Company/Environment/Scope and interaction ownership cannot be inferred safely.

## Resource Catalogue — I27 retained boundary

Resource Catalogue continues to own:

```text
Resource
  -> temporal Endpoint/realization facts
  -> temporal Resource Scope Affiliation
  -> temporal Resource Responsibility/contact
```

Resources workspace and owner-specific command/query seams remain as implemented by I27. Resource responsibility/contact and scope affiliation remain separate from mutation authority.

## Technical Access Evidence

TAE owns immutable source-qualified technical evidence, not authorization or realization truth. Source-specific parsing/collection remains adapters. APR and Traffic Analysis consume TAE through consumer-owned projections.

Configured data presented by Checker is stored TAE evidence. Checker never performs a synchronous live firewall/device read and never promotes configured evidence to authorization truth.

## Network Enforcement Placement / Network Context

NEP owns Logical Firewall identity, temporal provider correspondence, Enforcement Attachment semantics and stronger forwarding/placement knowledge where available.

A proven `ForwardingPath` is stronger than the baseline unordered Network Context candidate set. Candidate membership may be incomplete/false-positive and is not proof of traversal, order, authorization or configured state.

Feature boundary: `docs/architecture/network-context-candidate-boundary.md`.

## Access Policy Realization / Network Environment Operations

APR remains framework-free and owner-preserving:

```text
effective Access Policy + RC/ACC + NEP
    -> Desired Enforcement Policy
configured TAE + managed-scope contract
    -> Configured Enforcement Snapshot
    -> reconciliation
Desired Enforcement Policy
    -> target renderer
    -> Rendered | Unsupported | Unknown
```

Rendered configuration does not prove application to a target.

NEO remains a separate downstream boundary:

```text
Rendered Configuration
    -> operation authority
    -> acquire target revision
    -> conditional apply
    -> post-state verification
    -> Verified | PreconditionFailed | Rejected | Drift | Unknown
```

The supported target remains deterministic in-process/stub-first. Real Cisco transport, production credentials/rollback and durable operation audit require later concrete environment evidence.

## Read compositions

Scoped Connectivity Inventory, Network Operator Realization View and Traffic Analysis Checker remain non-peer read/application compositions. A composition consumes explicit owner/application ports, owns orchestration only, does not create copied business truth, and represents missing/ambiguous contributors explicitly.

Traffic Analysis continues to resolve a technical tuple through RC, ACC context, scoped Connectivity summaries, unordered Network Context candidates, stored TAE evidence and Resource responsibility/contact. Configured evidence never implies `Allowed`.

## Security/integrity guardrails

Architecture must preserve:
- exact proposal/Decision/Rule subject correlation;
- authoritative Rule uniqueness/idempotency;
- module-owned persistence boundaries;
- explicit logical-time validity where required;
- catalogue visibility/responsibility/scope affiliation separate from mutation authority;
- no caller-selected catalogue administrative authority scope;
- stable Application/Component identities and immutable historical DCS/downstream references across I31;
- compatibility Component Deployment/DCS IDs remain internal to the ACC compatibility boundary;
- interaction-scoped Resource membership is not widened into global Component-to-Resource identity;
- no destructive catalogue maintenance that erases referenced historical truth;
- no silent semantic broadening/narrowing in normalization/rendering;
- no false Verified outcome from transport acceptance alone;
- operation idempotency and optimistic concurrency for mutation;
- authentication identity separate from business authority;
- explicit degraded/error outcomes instead of convenient permission, absence or success;
- no PostgreSQL network trust in the supported local Compose path;
- startup/status probes do not mutate business state;
- missing/ambiguous evidence never becomes success;
- Network Context candidates never become fabricated path/order facts;
- Web dependency changes keep package intent and lockfile consistent.

## Revisit triggers

Revisit topology or add infrastructure only when accepted evidence requires it, such as concrete external identity/catalogue-source synchronization, organization/stewardship hierarchy, fine-grained catalogue visibility, Application Definition versioning/overrides, a real Cisco transport contract, calibrated path/telemetry evidence, durable NEO audit/rollback, measured workload/performance needs, independent availability/security constraints or an environment requiring public TLS/HA/external secret management.

## Canonical references

- ACC Tactical DDD: `docs/domain/application-communication-catalogue/tactical-model.md`;
- Application Catalogue product/architecture: `docs/requirements/application-catalogue-target.md`, `docs/architecture/application-catalogue-target-boundary.md`;
- Application Catalogue decisions: `docs/decisions/ADR-012-application-definition-deployment-model.md`, `docs/decisions/ADR-013-i31-application-catalogue-compatibility-and-reference-semantics.md`;
- Resource catalogue curation: `docs/architecture/catalogue-curation-boundary.md`, `docs/requirements/catalogue-curation.md`;
- semantic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- Resource role/responsibility: `docs/domain/resource-role-model.md`;
- Network Context: `docs/architecture/network-context-candidate-boundary.md`;
- current runtime/product state: `docs/engineering/current-state.md`;
- local operator workflow: `docs/engineering/local-product-operator-runbook.md`;
- active work only: `docs/plans/active/README.md`.
