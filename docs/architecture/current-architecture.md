# Current target architecture

Status: `accepted current target through I22; I23 Enterprise Identity and Authoritative Source Integration is next`.

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

No accepted workload/SLA currently justifies service-per-context distribution.

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

Current non-peer application/read compositions include Requirement-to-Policy Alignment, policy export/snapshot normalization and Scoped Connectivity Inventory.

I20 implements APR managed-scope desired/configured reconciliation. I21 adds target-specific rendering inside APR. I22 adds a separate downstream Network Environment Operations boundary for operation identity, authority admission, concurrency, mutation outcomes and verification. Runtime/deployment decomposition remains evidence-driven.

## Current runtime boundary

Implemented local/development topology:

```text
browser
  -> nginx / React Web UI
  -> FastAPI HTTP outer adapter
  -> framework-free application/domain modules
  -> module-owned PostgreSQL repositories
```

The normal local topology exposes one public nginx endpoint. This is a development/runtime boundary, not a production deployment/SLA claim.

## Authority and trust boundaries

Authenticated actor identity originates from the server/session boundary, not request payloads. Application use cases evaluate action-specific Authority Management admission. Read authority and mutation authority remain independent. Unknown/ambiguous required authority fails closed.

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

I22 introduces a separate framework-free Network Environment Operations module downstream of rendering.

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
- `OperationTarget` is NEO-owned projection data; composition maps upstream target identity into it without redefining Logical Firewall/Enforcement Attachment meaning;
- `operation_id` binds exactly one Operation Target + artifact digest and is the first-slice idempotency key;
- identical retry returns the recorded operation result; conflicting reuse fails closed;
- mutation authority is an explicit consumer-owned port and is independent from read authority;
- current target revision is the first-slice optimistic concurrency token;
- apply acceptance and semantic verification are distinct;
- `Verified` requires post-check evidence matching the requested artifact digest;
- Unknown apply is not blindly retried or reclassified as success;
- target/provider interaction remains behind a consumer-owned execution port;
- the current adapter is a deterministic in-process target stub because no real Cisco lab is available;
- stub success is only evidence of orchestration semantics, not Cisco transport compatibility;
- the current operation repository is in-memory and does not claim crash-durable audit;
- real transport, credential handling, production rollback and durable operation persistence require later concrete environment evidence.

Feature contract: `docs/architecture/network-environment-operations-boundary.md`.

## Cross-context application compositions

A composition consumes explicit owner/application ports, owns orchestration only, does not create copied business truth, and represents missing/ambiguous contributors explicitly. APR EnforcementTarget -> NEO OperationTarget mapping follows this rule.

## Transition and external sources

Legacy/MSSQL and real provider/device transport are not target dependencies by default. Vendor rendering is an APR outer-adapter capability. When concrete enterprise/provider integration is selected, adapt it at the infrastructure boundary, preserve provenance and fail closed when required identity/validity cannot be established.

## Security/integrity guardrails

Architecture must preserve:
- exact proposal/Decision/Rule subject correlation;
- authoritative Rule uniqueness/idempotency;
- module-owned persistence boundaries;
- explicit logical-time validity where required;
- no silent semantic broadening/narrowing in normalization or rendering;
- no false Verified outcome from transport acceptance alone;
- operation idempotency and optimistic concurrency for mutation;
- explicit degraded/error outcomes instead of convenient permission, absence or success.

## Revisit triggers

Revisit topology or add infrastructure only when accepted evidence requires it, such as concrete enterprise/provider source mechanics, a real Cisco lab/transport contract, production identity/deployment requirements, measured performance needs, or independent scale/security/availability constraints.

## Canonical references

- semantic ownership: `docs/domain/semantic-ownership.md`;
- current product requirements: `docs/requirements/`;
- feature architecture: `docs/architecture/`;
- ADRs: `docs/decisions/`;
- runtime/engineering state: `docs/engineering/current-state.md`;
- current execution only: `docs/plans/active/README.md`.
