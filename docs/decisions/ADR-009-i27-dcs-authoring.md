# ADR-009 — I27 Directed Communication Specification Authoring

Status: `accepted`.

Date: 2026-09-10.

## Context

NAPMS already persists immutable ACC DCS revisions as encoded projection payloads and decodes them into vendor-neutral traffic alternatives used by policy export and technical realization.

I27 must let a user define communication semantics through normal product fields. Exposing encoded `projection_payload`, vendor ACL syntax or arbitrary JSON would leak persistence/adapter concerns into the product and could bypass semantic validation.

The first slice should cover the existing normalized semantics without designing a new service catalogue.

## Decision

### Authoring model

One `CreateDcsRevision` command accepts:

```text
sourceComponentDeploymentId
destinationComponentDeploymentId
displayName?
trafficAlternatives: 1+
```

Each traffic alternative contains:

```text
protocol: canonical non-empty token
sourcePorts: NotApplicable | Any | PortRangeSet
destinationPorts: NotApplicable | Any | PortRangeSet
serviceReference?: non-empty string
```

A PortRangeSet contains one or more inclusive `first..last` ranges within `0..65535`.

The application layer canonicalizes ranges using the same normalized DCS semantics already consumed by export/realization and then encodes the accepted immutable ACC projection through the existing codec boundary.

The client never supplies `projection_payload`.

### UI-first subset

The first Web form optimizes the common transport-service case:

```text
protocol
source ports: Any by default
destination port/range(s)
optional service label
```

Advanced supported values may be exposed progressively. The backend contract remains the full normalized alternative model above; Web convenience must not redefine it.

### Protocol/port consistency

I27 does not invent a universal protocol registry beyond the existing canonical token contract.

The backend applies structural rules that are already semantically safe:

- protocol token must be non-empty/canonicalized;
- ranges must be valid and canonicalized;
- `NotApplicable` is distinct from `Any`;
- duplicate equivalent alternatives collapse or are rejected deterministically according to the existing normalized canonicalization contract;
- unsupported/invalid combinations fail explicitly instead of being translated to a broader selector.

Protocol-specific richer semantics such as ICMP type/code, application-layer URL paths or vendor service objects are outside I27 unless already represented by the existing normalized DCS contract.

### Direction

DCS direction is structural and explicit:

```text
source Component Deployment -> destination Component Deployment
```

The UI must not infer direction from the currently selected Resource or swap it implicitly.

### Immutability and revisioning

A persisted DCS revision is immutable.

Editing semantic fields creates another DCS revision identity. Existing Connectivity Requirements, Decisions and Access Rules keep their original revision reference.

Display metadata on an existing DCS revision remains presentation-only according to existing catalogue metadata semantics; changing traffic semantics is never a display-name edit.

### Active-participant rule

Normal DCS authoring requires both source and destination Component Deployments to be Active. Historical retired deployments remain readable for existing references but are not offered for new DCS creation.

### Authority

Creating a DCS revision requires `CurateApplicationCatalogue` under the selected admitted curation scope. This does not imply that the same actor may request, decide or materialize network access.

## API consequence

HTTP accepts a typed semantic DTO and returns the server-generated DCS revision identity plus canonicalized presentation/read data.

Transport field naming follows existing camelCase Web/API conventions, but transport naming does not belong in the Domain model.

## Alternatives rejected

### Raw JSON/projection editor

Rejected because it exposes persistence/codec representation and makes schema evolution/UI validation unsafe.

### ACL-style source/destination IP editor

Rejected because DCS describes application communication semantics between Component Deployments. Resource addressing belongs to Resource Catalogue and enforcement rendering is downstream.

### Single `protocol + port` scalar only

Rejected as the backend/domain contract because the existing normalized model supports alternatives and richer port constraints. The Web may initially optimize that simple case without narrowing domain truth.

## Consequences

- I27 can reuse the existing DCS codec/normalization seam rather than create parallel semantics;
- UI fields remain application-oriented and vendor-neutral;
- immutable historical policy references remain valid;
- unsupported richer protocol semantics remain explicit future work rather than guessed mappings.
