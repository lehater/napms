# Current target architecture

Status: `accepted current target through I15; evolves through active roadmap increments`.

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
- Connectivity Decision.

Current non-peer application compositions include:
- Requirement-to-Policy Alignment;
- policy export/snapshot normalization;
- Scoped Connectivity Inventory as selected I16A work.

Later roadmap contexts include Technical Access Evidence, Access Policy Realization and Network Enforcement Placement.

Their exact runtime/deployment decomposition remains evidence-driven.

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

ADR-005 is current: Connectivity Decision is a first-class Bounded Context owning immutable final `Allowed | NotAllowed` Decisions, validity, reasons/provenance and supersession semantics.

ADR-003 is historical and superseded. The former external/deferred Decision seam must not be treated as current target architecture.

Access Policy consumes effective final Decision truth but continues to own Access Rule identity/state.

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

Requirement-to-Policy Alignment and Scoped Connectivity Inventory follow this pattern.

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
- ADRs: `docs/decisions/`;
- runtime/engineering state: `docs/engineering/current-state.md`;
- current execution only: `docs/plans/active/README.md`.
