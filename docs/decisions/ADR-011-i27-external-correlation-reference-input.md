# ADR-011 — I27 External Correlation Reference Input

Status: `accepted`.

Date: 2026-09-10.

## Context

I27 requires normal Resource Catalogue curation for Resource Scope Affiliation and Resource Responsibility.

Those facts contain references that NAPMS deliberately does not own in the current local-first product:

```text
Resource Scope Affiliation -> Responsibility Scope reference
Resource Responsibility    -> Person/Team reference
```

Responsibility Scope remains an opaque correlation reference rather than a Company/Organization aggregate. Resource Catalogue records responsibility/contact facts but does not own a Person/Team directory identity lifecycle. No external scope registry or directory connector is required by I27.

At the same time, the I27 UI/API contract correctly forbids normal users from manufacturing NAPMS-owned UUID combinations for Application, Component, Component Deployment, DCS or Resource relationships. Treating every reference identically would therefore either block the required Resource workflow or force I27 to invent a new Scope/Party registry bounded context.

## Decision

### Distinguish owned identity from external correlation

I27 distinguishes two reference classes at the product boundary.

NAPMS-owned catalogue references use backend-owned discovery/selection:

```text
Application
Component
Component Deployment
DCS revision
Resource
Deployment Resource Binding targets
```

The normal Web path does not ask users to paste those internal stable identifiers.

Externally-owned correlation references may be entered explicitly when no configured registry/discovery adapter exists:

```text
Responsibility Scope reference
Responsible Person/Team reference
```

The UI must label these fields as external/correlation references rather than as NAPMS object IDs. Their text value is semantic business data for the owning Resource Catalogue fact.

### No identity manufacturing

Accepting an external correlation reference does not create or claim ownership of the referenced Scope, Person or Team.

I27 does not:

- create Company/Organization/Person/Team aggregates from those strings;
- infer a Person/Team reference from the authenticated actor ID;
- infer a Responsibility Scope from `ReadScopedConnectivity` or another authority assignment;
- validate external existence by pretending that Authority Management is a registry;
- derive mutation permission from either external reference.

The Resource Catalogue continues to validate the invariants it owns: non-empty bounded references, supported party kind/role, temporal validity, overlap/state rules and Resource existence/lifecycle.

### Authority remains independent

`CurateResourceCatalogue @ resource-catalogue` remains the server-owned mutation admission rule.

A user-entered Responsibility Scope reference is affiliation business data only. A Person/Team reference and responsibility role are operational/contact data only. Neither can substitute the fixed catalogue authority scope or grant any policy/catalogue permission.

### Future registry integration

A future Responsibility Scope registry or Person/Team directory may provide a discovery adapter for these fields. The Web control can then change from explicit external-reference entry to search/selection without changing Resource Catalogue fact identity, mutation authority or command semantics.

The adapter must remain a reference-validation/discovery dependency; it does not move Resource Scope Affiliation or Resource Responsibility ownership out of Resource Catalogue.

## Alternatives rejected

### Use `ReadScopedConnectivity` scopes as the affiliation registry

Rejected. Read authority/discovery is not evidence that the listed scopes are the complete set of valid business Responsibility Scope references, and it would conflate visibility/read admission with catalogue data.

### Use authenticated actor ID as Person reference

Rejected. Actor identity and responsible-party identity have independent lifecycle and semantics.

### Add a local Company/Organization/Party registry in I27

Rejected. This expands I27 into a new identity/organization bounded context contrary to the accepted non-goals and is not required for the minimum access-domain onboarding flow.

### Allow free text for every relationship

Rejected. NAPMS-owned identities already have authoritative backend discovery and must remain protected from arbitrary client-assembled reference combinations.

## Consequences

- the required C7 Resource onboarding flow can create scope affiliation and responsibility/contact facts without an external enterprise dependency;
- normal ACC/Resource cross-entity relationships still use trusted backend discovery;
- local-first operation remains viable without inventing organization/directory ownership;
- a later registry connector improves selection UX without forcing a Resource Catalogue domain rewrite;
- acceptance tests must prove external correlation input remains business data and does not affect catalogue mutation authority.