# Enterprise Identity and Authoritative Source Integration requirements

Status: `accepted I23 integration contract`.

Date: 2026-09-10.

## Purpose

Define observable I23 behavior for enterprise authentication and authoritative Authority/ACC/Resource source integration without selecting or inventing unavailable enterprise products, schemas or endpoints.

## Authentication and actor identity

NAPMS shall accept authenticated identity only from a trusted server-side authentication boundary.

A verified external identity shall be represented by a stable external subject key qualified by its identity-provider/issuer identity. Request payload fields shall not establish actor identity.

NAPMS shall map a verified external subject to exactly one NAPMS actor identity before application use cases execute.

Mapping outcomes are:
- `Mapped` — exactly one active NAPMS actor is established;
- `Unmapped` — no actor mapping exists;
- `Ambiguous` — more than one effective mapping exists;
- `Unknown` — required mapping evidence cannot be established.

Only `Mapped` establishes an authenticated NAPMS actor. All other outcomes fail closed.

Authentication proves actor identity only. Authentication claims, groups, roles or token scopes do not directly grant NAPMS business authority.

## Authority separation

After actor establishment, each application use case continues to evaluate its action/scope-specific authority through Authority Management.

External identity-provider claims may be source evidence for a separately accepted Authority Management integration adapter only when an explicit source mapping contract exists. They shall not bypass Authority Management admission semantics.

Unknown or ambiguous required authority remains non-permission.

## Session behavior

The HTTP runtime may establish a server-side session from a successfully mapped actor. Session identifiers remain opaque to clients and shall not encode business authority.

Session expiry/revocation invalidates authentication state only; subsequent business authorization is still evaluated through Authority Management.

Local username/password authentication may remain available only as an explicitly local/test adapter. It is not the production identity contract.

## Authoritative source imports

Authority Management, Application Communication Catalogue and Resource Catalogue remain semantic owners of their NAPMS domain state.

An enterprise source adapter shall translate source-owned records through an explicit import/projection contract owned by the consuming NAPMS module. The adapter shall not expose source/vendor transport models to Domain.

Each accepted source record/projection shall preserve enough provenance to identify:
- source system identity;
- source record identity or stable correlation key;
- source-observed/effective time when supplied by the source contract;
- NAPMS import/observation time;
- source revision/version when supplied and semantically relevant.

Source import outcomes shall distinguish at least:
- accepted/usable projection;
- rejected invalid projection;
- ambiguous correlation/mapping;
- unknown source state.

Required source data that is incomplete, ambiguous or unknown shall not silently become authoritative domain truth.

## Synchronization and deletion semantics

No source adapter may infer destructive deletion merely because a record is absent from one partial or failed fetch.

A source may drive retirement/removal only when its accepted contract establishes that the observation is complete for the relevant scope and that absence/tombstone semantics are authoritative.

Replay of the same source revision/projection shall be idempotent for the same semantic fact.

Conflicting reuse of the same source identity/revision with different semantic content shall fail closed and remain diagnosable.

## Catalogue identity

External identifiers shall be retained as source/correlation identities and shall not silently replace established NAPMS domain identities unless the owning bounded-context model explicitly defines that identity relationship.

Cross-context source ingestion shall not create direct table ownership or shared mutable catalogue records between Authority Management, ACC and Resource Catalogue.

## Deterministic proof when real enterprise systems are unavailable

When concrete enterprise IdP/source mechanics are not selected or reachable, I23 may use deterministic in-process verified-identity/source stubs to prove the source-neutral application semantics.

Such proof establishes only the NAPMS integration contract. It does not claim compatibility with any real IdP, directory, catalogue, API or transport.

## Acceptance examples

### Verified identity maps to actor, authority allows

Given a trusted authentication adapter verifies external subject `(issuer-a, subject-17)` and exactly one active mapping resolves it to actor `alice`, when the actor invokes an application action, then the action uses actor `alice` and evaluates Authority Management separately before execution.

### Valid token claims do not grant business authority

Given a verified external identity includes a group/role claim that resembles an application role, when no Authority Management admission exists for the requested action/scope, then the action is denied/unknown according to existing Authority semantics; the claim does not grant permission.

### Ambiguous actor mapping

Given one verified external subject resolves to two effective NAPMS actors, when authentication completes, then no authenticated actor/session is established and the outcome is `Ambiguous`.

### Partial source fetch cannot delete state

Given an authoritative source fetch is incomplete or its completeness cannot be proven, when an existing NAPMS catalogue item is absent from that fetch, then the adapter does not retire/delete the item merely from absence.

### Conflicting source revision

Given source identity `S:42` revision `7` has already been imported with semantic payload A, when the same identity/revision arrives with semantic payload B, then the import fails closed instead of overwriting A as if it were the same fact.

## Explicit unknowns

The following remain environment choices, not accepted product facts:
- concrete IdP/vendor/issuer;
- OIDC/OAuth2 client registration details and claim mapping;
- concrete Authority administration/source product;
- concrete ACC/Resource source products, schemas, transports and freshness/SLA contracts;
- Legacy/MSSQL bridge need.

These unknowns block claims of real enterprise transport compatibility, but do not block source-neutral I23 contract/core implementation with deterministic stubs.
