# Current target architecture

Status: `accepted current target through I27 Catalogue Curation for the supported local deployment`.

Date: 2026-09-10.

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

Non-peer application/read compositions include Requirement-to-Policy Alignment, policy export/snapshot normalization, Scoped Connectivity Inventory, Network Operator Realization View and Traffic Analysis Checker. Catalogue curation is not another bounded context: I27 adds write/read application seams inside ACC and RC and exposes them through outer adapters.

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

For I27 catalogue mutation the owning adapters select fixed administrative authority contexts:

```text
ACC -> CurateApplicationCatalogue @ application-catalogue
RC  -> CurateResourceCatalogue    @ resource-catalogue
```

The caller cannot replace these with a selected Responsibility Scope. Catalogue visibility, `ReadScopedConnectivity`, Resource Scope Affiliation and Resource Responsibility do not imply either curation permission.

## Catalogue Curation — I27

Feature boundary: `docs/architecture/catalogue-curation-boundary.md`.

I27 closes catalogue write capability inside the existing ACC/RC owners; it does not introduce a shared Catalogue aggregate/service.

```text
Web catalogue workspace
  -> authenticated task-oriented HTTP route
  -> ACC or RC application command/query
  -> catalogue-owned Authority admission port
  -> domain invariant
  -> owner-specific PostgreSQL UoW
```

### Owner boundaries

Application Communication Catalogue owns:

```text
Application
  -> Component
      -> Component Deployment
          -> temporal Deployment Resource Binding
          -> immutable DCS participation/revisions
```

Resource Catalogue owns:

```text
Resource
  -> temporal Endpoint/realization facts
  -> temporal Resource Scope Affiliation
  -> temporal Resource Responsibility/contact
```

The Web/API does not become a second catalogue owner.

### Cross-context binding

A Deployment Resource Binding is ACC-owned. ACC validates an RC Resource through a consuming projection port/adaptor. The command mutates only ACC state; it does not read/write RC tables directly and does not use a distributed ACC+RC transaction.

```text
ACC binding command
  -> DeploymentBindingResourceTargetPort
  -> RC-owned adapter/projection
  -> Active | Missing | Inactive | Unknown
```

Uncertainty fails closed.

### Identity, lifecycle and temporal history

Application, Component, Component Deployment and Resource have stable identities independent from presentation labels. Existing Deployment/DCS identities are preserved through migration.

Historical truth is not maintained through generic delete/update semantics:
- identity lifecycle uses explicit retirement;
- temporal realization/affiliation/responsibility/binding uses create/end/replace semantics;
- DCS revisions are immutable;
- creation provenance is preserved and later retirement/end provenance is recorded separately.

Optimistic `expectedVersion` and idempotent retry are separate controls. Durable command receipts prevent duplicate command effects; version checks prevent lost updates.

Known SQL failure before commit is distinct from an ambiguous commit acknowledgement.

### DCS authoring

The ACC application layer owns vendor-neutral communication authoring semantics. HTTP/Web never treats serialized projection bytes or vendor ACL syntax as the DCS domain model.

Normal UI selection of source/destination uses backend discovery of fully Active Application -> Component -> Deployment chains. NAPMS-owned relationships are not composed from manually pasted UUIDs in the ordinary workflow.

### External correlation references

NAPMS does not currently own a Responsibility Scope registry or Person/Team directory. ADR-011 therefore allows explicit local-first input of those external correlation references where no registry adapter exists. Such references do not create a new identity owner, Company/Organization aggregate or action authority.

### Read models

Owner-specific curation projections may optimize human workflows without duplicating authoritative state. In particular the Resources workspace read projection combines RC-owned current facts at one logical `asOf` to provide:
- effective Responsibility Scope filtering;
- search over Resource and current responsibility/contact presentation data;
- current realization/scope/responsibility/contact completeness indicators.

Those indicators are query projections, not Resource aggregate state.

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

## Network Operator Realization View — I25

The Realization workspace is a non-peer read composition. It owns no authoritative business state and preserves explicit stage availability. Missing evidence or operation history remains unavailable/unknown rather than fabricated success.

Feature contract: `docs/architecture/network-operator-realization-view.md`.

## Traffic Analysis Checker — I26

Checker remains a non-peer read composition from a technical tuple back toward domain and operational context:

```text
source/destination technical tuple + asOf
    -> RC reverse resolution
    -> ACC context
    -> Scoped Connectivity summaries
    -> unordered Network Context candidates
    -> stored Configured TAE matching
    -> Resource Responsibility/contact
```

No Checker aggregate/table is introduced. Ambiguity, partial data and missing evidence remain explicit; configured technical entries never imply `Allowed`.

## Cross-context application compositions

A composition consumes explicit owner/application ports, owns orchestration only, does not create copied business truth, and represents missing/ambiguous contributors explicitly.

This rule applies to Scoped Connectivity Inventory, Requirement-to-Policy Alignment, APR compositions, Network Operator Realization View, Traffic Analysis Checker and the ACC-to-RC validation seam used for Deployment Resource Binding.

Operational tooling may inspect/start/backup/restore the selected runtime but does not acquire semantic ownership of module data.

## Security/integrity guardrails

Architecture must preserve:
- exact proposal/Decision/Rule subject correlation;
- authoritative Rule uniqueness/idempotency;
- module-owned persistence boundaries;
- explicit logical-time validity where required;
- catalogue visibility/responsibility/scope affiliation separate from mutation authority;
- no caller-selected catalogue administrative authority scope;
- immutable DCS revisions and stable catalogue identities across migration;
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

Revisit topology or add infrastructure only when accepted evidence requires it, such as concrete external identity/catalogue-source synchronization, organization/stewardship hierarchy, fine-grained catalogue visibility, a real Cisco transport contract, calibrated path/telemetry evidence, durable NEO audit/rollback, measured workload/performance needs, independent availability/security constraints or an environment requiring public TLS/HA/external secret management.

## Canonical references

- semantic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- catalogue curation: `docs/architecture/catalogue-curation-boundary.md`, `docs/requirements/catalogue-curation.md`;
- Resource role/responsibility: `docs/domain/resource-role-model.md`;
- command/HTTP catalogue contracts: `docs/engineering/catalogue-curation-command-contract.md`, `docs/engineering/catalogue-curation-http-api-contract.md`;
- Network Context: `docs/architecture/network-context-candidate-boundary.md`;
- current runtime/product state: `docs/engineering/current-state.md`;
- local operator workflow: `docs/engineering/local-product-operator-runbook.md`;
- active work only: `docs/plans/active/README.md`.
