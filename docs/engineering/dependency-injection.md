# Dependency injection and composition model

Status: `accepted pre-infrastructure engineering decision`.

Date: 2026-09-08.

## Purpose

Define dependency direction and object composition before concrete infrastructure adapters are added.

## Decision

Use **explicit constructor injection** for application dependencies. Domain objects have no dependency-injection/container awareness.

There is one outer **composition root** for each executable process. It owns:
1. validated application configuration;
2. centralized logging/observability setup;
3. construction of concrete adapters;
4. construction of application use cases with those adapters;
5. attachment to transport/scheduler/CLI entrypoints.

The composition root depends inward. Domain/Application never import the composition root, DI container, FastAPI dependency primitives or adapter implementations.

## Ports

Port protocols are owned by the application/module that consumes them. Concrete adapters implement those protocols from the outside. Do not create a global service-locator or a generic `ports` dumping ground shared without ownership.

For the current I1 slice, `MaterializeAllowedAccessRule` receives:
- AuthorityPort;
- CommunicationCataloguePort;
- ConnectivityDecisionPort;
- AccessRuleRepository;
- RuleId factory.

This explicit dependency list is intentional and testable.

## Container policy

No DI framework/container is required by the core. If a framework container is later useful for runtime wiring, it is confined to the composition layer and must not become a service locator passed into use cases.

Forbidden:
- `container.resolve(...)` inside Domain/Application;
- global mutable dependency registry;
- hidden module-level adapter singleton accessed by use cases;
- framework decorators/types required to instantiate core use cases.

## Lifetimes

Default lifetime rules:
- immutable validated configuration: process lifetime;
- logging configuration/factory: process lifetime;
- stateless external clients/adapters: process lifetime when thread/task safe;
- transaction/UnitOfWork/repository session: operation/request lifetime when persistence arrives;
- application use case object: may be process lifetime only when dependencies are safe; otherwise operation lifetime;
- domain aggregates/value objects: normal domain lifetime, never container-managed singletons.

Concrete infrastructure can refine lifetime mechanics but not reverse dependency direction.

## Tests

Core tests construct use cases directly with fakes/in-memory implementations. They do not boot FastAPI, a DI container or production configuration. Composition tests later verify that the production root wires concrete adapters to the same port contracts.

## Cross-cutting concerns

Logging, metrics, tracing, retries and authorization checks must not be injected as an all-purpose context/service locator. Where a cross-cutting behavior belongs at the runtime boundary, use boundary middleware/decorator/composition. Where a use case semantically requires a capability such as Authority, keep it an explicit port dependency.

## I1 implementation consequence

The existing constructor-injected I1 use case is the accepted direction. A concrete production composition root is intentionally not created until there are production adapters to compose. I1 architecture tests must continue to prevent Domain/Application from importing framework/container/infrastructure packages.
