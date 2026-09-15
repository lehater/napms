# External identity and authoritative-source boundary

## Responsibility

Keep external identity and source integration outside NAPMS domain semantics while preserving the local-first runtime and bounded-context ownership.

## Authentication path

The primary runtime path is:

```text
local username/password
    -> LocalPasswordAuthenticator
    -> authenticated NAPMS actor
    -> server-side session/request actor
    -> application use case
    -> Authority Management action/scope admission
```

Local authentication is a supported product mechanism, not a provider adapter hidden behind domain abstractions.

An external authentication integration, when configured, terminates at the source-neutral seam:

```text
external authentication mechanism
    -> outer adapter verifies provider/protocol mechanics
    -> VerifiedExternalIdentity
    -> ActorIdentityResolver
    -> Mapped | Unmapped | Ambiguous | Unknown
    -> authenticated NAPMS actor
    -> existing session/application boundary
```

Exactly one effective actor mapping is required. `Unmapped`, `Ambiguous` and `Unknown` fail closed. Domain and application modules do not depend on OIDC/OAuth/JWT/vendor SDK types.

## Authority boundary

Authentication establishes actor identity only. Authority Management remains the owner of business permission.

External claims, groups, roles or token scopes are source facts unless an Authority-owned import/mapping contract assigns them NAPMS authority meaning.

## External source boundary

For an external authoritative source:

```text
external source
    -> source-specific adapter
    -> context-owned import/projection contract
    -> context application service
    -> context-owned repository/state
```

Authority Management, Application Communication Catalogue and Resource Catalogue retain semantic ownership. There is no shared enterprise-source domain model and no direct cross-context ownership of source tables.

Source-specific synchronization, freshness, completeness and deletion semantics belong to the concrete integration contract. They are not inferred by generic infrastructure.

## Dependency direction

```text
Domain
  <- Application / consuming ports
      <- outer adapters
          <- runtime/composition
```

Provider-specific adapters remain optional runtime composition. The local runtime does not depend on their presence.

## Invariants

1. Local authentication remains independently operable.
2. External identity maps to exactly one NAPMS actor or fails closed.
3. Authentication does not grant business authority.
4. Provider/protocol types remain outside Domain and application semantics.
5. Each bounded context retains ownership of imported semantic state.
6. External identifiers remain source/correlation identifiers unless the owning context explicitly defines stronger identity semantics.
7. Shared technical integration infrastructure does not create shared domain ownership.
