# Dependency injection and composition model

## Purpose

Define dependency direction and runtime composition without coupling Domain/Application to infrastructure or framework mechanics.

## Composition rule

Use explicit constructor injection for application dependencies. Domain objects have no dependency-injection/container awareness.

Each executable process has an outer composition root responsible for:

1. validated runtime configuration;
2. logging/observability setup;
3. concrete adapter construction;
4. application/use-case construction with those adapters;
5. transport, scheduler or CLI attachment.

The composition root depends inward. Domain/Application never import the composition root, DI containers, HTTP framework primitives or concrete adapters.

## Ports

Ports are owned by the consuming application/module. Cross-bounded-context translation belongs in outer adapters or explicitly owned composition/workflow code.

A bounded-context core does not import another bounded-context private model or persistence representation merely to share a convenient type. Cross-context contracts use the semantic references/projections published by the owning context.

No application module performs peer-context SQL or treats another context's repository as its own persistence port.

## Runtime composition

NAPMS runtime composition is explicit rather than service-locator based.

- validated configuration is assembled before dependencies;
- PostgreSQL repositories are constructed as outer adapters for the contexts they own;
- application workflows receive only the ports/contracts they consume;
- FastAPI is attached at the transport boundary;
- Web/nginx is an outer static/runtime adapter and does not compose Domain/Application objects;
- process/deployment sequencing does not alter inward dependency direction.

Executable roots such as migration, local seed and HTTP runtime each build only the dependencies required for that process.

## Container policy

No DI framework/container is required. A framework container, if present at the outermost runtime boundary, must not become a service locator passed into use cases.

Forbidden:

- `container.resolve(...)` inside Domain/Application;
- global mutable dependency registries;
- hidden module-level adapter singletons;
- framework decorators/types required to instantiate core use cases;
- peer-context repository injection that bypasses a public semantic contract.

## Lifetimes

Default lifetime rules:

- immutable validated configuration: process lifetime;
- logging configuration/factory: process lifetime;
- stateless thread-safe adapters/clients: process lifetime when appropriate;
- transaction/repository connection: operation or request lifetime;
- application use case: lifetime follows dependency safety;
- domain values/aggregates: normal domain lifetime.

A longer-lived dependency must not retain request/transaction state accidentally.

## Transactions and context ownership

A repository/transaction belongs to its semantic owner. Composition may coordinate several context calls but does not create implicit cross-context database ownership.

Cross-context atomicity, snapshots or consistency requirements must be explicit Architecture contracts. They are not inferred from the fact that several repositories happen to use one PostgreSQL server.

## Tests

Core tests construct use cases directly with fakes/in-memory implementations. Adapter integration tests prove concrete port contracts. Composition tests prove that executable roots wire real adapters to accepted ports without reversing dependencies.

Architecture tests should mechanically protect dependency direction and prohibit peer-private imports or persistence bypasses where practical.

## Cross-cutting concerns

Logging, metrics, tracing, retries, authentication and authorization do not become an all-purpose context/service locator. Runtime observability and authentication mechanics live at outer boundaries. Business authority remains an explicit semantic dependency owned by Authority Management.
