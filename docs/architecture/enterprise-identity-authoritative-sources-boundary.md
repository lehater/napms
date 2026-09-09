# Enterprise Identity and Authoritative Source Integration architecture boundary

Status: `accepted I23 boundary`.

Date: 2026-09-10.

## Responsibility

Define the infrastructure/application boundary for enterprise authentication and authoritative source ingestion while preserving existing NAPMS semantic ownership.

## Identity flow

```text
external IdP / authentication mechanism
    -> outer authentication adapter verifies protocol/credential mechanics
    -> VerifiedExternalIdentity
    -> ActorIdentityResolver
    -> MappedActor | Unmapped | Ambiguous | Unknown
    -> server-side session / request actor
    -> application use case
    -> Authority Management action/scope admission
```

The authentication adapter owns protocol mechanics. Actor mapping owns external-subject to NAPMS-actor correlation. Authority Management owns business permission. These responsibilities remain separate.

### Core contracts

The runtime/application-facing authentication seam uses source-neutral values equivalent to:
- `ExternalIdentityProviderId` / issuer identity;
- `ExternalSubjectId`;
- optional display/login metadata that is non-authoritative;
- verification provenance/time when relevant;
- `ActorId` after mapping.

Protocol-specific token/claim/library types remain in outer adapters.

Actor mapping is deterministic and fail-closed. Exactly one effective mapping is required. The mapping repository may be persisted later in I23; its schema is NAPMS-owned and independent from Authority Management grants.

## Session boundary

Server-side sessions contain authenticated actor identity and authentication/session metadata only. They do not snapshot business authority as durable permission truth.

Application authority remains evaluated through existing Authority Management ports at the use-case boundary. This preserves revocation/change semantics independently from authentication session lifetime.

The current local-password authenticator is retained only as a local/test outer adapter behind the same runtime seam.

## Authoritative source flow

For each source-owning NAPMS context:

```text
enterprise source
    -> source-specific transport/parser adapter
    -> context-owned import projection
    -> validation/correlation/completeness decision
    -> context application service
    -> context-owned repository/state
```

Authority Management, ACC and Resource Catalogue each own their import projection contract. There is no shared generic enterprise-record domain model that becomes authoritative across contexts.

Composition may schedule/coordinate imports, but it does not interpret source semantics or write another context's tables directly.

## Provenance and synchronization

Every import-capable context preserves source provenance sufficient for deterministic correlation and diagnosis.

Idempotency is keyed by source identity plus source revision/version when the accepted source contract provides a meaningful revision. When no source revision exists, the adapter must derive an explicit stable observation/correlation key from accepted source semantics rather than transport ordering.

Deletion/retirement requires positive evidence of authoritative scope completeness or explicit tombstone semantics. Partial fetch absence is not deletion evidence.

Ambiguous correlation, conflicting same-revision content, invalid projection and unknown source completeness fail closed.

## Authority source boundary

Identity-provider groups/roles/claims are authentication-source facts. They become Authority Management facts only through an explicit Authority-owned mapping/import contract.

No HTTP middleware, session object or OIDC adapter may answer business authorization from IdP claims directly.

## Catalogue source boundaries

ACC source adapters project source interactions/components into ACC-owned catalogue semantics. Resource source adapters project source resources/endpoints/affiliations into Resource Catalogue-owned semantics.

Source IDs remain provenance/correlation identities unless the owning context explicitly defines them as its domain identity. Cross-context joins continue through existing owner/application projections rather than shared source tables.

## First executable I23 slice

Because no concrete enterprise IdP/source products or endpoints are selected in repository truth, the first executable slice shall use deterministic in-process adapters for:
- verified external identity input;
- actor mapping success/unmapped/ambiguous/unknown;
- representative source import success/conflict/incomplete-scope cases.

This opens source-neutral core/runtime integration without falsely claiming vendor compatibility.

A real OIDC/provider adapter or real Authority/ACC/Resource transport is admitted only after concrete issuer/source configuration, schema/correlation and completeness semantics are accepted.

## Dependency direction

```text
Domain
  <- context Application / consuming ports
      <- enterprise-source and authentication adapters
          <- runtime/composition
```

Domain imports no OIDC/OAuth2/JWT/HTTP/SDK/vendor types.

Authority Management, ACC and Resource Catalogue do not depend on runtime authentication implementation.

## Consequences

Positive:
- production identity can replace local password mechanics without rewriting use cases;
- business authority remains independently revocable and explainable;
- source products can vary without transferring semantic ownership;
- deterministic stubs can prove I23 contracts before enterprise endpoints exist.

Trade-off:
- I23 requires explicit actor/source correlation state instead of treating external claims as application-native identities/permissions;
- real integration closure remains impossible until source-specific completeness, correlation and transport evidence exists.

## Deferred environment choices

Deferred until selected evidence exists:
- IdP vendor and OIDC/OAuth2 details;
- actor provisioning administration workflow beyond deterministic mapping contract;
- Authority source product/schema;
- ACC/Resource source product/schema/transport;
- Legacy/MSSQL bridge;
- secret/TLS/HA/production token-storage hardening, which belongs to I24 except where required for a concrete I23 protocol proof.

## References

- requirements: `docs/requirements/enterprise-identity-authoritative-sources.md`;
- cross-cutting architecture: `docs/architecture/current-architecture.md`;
- semantic ownership: `docs/domain/semantic-ownership.md`;
- active execution: `docs/plans/active/PLAN-037-i23-enterprise-identity-authoritative-sources.md`.
