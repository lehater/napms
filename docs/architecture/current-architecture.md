# Current target architecture

Status: `accepted current target through I26 Traffic Analysis Checker for the supported local deployment`.

Date: 2026-09-10.

## Purpose

Define the cross-cutting architecture that current feature boundaries must preserve. Product behavior is owned by requirements; domain identity/ownership is owned by DDD; consequential choices are owned by ADRs.

## Architecture drivers

Priority order:
1. semantic correctness of authoritative domain state, including idempotency/concurrency invariants;
2. coherent logical-time reads and fail-closed handling;
3. end-to-end provenance/explainability;
4. explicit semantic ownership and action-scoped authority;
5. simplest reversible topology consistent with current evidence.

No accepted workload/SLA currently justifies service-per-context distribution or a multi-node topology.

## Structural style

NAPMS is a modular application with explicit semantic modules and ports/adapters.

```text
Domain
  <- Application / consuming ports
      <- Adapters / composition / runtime
```

Rules:
- Domain depends only on language/runtime primitives and its own domain code;
- Application depends inward on Domain and consumer-owned ports;
- adapters translate persistence, HTTP, external source, target transport and runtime mechanics;
- composition wires modules without becoming a semantic owner;
- framework/database/transport/configuration/logging/DI-container types do not enter Domain;
- constructor injection is the default; no service locator/global mutable dependency registry.

A Bounded Context is a semantic boundary, not automatically a service, database, team or deployment unit.

## Semantic and persistence ownership

Each module owns access to its authoritative data and exposes application/port contracts to consumers. Cross-module direct table reads/writes are prohibited when they bypass owning contracts. Physical PostgreSQL colocation does not transfer semantic ownership.

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

Current non-peer application/read compositions include Requirement-to-Policy Alignment, policy export/snapshot normalization, Scoped Connectivity Inventory, Network Operator Realization View and I26 Traffic Analysis Checker.

I20 implements APR managed-scope desired/configured reconciliation. I21 adds target-specific rendering inside APR. I22 adds a separate downstream Network Environment Operations boundary for operation identity, authority admission, concurrency, mutation outcomes and verification. I23 adds only a dormant source-neutral external identity/source extension seam while preserving local-first runtime behavior. I24 hardens the selected local deployment/operations boundary. I25 closes the supported-local product chain with executable full-chain acceptance plus an owner-preserving operator read composition and Web explainability journey. I26 adds the reverse technical-entry-point analysis composition without introducing another source of domain truth.

## Current runtime boundary

Implemented local topology:

```text
browser
  -> 127.0.0.1 published nginx / React Web UI
  -> FastAPI HTTP outer adapter
  -> framework-free application/domain modules
  -> module-owned PostgreSQL repositories
```

Local username/password authentication with server-side sessions is the primary supported authentication path. Authority/ACC/Resource data remain locally owned and populated for the current product. No external IdP, directory, CMDB, catalogue or MSSQL dependency is required for normal operation.

Only nginx/Web is host-published by the supported Compose topology. API and PostgreSQL remain internal to the Compose network.

PostgreSQL host access is password-authenticated; fresh local volumes initialize host authentication with SCRAM-SHA-256. The supported startup path prepares an ephemeral database credential, rotates the local role before dependent services start, and verifies that incorrect credentials are rejected. Credential preparation is an outer operational concern, not an application/domain responsibility.

The supported local startup probe is intentionally non-mutating. A separate fresh-volume CI journey exercises state-changing product behavior. Local backup/recovery uses validated PostgreSQL custom-format logical backup plus explicit destructive clean-volume restore, then normal migration/startup. Failed forward upgrades recover from pre-upgrade backup and matching application revision; arbitrary reverse migrations are not promised.

Runtime diagnostics use structured logs, `/health/live`, PostgreSQL-backed `/health/ready`, Compose state and an explicit PostgreSQL query probe. A separate metrics platform is not part of the selected local architecture because no accepted requirement demands one.

Backend application containers remain non-root and NAPMS backend/Web Compose services use init/reaping plus `no-new-privileges`. PostgreSQL keeps the official image entrypoint/privilege model. Web dependency resolution is repository-owned through `web/package-lock.json`; supported CI and Docker build paths use `npm ci`.

## Authority and trust boundaries

