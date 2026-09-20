# Backend engineering policy

Status: ACCEPTED candidate

## Purpose

Constrain implementation so accepted domain/application/architecture contracts remain visible in code without prescribing private algorithms.

## Normative obligations

### Ownership and dependency direction

- Domain packages import no HTTP, database, OIDC, telemetry or framework types.
- Application services depend on narrow consumer-shaped ports; infrastructure implements those ports.
- A module may call a peer only through its public application/read contract. Direct peer-table mutation and import of peer persistence/private domain code are forbidden.
- Policy Materialization may compose peer read contracts but cannot become an alternate write owner.
- API DTOs and persistence rows are mapped at adapter boundaries; neither representation becomes a domain type.

### KISS / YAGNI

- Use the smallest component set that realizes current accepted contracts.
- No generic repository, event bus, mediator, CQRS split, plugin system, service mesh, workflow engine or speculative extension point without a concrete accepted need.
- Prefer explicit functions/value types and composition; introduce interfaces only at actual ownership/technology/substitution seams.
- Do not add a wrapper solely so every port has a distinct runtime object.

### SOLID/Clean constraints made concrete

- Each public component has one coherent owner/reason to change.
- Consumer-facing ports expose only operations required by the consuming use case.
- Infrastructure dependencies point inward through application-owned ports; inner code never depends on adapter/framework abstractions.
- Substitutable implementations must preserve public success/failure/transaction semantics, not merely method signatures.
- Cross-module collaboration is expressed by stable refs/public facts rather than sharing mutable objects.

### Domain/data correctness

- Unknown/missing/unresolved values are never silently converted to zero, empty collection, denial, unrestricted traffic or successful empty policy.
- IDs are opaque; no semantic meaning is encoded in sortable/string structure.
- Clock/time acquisition is injected at application/runtime boundaries where behavior depends on time.
- Network values are validated before domain acceptance: HOST is canonical IPv4/IPv6 literal only; PREFIX requires canonical CIDR with host bits already zero and must never be silently masked; IPv4-mapped IPv6 is not silently unmapped.
- TrafficClause uses canonical integer ipProtocol 0..255. Only TCP(6)/UDP(17) may carry port ranges; other protocols require empty port sets. Port ranges are sorted and overlapping/adjacent ranges merged without crossing gaps. No protocol-name alias layer exists at the canonical HTTP/domain boundary.
- Port-range canonicalization is mandatory: sort ascending and merge duplicate, overlapping and directly adjacent ranges; never merge across a gap; the resulting union must exactly equal the accepted input port set.
- All SQL/data access uses parameter binding; string-built SQL containing untrusted values is forbidden.
- Optimistic concurrency and idempotency semantics from Data Design are mandatory, not adapter conveniences.

### Error and failure discipline

- Domain rejection, authorization denial, stale conflict, unresolved materialization, dependency failure and unexpected failure remain distinct.
- Unexpected exceptions do not become domain rejection.
- An unknown commit outcome is never returned as confirmed success.
- Retry is permitted only where the operation is known idempotent or protected by accepted idempotency semantics.

### Security discipline

- Authentication/authorization occurs at every protected external operation before mutation.
- Caller-supplied identity/permission fields cannot override trusted principal data.
- Secrets/tokens are not persisted in domain tables and are never emitted in logs.
- Error/log serialization uses an allow-list of safe fields.

### Migrations and configuration

- Schema changes use ordered versioned migrations reviewed against Data Design.
- Startup configuration is typed/validated once; inner code does not read environment variables directly.
- Production defaults must not silently enable insecure authentication, debug disclosure or destructive migration behavior.

## Explicit non-rules

- TDD is not mandated by this policy.
- A class/interface construct is not required when a function/value contract is sufficient.
- Eventual consistency is not a default.
- REST maturity/HATEOAS is not a requirement.
- Domain events may be used internally only when they simplify accepted behavior; no broker/durable event contract is implied.

## Downstream consumers

Component Design, Verification/Test Design and Implementation Design must enforce these obligations.
