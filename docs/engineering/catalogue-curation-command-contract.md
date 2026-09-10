# Catalogue Curation Command Contract

Status: `accepted I27 engineering contract`.

Date: 2026-09-10.

## Purpose

Translate the I27 domain/ADR decisions into one implementation-facing command pattern shared by Application Communication Catalogue and Resource Catalogue without merging their repositories or transactions.

## Command envelope

Every catalogue mutation receives application-level context equivalent to:

```text
CatalogueCommandContext
    actorId            # server/session supplied
    authorityScope     # selected admitted Responsibility Scope
    idempotencyKey     # opaque non-empty value
    effectiveAt        # server-owned authorization/action time
```

The HTTP client never supplies trusted `actorId` or server action time.

A mutation of an existing mutable entity additionally receives:

```text
expectedVersion: positive integer
```

Temporal authoring commands may separately receive user-intended validity instants such as `validFrom` / `validUntil`.

## Result envelope

Successful commands return a stable result containing at least:

```text
identity/reference
version where mutable
canonical current representation or enough data to refetch it
```

A replay of an equivalent command with the same idempotency key returns the same semantic result.

## Failure classes

Application code keeps these failure categories distinct:

```text
NotAuthorized
ValidationFailed / DomainInvariantFailed
NotFound
ConcurrencyConflict
IdempotencyConflict
PersistenceOutcomeUnknown
```

HTTP mapping may use conventional status codes, but transport mapping must not collapse semantic distinctions required by Web error handling.

Recommended first-slice mapping:

```text
NotAuthorized            -> 403
NotFound                 -> 404
ValidationFailed         -> 422
ConcurrencyConflict      -> 409 / catalogue_concurrency_conflict
IdempotencyConflict      -> 409 / catalogue_idempotency_conflict
PersistenceOutcomeUnknown-> 503 or owning runtime uncertainty mapping
```

Authentication failure remains session/auth transport behavior.

## Authority admission

ACC command handlers require `CurateApplicationCatalogue`.

RC command handlers require `CurateResourceCatalogue`.

Authority is checked before mutation persistence. Object lookup needed to derive authoritative command context must not become a side channel leaking protected data.

## Identity factory ports

Application code obtains server-owned identifiers through injected ports/factories rather than calling transport/UI code.

Expected semantics:

```text
new UUID identity
new opaque Resource reference
new temporal fact/reference id
```

Concrete UUID/random/reference generation belongs to composition/adapters.

Deterministic compatibility IDs used only by schema/data migration are a separate migration concern and must not reuse interactive random identity generation semantics.

## Provenance factory

Application code uses an injected/source-owned provenance builder receiving trusted command context and new fact identity.

The resulting domain provenance reference is non-empty and stable enough for explainability. User strings are not accepted as authoritative provenance.

## Idempotency repository

Each owning catalogue persistence boundary provides application support for idempotency records keyed by a tuple equivalent to:

```text
actor + authority action + authority scope + idempotency key
```

Stored data includes:

- canonical request fingerprint;
- command kind;
- stable semantic result identity/reference;
- result version where needed;
- recorded time/provenance correlation.

Equivalent replay returns the recorded result. Different fingerprint under the same key fails with `IdempotencyConflict`.

The fingerprint is computed from canonical semantic command input, excluding transient transport representation and server action time.

## Optimistic concurrency

Mutable identity records contain integer `version >= 1`.

Repository update methods use compare-and-set semantics in SQL/application persistence:

```text
UPDATE ...
SET ..., version = version + 1
WHERE identity = ? AND version = expectedVersion
```

Zero affected rows are resolved as not-found vs version conflict without claiming success.

A command transaction records the idempotency result only when the semantic mutation is committed as part of the same owning-context transaction.

## Create commands

Create commands do not take client-generated domain identity.

On first execution:

1. authorize;
2. validate semantic inputs/parents;
3. allocate server identity/reference;
4. create provenance;
5. persist semantic record(s) and idempotency result atomically;
6. return generated identity/current representation.

On retry with the same equivalent idempotency command, return the original generated identity.

## Immutable DCS command

`CreateDcsRevision` is create-only:

1. authorize `CurateApplicationCatalogue`;
2. ensure source/destination deployments exist and are Active;
3. validate/canonicalize traffic alternatives;
4. generate revision UUID and provenance;
5. encode through the existing ACC projection codec boundary;
6. persist immutable revision + idempotency result atomically.

No update command changes DCS traffic semantics in place.

## Temporal relation commands

Creation of realization, scope affiliation, responsibility or binding facts validates effective intervals and overlap invariants before commit.

Ending a relation is an explicit command with an expected version/current-state precondition. It records the user-intended effective end time separately from server action/provenance time.

Historical relation rows are retained.

## Read-side version exposure

Curation read DTOs expose version for mutable entities/relations needed by forms. Existing read consumers that do not mutate catalogue state are not required to adopt version fields unless their contract benefits from them.

## Testing consequences

Every command family requires focused executable evidence for:

- authorized success;
- unauthorized failure with no mutation;
- invariant validation;
- server-generated identity/provenance;
- equivalent idempotent replay;
- idempotency-key conflict;
- stale expectedVersion conflict;
- persistence failure/outcome uncertainty behavior where the repository contract distinguishes it.

## Boundary consequence

This contract is reusable structure, not a shared cross-context domain service. ACC and RC retain independent domain types, repositories, tables and transactions.