Authenticated actor identity originates from the server/session boundary, not request payloads. Application use cases evaluate action-specific Authority Management admission. Read authority and mutation authority remain independent. Unknown/ambiguous required authority fails closed.

Authentication identity does not grant business authority. Authority Management remains the owner of application permission. Resource responsibility/contact facts are also not authority facts.

A dormant optional external-authentication seam may provide a verified provider-qualified external subject to an `ActorIdentityResolver`, which resolves only to `Mapped | Unmapped | Ambiguous | Unknown`; only `Mapped` exposes a NAPMS actor. This seam is not wired as the default login path.

## Technical Access Evidence

TAE owns immutable source-qualified technical evidence, not authorization or realization truth. Source-specific parsing/collection remains adapters. APR and Traffic Analysis consume TAE through consumer-owned projections; TAE does not depend on either consumer.

Configured data presented by Checker is always stored TAE evidence. Checker never performs a synchronous live firewall/device read and never promotes configured evidence to authorization truth.

## Network Enforcement Placement / Network Context

NEP owns Logical Firewall identity, temporal provider correspondence, Enforcement Attachment semantics and stronger forwarding/placement knowledge when such knowledge is actually available.

I26 establishes an important distinction:

```text
proven ForwardingPath capability
!=
baseline Network Context candidate set
```

A baseline Network Context result is an unordered set of relevant enforcement/device candidates. It may be incomplete and may contain false positives. Candidate membership is not proof of traversal, order, authorization or configured state. Source relevance, provenance and knowledge gaps must remain visible. A proven ordered path may still exist as a stronger optional capability only where a contributing source can actually prove it.

Feature boundary: `docs/architecture/network-context-candidate-boundary.md`.

## Resource Catalogue responsibility facts

Resource Catalogue owns Resource identity, endpoint/realization history, Resource Scope Affiliation and I26 Resource Responsibility facts used for owner/support contact discovery.

Resource Responsibility is temporal and may reference a person or team in roles such as service owner, technical owner, operations/support contact or business owner. These facts are independent from Authority Management Responsibility Assignments and do not grant NAPMS action permission.

## Access Policy Realization — I18/I20/I21

APR remains framework-free Domain/Application with APR-owned ports and outer owner-preserving/vendor adapters.

```text
effective Access Policy + RC/ACC + NEP
    -> Desired Enforcement Policy

configured TAE + trusted managed-scope contract
    -> Configured Enforcement Snapshot
    -> Policy Reconciliation

Desired Enforcement Policy
    -> RenderConfiguration
    -> ConfigurationRenderer port
    -> Cisco ASA outer adapter
    -> Rendered | Unsupported | Unknown
```

Rendering remains derived on demand and does not prove provider/device application.

## Network Environment Operations — I22

```text
APR Rendered Configuration
    -> composition projects EnforcementTarget identity
    -> NEO OperationTarget
    -> mutation-authority admission
    -> acquire current target revision
    -> conditional apply
    -> reacquire post-state
    -> Verified | PreconditionFailed | Rejected | Drift | Unknown
```

NEO owns operation identity/outcome/concurrency/provenance, not desired policy, placement or rendering semantics. The current adapter is a deterministic in-process target stub because no real Cisco lab is available. Stub success proves orchestration semantics only; real transport, credential handling, production rollback and durable operation persistence require later concrete environment evidence.

Feature contract: `docs/architecture/network-environment-operations-boundary.md`.

## Network Operator Realization View — I25

I25 provides a non-peer, read-only application composition for network/security operator inspection. It owns no authoritative business state.

```text
server-authenticated actor + scope + asOf
    -> ReadNetworkOperatorRealization authority admission
    -> owner-preserving APR / NEP / TAE / NEO projections
    -> stage availability + references/artifacts/evidence
    -> HTTP transport DTO
    -> Realization Web workspace
```

Missing configured-evidence/managed-scope input or actual NEO operation result remains `NotAvailable`; ambiguous/incomplete semantic input remains `Unknown`. Cross-chain explainability follows existing Rule -> Decision -> Connectivity Requirement owner pages.

Feature contract: `docs/architecture/network-operator-realization-view.md`.

## Traffic Analysis Checker — I26

I26 adds a second non-peer application/read composition, oriented from a technical traffic tuple back toward domain and operational context.

