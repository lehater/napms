# ADR-008 — I27 Catalogue Mutation Authority

Status: `accepted; corrected during Stage 0 implementation re-entry`.

Date: 2026-09-10.

## Context

I27 adds user-facing mutations to Application Communication Catalogue and Resource Catalogue. Existing catalogue visibility is intentionally broader than mutation authority, and Resource Responsibility / Resource Scope Affiliation are not permissions.

The mutation model needs enough granularity to separate application-communication curation from resource curation without creating a large matrix of field-level permissions before a concrete need exists.

During implementation re-entry, the initial idea of evaluating catalogue curation against a caller-selected Responsibility Scope was found unsafe/underspecified: ACC structural identities do not belong to a Responsibility Scope, and RC Resource Scope Affiliation is explicitly membership data rather than catalogue stewardship. A caller-selected arbitrary scope therefore could not be authoritatively correlated to the mutated catalogue object.

## Decision

I27 introduces two Authority Management actions:

```text
CurateApplicationCatalogue
CurateResourceCatalogue
```

The first I27 slice evaluates them against server-owned fixed administrative scope references:

```text
CurateApplicationCatalogue -> application-catalogue
CurateResourceCatalogue    -> resource-catalogue
```

These are Authority Management scope correlation values only. They are not Responsibility Scope membership, Application/Resource identity, organization hierarchy or ownership facts.

### CurateApplicationCatalogue

Admits ACC-owned curation, including:

- Application create/rename/retire;
- Component create/rename/retire;
- Component Deployment create/rename/retire;
- DCS revision authoring;
- Deployment Resource Binding create/end.

The application command chooses `application-catalogue` as the authority scope. The client does not select or substitute this value.

This action does not imply `ProposeConnectivity`, `DecideConnectivity`, Access Rule mutation or Resource Catalogue mutation.

### CurateResourceCatalogue

Admits Resource Catalogue curation, including:

- Resource create/rename/retire;
- endpoint/realization authoring;
- Resource Scope Affiliation create/end;
- Resource Responsibility create/end.

The application command chooses `resource-catalogue` as the authority scope. The client does not select or substitute this value.

This action does not imply ACC mutation, Connectivity Requirement/Decision/Rule authority or network operation authority.

## Why fixed catalogue administration scopes

The current domain contains no accepted catalogue-stewardship relation that maps an ACC Application/Component/Deployment or RC Resource to one mutation-governance Responsibility Scope.

Using Resource Scope Affiliation as implicit Resource-catalogue stewardship would change its accepted meaning. Using an arbitrary UI-selected scope for ACC would provide no object-to-scope invariant at all.

The fixed scopes therefore provide the smallest fail-closed first slice:

```text
catalogue curator authority
!= Resource Scope Affiliation
!= Resource Responsibility
!= application/resource ownership
```

If later product requirements need delegated per-company/per-team catalogue curation, that requires an explicit stewardship/governance relation and a domain re-entry rather than overloading current membership/contact facts.

## Deployment Resource Binding

A Deployment Resource Binding mutation requires `CurateApplicationCatalogue` on `application-catalogue`, because the binding is ACC-owned.

Referencing a Resource does not grant Resource Catalogue mutation and does not require `CurateResourceCatalogue` merely to create/end the ACC relation. The command still validates that the Resource reference exists through the accepted consuming port.

## Resource Scope Affiliation

Creating or ending a Resource Scope Affiliation requires `CurateResourceCatalogue` on `resource-catalogue`.

The target Responsibility Scope is semantic data of the affiliation command, not the authority scope used to admit the catalogue mutation.

## Why two actions

One generic `CurateCatalogue` action is rejected because ACC and RC are independent semantic owners and may have different operational custodians.

Fine-grained actions such as `RenameComponent`, `RetireComponent`, `SetResourceEndpoint` are deferred because no current user scenario requires that administrative complexity. The two-context split is the smallest useful separation.

## Read visibility

Existing catalogue read/discovery visibility remains independent. Having `CurateApplicationCatalogue` or `CurateResourceCatalogue` does not widen protected Requirement/Decision/Rule reads.

UI may expose curation actions based on the two server-known authority capabilities for usability, but HTTP commands always re-check Authority Management.

## Local demo

The local demo actor receives:

```text
CurateApplicationCatalogue @ application-catalogue
CurateResourceCatalogue    @ resource-catalogue
```

so the supported single-account local product can exercise the full curation workflow.

This is demo authority data, not a rule that authenticated users universally receive catalogue mutation rights.

## Consequences

- ACC and RC mutation authority remain independently assignable;
- the client cannot authorize a catalogue mutation by substituting an unrelated Responsibility Scope;
- Resource scope membership and operational responsibility/contact remain data, not permission;
- the first slice avoids inventing catalogue stewardship relations before they are required;
- delegated scope-specific catalogue curation remains explicit future domain work rather than an accidental interpretation of current relations.
