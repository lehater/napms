# NAPMS First-MVP Component Design

Status: research candidate.

Normative constraint input: `docs/research/engineering-design-policy.md`.

## Purpose

Constrain implementation-facing component ownership for the accepted first-MVP journey without replacing the canonical module contracts, OpenAPI, persistence model or domain models.

## Structural rule

NAPMS remains one modular application. Bounded-context/application modules collaborate in-process through provider-owned application contracts. HTTP is an external delivery adapter, not an internal module integration mechanism.

```text
HTTP / browser adapters
        ↓
application command/query handlers
        ↓
module-owned domain policy
        ↓ ports
module persistence / external adapters
        ↑
composition root selects concrete implementations

cross-module consumer
        ↓
provider application contract
        ↓
provider application/domain
```

## Public component families

For each first-MVP module, implementation exposes only the application operations already required by `mvp-module-contracts.yaml`. Component Design does not invent a second service API.

### Resource Catalogue

- command handlers own create/update/lifecycle orchestration;
- query handlers own current/history/detail projections;
- domain owns resource identity, lifecycle and catalogue invariants;
- persistence port is consumer/use-case shaped; SQLAlchemy/PostgreSQL representation remains infrastructure;
- published application contracts are the only cross-module access to Resource Catalogue state.

### Application Communication Catalogue / Application Deployment / Business Connectivity

Each provider follows the same boundary pattern: domain policy owns its accepted invariants; application components expose accepted module operations; persistence adapters implement module-owned persistence needs. Cross-module validation consumes provider application contracts, never provider tables/repositories.

### Access Policy

- application command component orchestrates policy authoring/lifecycle;
- domain owns policy rule/decision semantics;
- cross-module validation uses the accepted provider application contracts for catalogue/deployment/connectivity facts;
- policy materialization/export reads a coherent application-level snapshot through contracts, not cross-table joins owned by the consumer.

### Authority Management / security admission

Protected delivery operations invoke the accepted authorization/admission component before state-changing application commands. HTTP adapters do not reimplement authorization meaning, and repositories do not become authorization policy owners.

## External HTTP components

FastAPI route/controller components:

- parse/validate transport representation according to OpenAPI;
- establish request/security/correlation context;
- invoke one application operation;
- translate explicit application outcomes to canonical HTTP responses.

They do not contain domain decisions, SQL queries or cross-module orchestration.

## Persistence components

A module may use one concrete repository/unit implementation to satisfy several narrow application-owned contracts. Do not create a generic `Repository[T]` hierarchy.

Transaction ownership follows accepted system/persistence rules. Cross-module business composition happens above repositories. No foreign repository is injected into another module's domain model.

## Policy export/materialization collaboration

The critical first-MVP export flow is:

1. delivery adapter invokes the export application operation;
2. application orchestration obtains accepted facts through provider application contracts;
3. Access Policy/materialization policy composes the required policy representation;
4. unresolved required inputs remain explicit `Unresolved` outcomes;
5. renderer/export adapter produces canonical JSON/table/CSV representation;
6. observability/correlation is attached at the accepted outer boundary.

No internal HTTP/message bus is inserted into this path.

## Composition

The backend composition root constructs:

- module persistence implementations;
- provider application services/handlers;
- security admission implementation;
- policy materialization/export collaborators;
- external delivery adapters.

A DI framework is not required. Construction mechanism is implementation freedom as long as dependency ownership is preserved.

## Mapping boundaries

- OpenAPI DTO ↔ application input/output: HTTP adapter;
- persistence row ↔ module domain/application value: owning persistence adapter;
- provider application fact ↔ consumer input: consumer-side application mapping when representations differ;
- domain/application outcomes ↔ CSV/JSON presentation: export/delivery renderer.

Framework representations never become domain contracts.

## Forbidden dependencies

- domain/application → FastAPI/SQLAlchemy/PostgreSQL driver/browser framework;
- module consumer → another module's repository/table;
- repository → HTTP/controller;
- Access Policy consumer → provider persistence internals;
- internal module → another module through HTTP;
- solver/event/message infrastructure introduced without accepted requirement;
- generic repository/service locator/mediator used only for architectural style;
- authorization meaning implemented independently in controllers or repositories.

## Structural verification

Architecture tests should reject inner-layer framework imports, cross-module repository/table imports, internal HTTP clients between modules and domain/application contracts containing transport/persistence types. Existing NAPMS architecture tests remain evidence where they already enforce these rules.

## Implementation freedoms

Coding may choose private helpers, local class/function representation, concrete construction technique, file split inside the accepted module taxonomy and local algorithms. Coding may not change module/application contract ownership, cross-module dependency direction, security admission placement, transaction/materialization semantics or introduce a new integration mechanism without reopening the owning design Authority.


