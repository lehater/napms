# Resource Catalogue — Tactical Model

Status: `S2 MVP Tactical model revalidated 2026-09-16`.

## Purpose

Define the minimum Tactical DDD semantics Resource Catalogue must own for the MVP happy path while preserving accepted Resource curation, scope-affiliation and responsibility semantics.

The current target realization contract in `target-realization-model.md` is authoritative. The former `ResourceRealizationVersion -> EndpointAddress+` model is superseded and is not part of the current target.

## MVP modelling rule

Model only identities, invariants and operations required to express accepted Resource semantics and the first end-to-end access-policy path.

Do not introduce interfaces, endpoints, VIPs, listeners, deployment-specific exposure, provider-runtime identities, address-set aggregates or revision workflows until a confirmed use case requires them.

## Core model

```text
Resource
    ResourceId
    displayName?
    lifecycle: Active | Retired

ResourceAddressFact
    ResourceAddressFactId
    ResourceRef
    AddressSpace: HostAddress | Prefix
    [validFrom, validUntil)
    provenanceReference
    endProvenanceReference?

CurrentResourceRealization(ResourceRef, logicalTime)
    -> AddressSpace? : HostAddress | Prefix
```

### Resource

`Resource` is the stable RC-owned semantic identity of an access-relevant resource.

`ResourceId` remains the same when the Resource is renamed, its address changes, its responsibility changes, its scope affiliation changes, or a Component Deployment starts/stops referencing it.

`ResourceRef` is the opaque cross-context reference to that identity. Consumers do not depend on RC storage keys or private realization records.

The retained MVP lifecycle is:

```text
Active -> Retired
```

Retirement preserves historical identity and facts. Richer lifecycle states and restoration semantics are deferred.

### AddressSpace

`AddressSpace` is a value object with exactly one of:

```text
HostAddress
Prefix
```

Its value is the corporate-visible address or prefix meaningful for access management. A Prefix remains a Prefix; RC does not expand it into hosts.

AddressSpace has no independent identity or lifecycle.

### ResourceAddressFact

`ResourceAddressFact` records one authoritative address realization of one Resource for a validity interval.

Its identity exists only to preserve historical fact/provenance continuity. It does not represent an endpoint, interface, listener or deployment binding.

Changing the effective address does not change `ResourceId`. It ends the previous effective address fact, when one exists, and establishes another fact for the same Resource.

For one Resource at one logical time, at most one ResourceAddressFact may be effective.

Absence of an effective ResourceAddressFact is valid and means the current Resource realization has no resolved AddressSpace. It must remain distinguishable from an empty set of required access.

Creation provenance and later end provenance are distinct business facts:

```text
provenanceReference
endProvenanceReference?
```

The exact persistence/versioning mechanism is not Tactical domain truth.

## Authoritative versus derived state

Authoritative RC truth:

- Resource identity and lifecycle;
- ResourceAddressFact history;
- Resource Scope Affiliation history;
- Resource Responsibility history.

Derived semantic projection:

```text
CurrentResourceRealization {
    resourceRef
    addressSpace? : HostAddress | Prefix
    asOf
    resolution/completeness
    provenance/freshness reference
}
```

`CurrentResourceRealization` is a published semantic projection over RC truth. It is not a second owner of Resource identity or address history.

## Minimal address operations

```text
CreateResource
SetResourceAddressSpace
ReplaceResourceAddressSpace
```

`CreateResource` establishes Resource identity.

`SetResourceAddressSpace` establishes an address fact when no effective address fact exists for the requested logical time.

`ReplaceResourceAddressSpace` expresses the domain meaning “the previous effective address stops here and this address becomes effective here”, preserving provenance of both facts.

Exact command/API names, transaction shape, optimistic-lock fields and database representation belong downstream unless a later requirement makes them semantic.

Explicit address clearing without replacement is deferred until a confirmed user journey requires it.

## Resource Scope Affiliation

```text
ResourceScopeAffiliation
    AffiliationId
    ResourceRef
    ResponsibilityScopeRef
    [validFrom, validUntil)
    provenanceReference
    endProvenanceReference?
```

It determines responsibility-oriented scope membership of a Resource. It does not grant actor authority.

For the same Resource + Responsibility Scope + logical time, at most one equivalent affiliation is effective.

Access Policy consumes this published truth to determine source/destination approval obligations for a concrete Policy Rule endpoint Resource. RC does not decide those obligations.

## Resource Responsibility

```text
ResourceResponsibility
    ResourceRef
    ResponsiblePartyRef
    partyKind: Person | Team
    role: ServiceOwner | TechnicalOwner | OperationsContact | BusinessOwner
    displayName
    contactPoint?
    [validFrom, validUntil)
    provenanceReference
    endProvenanceReference?
```

Resource Responsibility records who is responsible for the Resource. It does not place the Resource into a Responsibility Scope and does not grant NAPMS mutation or policy-decision authority.

## Cross-context contract

Application Deployment references only Resource identity:

```text
AD ComponentDeployment.ResourceRef
        -> RC Resource
```

When policy materialization needs an address:

```text
ComponentDeployment.ResourceRef
        -> CurrentResourceRealization(ResourceRef, logicalTime)
        -> AddressSpace? = HostAddress | Prefix
```

AD does not copy or own the address. Address changes therefore do not change `ComponentDeployment` identity.

For Evidence Access Recognition, RC may publish address-to-Resource correlation semantics sufficient to resolve an observed address to zero/one/many matching Resources. Ambiguous or missing correlation is not silently resolved by RC or the recognition composition.

RC does not own Application, Component, Interaction, ComponentDeployment, Policy Rule, authorization/governance decisions or enforcement-device semantics.

## Invariants for the current scope

1. `ResourceId` is stable across address, deployment-reference, scope and responsibility changes.
2. One Resource has at most one effective AddressSpace at one logical time.
3. AddressSpace is exactly one HostAddress or one Prefix when resolved.
4. Address history remains explainable through fact validity and provenance.
5. A missing current AddressSpace is explicit unresolved realization, not an empty access requirement.
6. Resource Scope Affiliation, Resource Responsibility and actor authority remain separate meanings.
7. Cross-context consumers use opaque ResourceRef plus published RC projections, not RC-private fact identities.
8. Resource AddressSpace change never changes PolicyRule or ComponentDeployment identity by itself.

## Deliberately deferred beyond this MVP checkpoint

- several simultaneous addresses/prefixes for one Resource;
- interface or endpoint identity;
- management/data-plane separation;
- VIP/listener modelling;
- deployment-specific network exposure;
- NAT calculation;
- generic CMDB/asset-inventory semantics;
- richer Resource lifecycle/restoration;
- explicit address clearing workflow unless demanded by a user journey;
- persistence schema, ORM model, ETag/version columns and migration mechanism.

## Tactical coherence result

For the current RC scope:

- identity remains explicit and independent from address/deployment realization;
- current address realization remains RC-owned derived projection;
- ComponentDeployment references Resource identity directly;
- Access Policy consumes scope affiliation without transferring authority ownership;
- evidence recognition may correlate addresses without making RC an authorization owner;
- no new RC aggregate or endpoint model is required by the revalidated first MVP.
