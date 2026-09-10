# ADR-008 — I27 Catalogue Mutation Authority

Status: `accepted`.

Date: 2026-09-10.

## Context

I27 adds user-facing mutations to Application Communication Catalogue and Resource Catalogue. Existing catalogue visibility is intentionally broader than mutation authority, and Resource Responsibility / Resource Scope Affiliation are not permissions.

The mutation model needs enough granularity to separate application-communication curation from resource curation without creating a large matrix of field-level permissions before a concrete need exists.

## Decision

I27 introduces two Authority Management actions:

```text
CurateApplicationCatalogue
CurateResourceCatalogue
```

### CurateApplicationCatalogue

Admits ACC-owned curation for the selected Responsibility Scope context, including:

- Application create/rename/retire;
- Component create/rename/retire;
- Component Deployment create/rename/retire;
- DCS revision authoring;
- Deployment Resource Binding create/end.

This action does not imply `ProposeConnectivity`, `DecideConnectivity`, Access Rule mutation or Resource Catalogue mutation.

### CurateResourceCatalogue

Admits Resource Catalogue curation for the selected Responsibility Scope context, including:

- Resource create/rename/retire;
- endpoint/realization authoring;
- Resource Scope Affiliation create/end where the command is scoped to the admitted Responsibility Scope;
- Resource Responsibility create/end.

This action does not imply ACC mutation, Connectivity Requirement/Decision/Rule authority or network operation authority.

## Scope model

Both actions are evaluated by Authority Management using the existing stable Responsibility Scope reference.

For commands affecting an existing scoped object, the backend derives/validates the applicable scope from authoritative catalogue relations rather than trusting a caller-provided object owner field.

For creation commands that need an initial Responsibility Scope, the HTTP request selects a scope from actor-admitted `Curate*Catalogue` scopes. The server treats it as command context, not as trusted actor identity.

ACC structural identities are not themselves owned by a Responsibility Scope in I27. ACC curation authority uses the selected curation scope as an administrative action boundary; it does not add scope into Application/Component/Deployment identity. A later requirement may introduce more precise catalogue stewardship without changing those identities.

Deployment Resource Binding requires `CurateApplicationCatalogue` in the selected curation scope. Referencing a Resource does not grant or require Resource Catalogue mutation because the command mutates only the ACC-owned binding.

Resource Scope Affiliation creation/end for scope `S` requires `CurateResourceCatalogue` for `S`.

## Why two actions

One generic `CurateCatalogue` action is rejected because ACC and RC are independent semantic owners and are likely to have different operational custodians.

Fine-grained actions such as `RenameComponent`, `RetireComponent`, `SetResourceEndpoint` are deferred because no current user scenario requires that administrative complexity. The two-context split is the smallest useful separation.

## Read visibility

Existing catalogue read/discovery visibility remains independent. Having `CurateApplicationCatalogue` or `CurateResourceCatalogue` does not widen protected Requirement/Decision/Rule reads.

UI may expose curation workspaces only for admitted scopes/actions for usability, but HTTP commands always re-check Authority Management.

## Local demo

The local demo actor may receive both new actions for `local-demo` so the supported single-account local product can exercise the full curation workflow.

This is demo authority data, not a rule that authenticated users universally receive catalogue mutation rights.

## Consequences

- ACC and RC mutation authority remain independently assignable;
- the first slice avoids field-level RBAC complexity;
- Resource responsibility/contact remains operational metadata, not permission;
- the shared Responsibility Scope is used as an authority correlation value without becoming Application/Component identity;
- application/backend implementation can introduce the two actions without changing existing authorization semantics.
