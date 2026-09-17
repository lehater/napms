# Dependency injection and composition model

Status: `accepted and exercised through I16B Connectivity Decision Runtime`.

Date: 2026-09-09.

## Purpose

Define dependency direction and object composition without coupling core semantics to infrastructure/frameworks.

## Decision

Use **explicit constructor injection** for application dependencies. Domain objects have no dependency-injection/container awareness.

There is one outer **composition root** for each executable process. It owns:
1. validated application configuration;
2. centralized logging/observability setup when the runtime boundary is introduced;
3. construction of concrete adapters;
4. construction of application use cases with those adapters;
5. attachment to the selected transport/scheduler/CLI entrypoint.

The composition root depends inward. Domain/Application never import the composition root, DI container, HTTP framework primitives or adapter implementations.

## Greenfield PostgreSQL composition

The local-dev greenfield PostgreSQL composition constructs:
- Authority Management PostgreSQL repository -> action-specific consumer adapters, including independent Decision Decide/Read authority;
- Application Communication Catalogue PostgreSQL repository -> proposal, Decision, Requirements and policy-export consumer adapters;
- Resource Catalogue PostgreSQL repository -> policy-export and Scoped Connectivity consumer adapters;
- Access Policy PostgreSQL repository;
- Connectivity Requirements PostgreSQL repository;
- Connectivity Decision PostgreSQL repository -> Decision application use cases, Access Policy consumer projection and Scoped Connectivity coarse summary;
- strict internal DCS projection codec/decoder.

Each persisted bounded context uses its own repository/schema ownership. No application code performs cross-module SQL.

ACC and RC use separate read-only `REPEATABLE READ` connections for one logical snapshot scope. Access Policy uses its own transactional connection. These are infrastructure mechanics and do not alter Domain/Application semantics.

Connectivity Decision is a first-class bounded context with Decision-owned PostgreSQL persistence. The normal local runtime composes its durable repository and consumer adapters directly; it does not inject a deterministic Allowed provider.

## Ports

Port protocols are owned by the consuming application/module. Cross-bounded-context translation belongs in outer adapters. A bounded context Domain/Application core does not import another bounded context core merely to share a convenient type.

This rule is executable in architecture tests.

## HTTP composition

The HTTP runtime composition owns:
- validated `HttpRuntimeConfig`;
- process-lifetime local authenticator and opaque in-memory session store;
- request-lifetime greenfield PostgreSQL scope;
- durable Decision participant and consumer dependencies supplied by that scope;
- FastAPI transport attachment;
- readiness probing.

Access Policy receives the Decision consumer through its own port. The normal runtime obtains that consumer from the greenfield scope. An explicit injected `ConnectivityDecisionPort` remains available only as focused composition/test plumbing and is not the normal local product path.

## I11 local executable process roots

Docker Compose introduces process orchestration, not a DI container.

Python executable roots remain explicit:
- `napms-migrate` -> typed application config -> tracked PostgreSQL migration runner;
- `napms-seed-local` -> typed local seed config -> idempotent local demo seed;
- `napms-http` -> typed HTTP runtime config -> existing greenfield composition + FastAPI.

The Web image is an outer static/runtime adapter: nginx serves built React assets and proxies same-origin HTTP traffic. It does not compose Domain/Application objects.

Compose dependency ordering (`postgres -> migrate -> seed -> api -> web`) is deployment/runtime sequencing and does not change inward dependency direction.

## Container policy

No DI framework/container is required. If one is later useful, it remains confined to composition and must not become a service locator passed into use cases.

Forbidden:
- `container.resolve(...)` inside Domain/Application;
- global mutable dependency registry;
- hidden module-level adapter singleton;
- framework decorators/types required to instantiate core use cases.

## Lifetimes

Default rules:
- immutable validated configuration: process lifetime;
- logging configuration/factory: process lifetime;
- stateless safe adapters/clients: process lifetime when appropriate;
- transaction/repository connection: operation/request lifetime;
- application use case: lifetime follows dependency safety;
- domain values/aggregates: normal domain lifetime.

## Tests

Core tests construct use cases directly with fakes/in-memory implementations. PostgreSQL integration tests prove concrete adapter contracts. Composition tests prove the outer root wires real adapters to the accepted ports without reversing dependencies.

## Cross-cutting concerns

Logging, metrics, tracing, retries and authorization must not become an all-purpose context/service locator. Runtime observability belongs at the outer boundary. Business Authority remains an explicit semantic dependency.

The I8 HTTP runtime implements the structured logging/correlation obligations in `docs/engineering/observability.md`; Domain/Application remain transport- and logging-framework-independent.
