# Optional External Identity and Source Extension requirements

Status: `accepted I23 optional-extension contract`.

Date: 2026-09-10.

## Purpose

Define only the architectural extension points required to keep future external identity/source integration possible without making it part of the current product operating model.

The current supported mode is local. Local authentication, local Authority data, local Application Communication Catalogue data and local Resource Catalogue data remain first-class product behavior.

## Local-first operation

NAPMS shall continue to support local username/password authentication as the primary runtime authentication path.

NAPMS shall not require an external IdP, directory, CMDB, application catalogue, resource inventory, MSSQL bridge or other enterprise system for normal operation.

Future external integration is optional and shall be activated only by an explicit accepted requirement selecting a concrete source/provider.

## Optional external identity seam

If a future authentication adapter verifies an external identity, it may present that identity to NAPMS as a stable subject key qualified by its provider/issuer identity.

NAPMS may map such a verified external subject to exactly one NAPMS actor identity through a source-neutral mapping seam.

Mapping outcomes are:
- `Mapped` — exactly one active NAPMS actor is established;
- `Unmapped` — no actor mapping exists;
- `Ambiguous` — more than one effective mapping exists;
- `Unknown` — required mapping evidence cannot be established.

Only `Mapped` establishes an actor. All other outcomes fail closed.

This seam is optional extension infrastructure. It does not replace the current local login flow and does not require an HTTP/OIDC callback or provider-specific implementation.

## Authority separation

Authentication identifies an actor. Authority Management remains the sole owner of NAPMS business authorization.

External claims, groups, roles or token scopes, if ever introduced, shall not directly grant NAPMS business authority.

## Session behavior

Current server-side local sessions remain valid product behavior.

A future external authentication adapter may establish the same NAPMS actor/session boundary after successful mapping, but no such adapter is required by I23.

Sessions shall not encode a durable business-authority snapshot; application use cases continue to query Authority Management.

## Optional external source seams

Authority Management, Application Communication Catalogue and Resource Catalogue remain semantic owners of their domain state.

If a future external source adapter is introduced, it shall terminate at a context-owned import/projection boundary rather than exposing vendor transport models to Domain or creating shared mutable source tables across contexts.

External identifiers remain source/correlation identifiers unless the owning bounded context explicitly defines a stronger identity relationship.

No source synchronization engine, transport, scheduler, completeness protocol, deletion model or production source contract is required by I23.

## Deterministic stubs

Deterministic in-process stubs are sufficient for I23 where an executable proof is useful.

Such stubs prove only that the extension seam is coherent and fail-closed. They do not claim compatibility with any real provider, protocol or external source.

## Acceptance examples

### Local login remains primary

Given the default local runtime, when a configured local user authenticates with username/password, then NAPMS establishes the existing local server-side session without requiring any external identity provider.

### Optional external identity maps deterministically

Given a deterministic verified external identity stub and exactly one active mapping, when the mapping seam is invoked, then it returns `Mapped` with the corresponding NAPMS actor.

### Optional external identity fails closed

Given an unmapped, ambiguous or unknown external subject, when the mapping seam is invoked, then no NAPMS actor is established.

### Identity does not grant authority

Given either a locally authenticated actor or a future externally mapped actor, when the actor invokes a protected application action, then Authority Management decides action/scope admission independently from authentication.

## Explicit non-goals

I23 does not require:
- OIDC/OAuth2 implementation;
- corporate IdP integration;
- replacement of local password authentication;
- external Authority administration;
- ACC/Resource external synchronization;
- Legacy/MSSQL integration;
- real-source freshness, completeness or deletion guarantees;
- production external-source transport compatibility.

Those concerns remain deferred unless a future accepted requirement makes one concrete integration necessary.