```text
source address + destination address + protocol + port/range + asOf
    -> Resource Catalogue reverse address resolution
    -> ACC resource/component/DCS context
    -> existing Scoped Connectivity Inventory policy summaries
    -> Network Context unordered candidates
    -> per-candidate stored Configured TAE snapshot matching
    -> Resource Responsibility/contact projection
    -> authenticated HTTP DTO
    -> Checker Web workspace
```

Architecture rules:
- Traffic Analysis owns orchestration/read DTOs only; no Checker aggregate/table is introduced;
- IP resolution preserves `Resolved | Ambiguous | Historical | Unknown` and may retain several candidate Resources;
- policy composition reuses owner-preserving reads and preserves multiple/partial/unknown matches;
- Web does not implement independent traffic predicate algebra;
- technical matching is backend-owned and distinguishes exact/containment/overlap/no-match for supported predicates;
- Network Context candidates are unordered and cannot be rendered as a proven `A -> B -> C` path;
- each candidate may have an applicable stored evidence snapshot or explicit missing-evidence state;
- snapshot `capturedAt`, `recordedAt`, source and provenance are carried independently of analysis time;
- no absence of evidence is promoted into proof that a device/rule/path does not exist;
- configured technical entries remain evidence and never imply `Allowed`;
- ownership/support contacts are Resource Catalogue responsibility facts, not authorization;
- the supported local target uses deterministic Network Context and responsibility adapters and stored PostgreSQL TAE; no live Cisco/provider transport is required.

Observable contract: `docs/requirements/traffic-analysis-checker.md`.

## I25 full-chain acceptance composition

The PostgreSQL acceptance suite composes existing owner APIs/repositories to prove Requirement -> Decision -> Access Rule -> NEP/TAE/APR -> deterministic NEO -> `Verified`. This remains executable acceptance evidence, not a new aggregate and not a claim that every runtime installation always has configured inputs or operation history.

## Cross-context application compositions

A composition consumes explicit owner/application ports, owns orchestration only, does not create copied business truth, and represents missing/ambiguous contributors explicitly. APR EnforcementTarget -> NEO OperationTarget mapping, Scoped Connectivity Inventory, Network Operator Realization View and Traffic Analysis Checker follow this rule.

Operational tooling may inspect/start/backup/restore the selected local runtime but does not acquire semantic ownership of module data. Database backup/restore preserves storage state as a whole; it is not a cross-context business API.

## Optional external extensions — I23

External identity and source integrations are optional future extensions, not current target dependencies. Future adapters terminate at source-neutral/context-owned boundaries. Deterministic stubs are sufficient to prove dormant seams. Legacy/MSSQL and real provider/device transport are not target dependencies by default.

## Security/integrity guardrails

Architecture must preserve:
- exact proposal/Decision/Rule subject correlation;
- authoritative Rule uniqueness/idempotency;
- module-owned persistence boundaries;
- explicit logical-time validity where required;
- no silent semantic broadening/narrowing in normalization or rendering;
- no false Verified outcome from transport acceptance alone;
- operation idempotency and optimistic concurrency for mutation;
- authentication identity separate from business authority;
- resource responsibility/contact separate from business authority;
- explicit degraded/error outcomes instead of convenient permission, absence or success;
- no PostgreSQL network trust in the supported local Compose path;
- operational startup/status probes do not mutate business state;
- destructive local recovery requires explicit operator intent and a validated backup artifact;
- realization and Traffic Analysis read models never promote missing/ambiguous owner evidence to success;
- Network Context candidates never become fabricated path/order facts;
- Web dependency changes keep package intent and lockfile consistent.

## Revisit triggers

Revisit topology or add infrastructure only when accepted evidence requires it, such as a concrete external identity/source requirement, a real Cisco lab/transport contract, calibrated path/telemetry evidence, durable NEO audit/rollback, measured workload/performance needs, independent scale/security/availability constraints, or a target environment requiring public TLS/HA/external secret management.

## Canonical references

- semantic ownership: `docs/domain/strategic-model.md`, `docs/domain/semantic-ownership.md`;
- Resource role/responsibility model: `docs/domain/resource-role-model.md`;
- current product requirements: `docs/requirements/`;
- feature architecture: `docs/architecture/`;
- runtime/product state: `docs/engineering/current-state.md`;
- local operator workflow: `docs/engineering/local-product-operator-runbook.md`;
- current execution only: `docs/plans/active/README.md`.
