# PLAN-037 — I23 Enterprise Identity and Authoritative Source Integration

Status: `active — WP2 enterprise authentication seam`.

Date: 2026-09-10.

## Goal

Replace I8-era local/demo identity and seed-only source dependencies with explicit enterprise-facing integration boundaries while preserving the semantic ownership established by Authority Management, Application Communication Catalogue and Resource Catalogue.

I23 must not invent a corporate IdP, directory, catalogue product, endpoint, schema or Legacy/MSSQL dependency that is not selected by accepted evidence.

## Current baseline

Accepted/known:
- runtime authentication is currently a replaceable local/test username/password authenticator with opaque in-memory server-side sessions;
- application authorization is already independent from authentication and is owned by Authority Management action/scope admission semantics;
- ACC and Resource Catalogue are first-class bounded contexts with NAPMS-owned models and PostgreSQL persistence;
- local seed data currently supplies development identities/authority/catalogue records;
- the roadmap requires enterprise identity/source integration before production hardening;
- Legacy/MSSQL is not selected by default.

Unknown and therefore not to be invented:
- concrete corporate IdP/vendor and issuer metadata;
- exact OAuth2/OIDC client registration, redirect URIs, claims and group mappings;
- authoritative Authority administration system and external schema;
- authoritative ACC/Resource source products, APIs, delivery modes and freshness/SLA contracts;
- external Decision/provider integration endpoints.

## Architectural intent

Authentication proves an external subject and establishes a NAPMS actor identity. Authority Management decides what that actor may do. Enterprise identity claims must not become implicit business authority.

Authoritative source adapters translate source-owned records into explicit import/projection contracts. They must preserve source identity, observation/import time and provenance and must fail closed on ambiguous or incomplete mappings. Source integration must not move domain semantics into runtime/composition code.

## Work packages

### WP1 — Re-enter identity/source boundaries

Status: `done`.

Artifacts:
- `docs/requirements/enterprise-identity-authoritative-sources.md`;
- `docs/architecture/enterprise-identity-authoritative-sources-boundary.md`.

Exit achieved:
- identity != authority is explicit;
- NAPMS actor mapping responsibility is explicit;
- source import vs domain ownership is explicit;
- unknown concrete enterprise systems remain named unknowns rather than guessed implementations.

### WP2 — Enterprise authentication seam

Status: `active`.

Implement a protocol-facing authentication boundary that can consume a verified external identity result without coupling domain/application modules to OIDC libraries or token formats. Preserve the local authenticator only as an explicitly local/test adapter.

First executable proof may use a deterministic in-process verified-identity stub when no concrete IdP configuration is available.

Exit:
- HTTP/runtime composition can consume an authentication abstraction rather than depending semantically on local-password behavior;
- external subject -> NAPMS actor mapping is explicit and deterministic;
- unmapped/ambiguous/unknown identity fails closed;
- authority remains a separate Authority Management query.

### WP3 — Authority source integration contract

Status: `unblocked after WP1; queued behind WP2`.

Define source-neutral ingestion/synchronization semantics for Authority Management without converting IdP claims/groups directly into authorization decisions.

Exit:
- external source records can be projected into Authority-owned state with source/provenance identity;
- duplicate/ambiguous/stale input has explicit fail-closed behavior;
- local seed remains dev-only.

### WP4 — ACC and Resource Catalogue source integration contracts

Status: `unblocked after WP1; queued behind WP2/WP3`.

Define owner-preserving import/synchronization adapters for ACC and Resource Catalogue.

Exit:
- import contracts preserve canonical external identities and source provenance;
- invalid partial mappings cannot silently create authoritative catalogue facts;
- ingestion does not create cross-context ownership.

### WP5 — Runtime composition

Status: `blocked on WP2-WP4`.

Wire selected enterprise adapters when concrete source evidence exists. Where source products are unavailable, wire deterministic source stubs only for semantic integration proof and mark real transport unproven.

Exit:
- runtime no longer requires demo credentials/seeded source data for the I23 integration path;
- local development path remains explicit and isolated.

### WP6 — End-to-end acceptance proof

Status: `blocked on WP5`.

Prove:

```text
verified external identity
    -> mapped NAPMS actor
    -> Authority Management admission
    -> authoritative ACC/RC source projection
    -> existing connectivity/policy use case
```

Adversarial cases must cover unmapped identity, ambiguous actor mapping, unknown source state and incomplete catalogue projection.

### WP7 — Final gates and absorption

Status: `blocked on WP6`.

Run relevant repository/Web/PostgreSQL gates, absorb durable truth into requirements/domain/architecture/engineering state, remove the completed active plan and promote I24 only if I23 closure is truthful.

## Current gate

WP2 is open for source-neutral authentication and deterministic identity mapping. Concrete provider adapters remain closed because the repository contains no accepted concrete enterprise IdP/source selection.

## Next action

Implement the verified-external-identity + actor-resolution seam and deterministic fail-closed proof, then review whether the existing HTTP dependency type can be generalized without changing the local UI contract.
