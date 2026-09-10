# Current target architecture

Status: `accepted current target through I25 product completion for the supported local deployment`.

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

## Current semantic modules and compositions

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

Current non-peer application/read compositions include Requirement-to-Policy Alignment, policy export/snapshot normalization, Scoped Connectivity Inventory and the I25 Network Operator Realization View.

I20 implements APR managed-scope desired/configured reconciliation. I21 adds target-specific rendering inside APR. I22 adds a separate downstream Network Environment Operations boundary for operation identity, authority admission, concurrency, mutation outcomes and verification. I23 adds only a dormant source-neutral external identity/source extension seam while preserving local-first runtime behavior. I24 hardens the selected local deployment/operations boundary. I25 closes the supported-local product chain with executable full-chain acceptance plus an owner-preserving operator read composition and Web explainability journey.

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

Backend application containers remain non-root and NAPMS backend/Web Compose services use init/reaping plus `no-new-privileges`. PostgreSQL keeps the official image entrypoint/privilege model.

Web dependency resolution is repository-owned through `web/package-lock.json`; supported CI and Docker build paths use `npm ci`.

This is the current supported local deployment shape, not a claim of enterprise HA/SLA topology. Performance/capacity claims require an accepted workload target.

## Authority and trust boundaries

Authenticated actor identity originates from the server/session boundary, not request payloads. Application use cases evaluate action-specific Authority Management admission. Read authority and mutation authority remain independent. Unknown/ambiguous required authority fails closed.

A dormant optional external-authentication seam may provide a verified provider-qualified external subject to an `ActorIdentityResolver`, which resolves only to `Mapped | Unmapped | Ambiguous | Unknown`; only `Mapped` exposes a NAPMS actor. This seam is not wired as the default login path and introduces no OIDC/OAuth2/provider dependency.

Authentication identity does not grant business authority. Authority Management remains the owner of application permission for both local actors and any future externally mapped actor.

Local PostgreSQL credentials are operational transport credentials only. They do not represent NAPMS business actors or Authority facts.

## Technical Access Evidence

TAE owns immutable source-qualified technical evidence, not authorization or realization truth. Source-specific parsing/collection remains adapters. APR consumes TAE through consumer-owned projections; TAE does not depend on APR.

## Network Enforcement Placement

NEP owns normalized forwarding/path meaning, Logical Firewall identity, temporal provider correspondence, Enforcement Attachment and placement selection. It does not own authorization, vendor rendering or execution. APR consumes NEP through an APR-owned projection.

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
    -> application-owned ConfigurationRenderer port
    -> Cisco ASA outer adapter
    -> Rendered | Unsupported | Unknown
    -> independent semantic projection/equivalence proof
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

Architecture rules:
- NEO Domain imports no APR/NEP/TAE domain types;
- `OperationTarget` is NEO-owned projection data;
- `operation_id` binds exactly one Operation Target + artifact digest and is the first-slice idempotency key;
- identical retry returns the recorded operation result; conflicting reuse fails closed;
- mutation authority is independent from read authority;
- current target revision is the first-slice optimistic concurrency token;
- apply acceptance and semantic verification are distinct;
- `Verified` requires post-check evidence matching the requested artifact digest;
- Unknown apply is not blindly retried or reclassified as success;
- target/provider interaction remains behind a consumer-owned execution port;
- the current adapter is a deterministic in-process target stub because no real Cisco lab is available;
- stub success proves orchestration semantics only;
- the current operation repository is in-memory and does not claim crash-durable audit;
- real transport, credential handling, production rollback and durable operation persistence require later concrete environment evidence.

Feature contract: `docs/architecture/network-environment-operations-boundary.md`.

## Network Operator Realization View — I25

I25 adds a non-peer, read-only application composition for network/security operator inspection. It owns no authoritative business state.

```text
server-authenticated actor + scope + asOf
    -> ReadNetworkOperatorRealization authority admission
    -> owner-preserving APR / NEP / TAE / NEO projections
    -> stage availability + references/artifacts/evidence
    -> HTTP transport DTO
    -> Realization Web workspace
```

Rules:
- composition consumes owning application/port contracts and does not read peer tables directly;
- no independent realization-view persistence is introduced;
- authority is checked before cross-context composition;
- stage availability is `Available | NotAvailable | Unknown`;
- missing configured-evidence/managed-scope input is `NotAvailable`, not `Satisfied` or `Drift`;
- missing actual NEO operation result is `NotAvailable`, not `Verified`;
- ambiguous/incomplete semantic input remains `Unknown`;
- HTTP maps transport only and performs no reconciliation/execution inference;
- Web preserves backend availability and adds no mutation controls;
- contributing Access Rule references link to the existing Rule owner page;
- cross-chain explainability continues through existing Rule -> Decision -> Connectivity Requirement references, with each owner page enforcing its own read authority.

Feature contract: `docs/architecture/network-operator-realization-view.md`.

## I25 full-chain acceptance composition

The PostgreSQL acceptance suite composes existing owner APIs/repositories to prove:

```text
Connectivity Requirement
    -> Connectivity Decision
    -> Access Rule
    -> NEP placement + configured TAE evidence
    -> APR desired/reconciliation/rendering
    -> deterministic NEO controlled execution
    -> post-check Verified
```

This is executable acceptance evidence, not a new aggregate and not a claim that every runtime installation always has configured inputs or operation history. The interactive Realization view reports only current owning inputs/results.

## Cross-context application compositions

A composition consumes explicit owner/application ports, owns orchestration only, does not create copied business truth, and represents missing/ambiguous contributors explicitly. APR EnforcementTarget -> NEO OperationTarget mapping and the I25 realization view follow this rule.

Operational tooling may inspect/start/backup/restore the selected local runtime but does not acquire semantic ownership of module data. Database backup/restore preserves storage state as a whole; it is not a cross-context business API.

## Optional external extensions — I23

External identity and source integrations are optional future extensions, not current target dependencies. Future adapters terminate at source-neutral/context-owned boundaries. Deterministic stubs are sufficient to prove dormant seams. Real provider/source compatibility requires its own accepted future requirement.

Legacy/MSSQL and real provider/device transport are not target dependencies by default.

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
- explicit degraded/error outcomes instead of convenient permission, absence or success;
- no PostgreSQL network trust in the supported local Compose path;
- operational startup/status probes do not mutate business state;
- destructive local recovery requires explicit operator intent and a validated backup artifact;
- the realization read model never promotes missing/ambiguous owner evidence to success;
- Web dependency changes keep package intent and lockfile consistent.

## Revisit triggers

Revisit topology or add infrastructure only when accepted evidence requires it, such as a concrete external identity/source requirement, a real Cisco lab/transport contract, a requirement for durable NEO audit/rollback, measured workload/performance needs, independent scale/security/availability constraints, or a target environment requiring public TLS/HA/external secret management.

## Canonical references

- semantic ownership: `docs/domain/semantic-ownership.md`;
- current product requirements: `docs/requirements/`;
- feature architecture: `docs/architecture/`;
- ADRs: `docs/decisions/`;
- runtime/product state: `docs/engineering/current-state.md`;
- local operator workflow: `docs/engineering/local-product-operator-runbook.md`;
- current execution only: `docs/plans/active/README.md`.