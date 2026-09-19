# NAPMS Engineering Design Policy

Status: research candidate. This is project engineering policy, not universal Harness semantics.

## Purpose

Constrain implementation-facing design so agents preserve the accepted NAPMS modular application architecture, domain ownership, security boundaries and contract-first delivery without inventing framework-driven structure.

## Obligations

### Dependency and ownership

- Source dependencies follow accepted module contracts and point from delivery/infrastructure toward application/domain policy.
- A module does not read or write another module's persistence tables as an integration mechanism.
- Cross-module collaboration uses the provider's accepted application/module contract.
- Domain/application contracts do not expose SQLAlchemy, FastAPI, PostgreSQL-driver or browser-framework representations.
- Composition is allowed to select concrete implementations; inner policy is not.
- Authorization admission remains at the accepted security boundary and is not duplicated as ad-hoc controller/repository checks.

### SOLID / responsibility

- SRP: HTTP handling, application orchestration, domain decisions, persistence mapping, authorization admission and projection/rendering are separate responsibilities when independently changeable.
- OCP: create seams for accepted providers/external mechanisms and required variation; no plugin architecture for hypothetical providers.
- LSP: substitutes preserve explicit contract outcomes, including validation/conflict/authorization/Unresolved semantics.
- ISP: consumer-facing contracts expose only operations needed by that consumer/journey slice.
- DIP: high-level policy depends on provider/application contracts, never concrete persistence or transport implementations.

### General constraints

- KISS/YAGNI: no generic repository, service locator, event bus, mediator, internal HTTP or microservice split without accepted need.
- CQS: query projections do not perform hidden domain mutation; state-changing commands are explicit.
- LoD/Tell Don't Ask: consumers do not navigate another module's internal aggregate/persistence representation to implement policy.
- Composition over inheritance unless substitutability is a real domain/technical relationship.
- DbC: public module/application contracts preserve accepted inputs, outcomes and failure semantics.
- Fail Fast: invalid technical state and violated invariants fail at the owning boundary; they do not become successful/partial business outcomes.
- POLA: no hidden current-time/user/global defaults where canonical contracts require explicit values/context.

## NAPMS-specific non-rules

The accepted architecture explicitly has no internal HTTP between modules and no asynchronous messaging requirement for the first MVP. Therefore this policy does not introduce:

- internal REST between modules;
- message bus/event-driven integration;
- CQRS infrastructure merely because commands and queries are distinct;
- generic repository abstractions;
- service-per-bounded-context deployment;
- dependency-injection framework as an architectural requirement.

## Component-design acceptance

A component design must identify public components/contracts, responsibility, contract ownership, cross-module dependency direction, persistence/representation mappings, composition, security admission placement, critical first-MVP journey collaboration, forbidden dependencies and structural verification. It must also state implementation freedoms.
