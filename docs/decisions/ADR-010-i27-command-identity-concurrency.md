# ADR-010 — I27 Catalogue Command Identity, Provenance and Concurrency

Status: `accepted`.

Date: 2026-09-10.

## Context

I27 opens catalogue mutations through HTTP/Web. The current seed/direct-persistence path supplies stable IDs and provenance internally; a normal product workflow must not make users invent UUIDs, fact references or provenance strings.

Mutation also needs two independent safety properties:

- retried commands must not accidentally create duplicate effects;
- concurrent edits must not silently overwrite newer state.

## Decision

### Server-owned identities

For UI/HTTP-created catalogue identities and facts, the server generates authoritative identifiers.

Use UUID values for ACC Application, Component, Component Deployment and DCS revision identities.

Resource `resourceReference` remains the Resource Catalogue stable reference type, but UI-created references are generated server-side using an opaque repository-owned form. The external value must not encode mutable display name, address, Responsibility Scope or owner.

Temporal fact/binding/reference identifiers are likewise server-generated.

Clients may never choose authoritative identity merely because a transport field could technically accept one.

### Command idempotency key

Every catalogue mutation HTTP request carries a client-generated opaque `Idempotency-Key` header.

The server records enough command-result correlation within the owning bounded context to guarantee:

```text
same actor + same action + same idempotency key + equivalent command
    -> same semantic result
```

Reusing the same key with a materially different command fails explicitly.

Idempotency records must not become business-domain entities; they are application/persistence support for safe transport retry.

Internal non-HTTP callers use the same application idempotency contract when duplicate execution is possible.

### Optimistic concurrency

Mutable catalogue identities carry a monotonically increasing integer `version` beginning at `1`.

Commands that mutate an existing mutable entity require `expectedVersion`.

On successful mutation:

```text
stored version == expectedVersion
    -> apply mutation
    -> version = version + 1
```

Otherwise the command fails with a concurrency conflict and performs no semantic mutation.

For immutable create-only facts such as DCS revisions, expected version is not applicable; idempotency still applies.

For ending a temporal relation, the relation itself carries or exposes a version/precondition sufficient to prevent two clients from silently applying conflicting end operations.

### HTTP representation

Read DTOs expose `version` for mutable catalogue entities/relations.

Mutation DTOs use explicit `expectedVersion` for clarity in the first slice. HTTP ETags may be added later but are not required to prove the product contract.

Concurrency conflicts map to a dedicated conflict response (`409`) with a stable machine-readable error code. Validation and authorization remain distinct failure categories.

### Provenance

Users do not enter `provenanceReference`.

For interactive catalogue mutations, the application layer creates provenance containing/stably referencing:

- authenticated actor identity;
- catalogue action/command kind;
- server-recorded action time;
- command/idempotency correlation;
- source namespace identifying interactive NAPMS curation.

The exact serialized provenance string is an engineering representation. Domain/business truth is that mutation provenance is server-owned, non-empty and sufficient to explain the source of a curated fact.

Imported/provider-fed future sources may use different provenance namespaces behind the same domain contract.

### Time

The server owns `recordedAt`/action time.

Where the user intentionally authors effective validity, such as a Resource Scope Affiliation or Resource Realization effective start/end, those effective instants are explicit semantic inputs and remain distinct from server-recorded action time.

### Transactional guarantee

Within one owning-context mutation transaction, the server persists:

```text
semantic mutation
+ new version where applicable
+ idempotency/result correlation
+ provenance needed by the new fact
```

so an acknowledged success cannot later be retried into a duplicate effect.

## Alternatives rejected

### Client-generated domain UUIDs

Rejected for normal UI because it leaks technical identity responsibility to the user/client and complicates trust boundaries.

### Display name as stable key

Rejected because names are mutable presentation data.

### Last-write-wins

Rejected because concurrent curation could silently destroy catalogue changes and make downstream connectivity reasoning depend on browser timing.

### Idempotency only

Rejected because retry deduplication does not prevent stale clients overwriting newer state.

### Optimistic version only

Rejected because a timed-out successful create retried by the client could create another identity/effect.

## Consequences

- users author semantic catalogue data rather than implementation identifiers;
- HTTP retry is safe;
- stale writes fail explicitly;
- provenance is trustworthy server-owned data;
- ACC and RC can share one mutation safety pattern without sharing repositories or bounded-context transactions;
- Stage 0 command/concurrency blocking decision is closed and implementation may now model the supporting ports/persistence.
