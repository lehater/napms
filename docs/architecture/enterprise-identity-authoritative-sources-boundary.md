# Optional External Identity and Source Extension boundary

Status: `accepted I23 optional-extension boundary`.

Date: 2026-09-10.

## Responsibility

Keep future external identity/source integration architecturally possible without changing the current local-first runtime or promoting external systems to a product dependency.

## Current operating model

The supported runtime remains:

```text
local username/password
    -> LocalPasswordAuthenticator
    -> authenticated NAPMS actor
    -> server-side session/request actor
    -> application use case
    -> Authority Management action/scope admission
```

Local authentication is not a temporary test-only mechanism. It is the primary current authentication path.

Authority Management, ACC and Resource Catalogue continue to use NAPMS-owned local state for the current product.

## Optional external identity seam

A future external adapter may terminate at the following dormant seam:

```text
external authentication mechanism
    -> outer adapter verifies provider/protocol mechanics
    -> VerifiedExternalIdentity
    -> ActorIdentityResolver
    -> Mapped | Unmapped | Ambiguous | Unknown
    -> authenticated NAPMS actor
    -> existing session/application boundary
```

The seam is intentionally source-neutral. Domain/application modules shall not depend on OIDC/OAuth2/JWT/vendor SDK types.

Exactly one effective actor mapping is required. `Unmapped`, `Ambiguous` and `Unknown` fail closed.

The optional seam does not require a concrete IdP, HTTP callback route, persistent actor-mapping repository or provider configuration in I23.

## Authority boundary

Authentication establishes actor identity only. Authority Management remains the owner of business permission.

No local or future external authentication adapter may answer business authorization itself.

If a future IdP exposes groups/roles/claims, those values remain authentication-source facts until an explicit Authority-owned mapping/import requirement is accepted.

## Optional source-adapter seams

For any future external source, the boundary is:

```text
external source
    -> source-specific adapter
    -> context-owned import/projection contract
    -> context application service
    -> context-owned repository/state
```

Authority Management, ACC and Resource Catalogue each retain semantic ownership. There is no shared enterprise-source domain model and no direct cross-context source-table ownership.

I23 does not implement synchronization engines, schedulers, transport protocols, external schemas, completeness/deletion semantics or production source adapters.

## Deterministic proof

The only executable external-integration proof required by I23 is a deterministic in-process stub where useful.

For identity, the existing skeleton proves:
- provider-qualified external subject identity;
- deterministic mapping;
- `Mapped | Unmapped | Ambiguous | Unknown` outcomes;
- fail-closed behavior.

This proves an extension point only. It does not prove a real provider integration.

## Dependency direction

```text
Domain
  <- Application / consuming ports
      <- optional outer adapters
          <- runtime/composition
```

The default runtime need not instantiate optional external adapters at all.

## Consequences

Positive:
- the current local product stays simple and self-contained;
- future external integration has an explicit place to attach if ever required;
- no speculative enterprise infrastructure or domain semantics are introduced;
- business authorization remains independent from authentication mechanics.

Trade-off:
- real enterprise/provider compatibility is deliberately unimplemented and unproven;
- any future concrete integration will require its own accepted requirements and adapter work.

## Deferred until explicitly required

- IdP vendor and OIDC/OAuth2 details;
- external actor provisioning/mapping persistence;
- external Authority source;
- external ACC/Resource sources;
- CMDB/directory integration;
- Legacy/MSSQL bridge;
- source synchronization/freshness/completeness/deletion behavior.

None of these is a prerequisite for the current local NAPMS product.

## References

- requirements: `docs/requirements/enterprise-identity-authoritative-sources.md`;
- cross-cutting architecture: `docs/architecture/current-architecture.md`;
- semantic ownership: `docs/domain/semantic-ownership.md`;
- active execution: `docs/plans/active/PLAN-037-i23-enterprise-identity-authoritative-sources.md`.
