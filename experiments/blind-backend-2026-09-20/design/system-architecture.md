# Blind backend system architecture

Status: ACCEPTED candidate

## Runtime shape

Use one stateless backend application process as a modular monolith plus one ACID relational database. Authentication depends on an external OpenID Connect identity provider. No message broker or distributed service topology is required by current behavior.

Rationale:
- accepted flows are synchronous;
- domain owners need strong local transactions;
- AccessRequest submission needs one coherent validation/write snapshot without cross-owner writes;
- complete policy materialization requires a coherent cross-module read snapshot;
- no accepted independent scaling/deployment requirement justifies network-separated services.

## Modules

Domain/application modules:
- `resource_description`
- `application_communication`
- `application_deployment`
- `business_connectivity`
- `access_policy`
- `policy_materialization` (application composition, no independent domain truth)

Technical edge modules:
- `api` — external request/response adapter;
- `authn_authz` — OIDC validation and permission admission;
- persistence adapters owned by each domain module;
- `runtime` — composition/configuration/health/telemetry wiring.

## Dependency rules

- Domain code depends only on its own domain types.
- Application services depend on owner-domain contracts and consumer-shaped ports.
- One domain module never imports peer persistence/schema/private domain internals.
- Cross-domain references cross module boundaries as opaque refs plus minimal public facts.
- API maps external representations to application commands/queries; domain models are not serialized directly.
- Persistence adapters implement module-owned repository ports.
- Policy Materialization consumes public read ports from owners; it cannot mutate peer truth.

## Transactions and consistency

Writes:
- exactly one semantic owner is mutated per command;
- optimistic aggregate version checks;
- a command may use one database transaction to perform peer-owner validation reads plus its owner write, while peer tables remain read-only;
- database uniqueness/foreign-key constraints stay inside a module's owned schema; cross-owner references are opaque values validated through public ports.

Policy materialization:
- runs read-only under database REPEATABLE READ (or stronger equivalent) across module-owned schemas in the same physical relational database;
- owner query ports accept the shared read-snapshot context so all resolved facts come from one database snapshot;
- the backend records server-owned `evaluationAt` for that snapshot; historical/time-travel policy materialization is not part of the MVP.

## Interaction style

- external interface: synchronous HTTP/JSON selected as the smallest interoperable request/response boundary for the current CRUD/decision/materialization workload;
- internal interaction: synchronous in-process calls through public application/read ports;
- asynchronous messaging: NOT_APPLICABLE to current accepted behavior.

## Persistence constraint

A single physical relational database is architecture-significant because it provides atomic owner transactions plus coherent cross-module snapshot reads. Domain schemas remain module-owned. Concrete database vendor is an implementation freedom only if it supports required transaction isolation, constraints, migrations and time/network-address types used by Data Design; otherwise Implementation Design must select a compatible engine explicitly.

## Deployment/configuration boundary

The process is horizontally replicable only when all authoritative state remains in the relational database and authentication is token based. Configuration is externalized; secrets are supplied through a secret-capable runtime source and never committed.

## Architectural non-goals

- microservices/service mesh;
- distributed transactions;
- event sourcing;
- message broker;
- provider/firewall adapters;
- UI rendering;
- configured-state reconciliation;
- historical policy export.
