# Resource Catalogue — Tactical DDD model

Status: `current target`.

## Purpose

Own stable Resource identity, network AddressSpace realization, Responsibility Scope affiliation and Resource responsibility without importing Application Deployment or authorization meaning.

## Resource

```text
Resource {
    resourceId
    displayName?
    lifecycle: Active | Retired
}
```

`ResourceId` is stable across rename, address, placement, scope-affiliation and responsibility changes. Cross-context consumers use opaque `ResourceRef`.

## Address realization

```text
ResourceAddressFact {
    resourceAddressFactId
    resourceRef
    addressSpace: HostAddress | Prefix
    validFrom
    validUntil?
    provenanceReference
    endProvenanceReference?
}
```

For one Resource at one logical time, at most one ResourceAddressFact is effective. An AddressSpace is exactly one `HostAddress` or one `Prefix`; a Prefix is not expanded into hosts by RC.

Changing AddressSpace does not change Resource identity. Absence of an effective AddressSpace is valid unresolved realization and must not be interpreted as an empty required-access set.

Current published realization:

```text
CurrentResourceRealization {
    resourceRef
    addressSpace?: HostAddress | Prefix
    asOf
    resolution/completeness
    provenance/freshness reference
}
```

## Resource Scope Affiliation

```text
ResourceScopeAffiliation {
    affiliationId
    resourceRef
    responsibilityScopeRef
    validFrom
    validUntil?
    provenanceReference
    endProvenanceReference?
}
```

Scope affiliation describes responsibility-oriented membership. It does not grant actor authority.

## Resource Responsibility

```text
ResourceResponsibility {
    resourceRef
    responsiblePartyRef
    partyKind: Person | Team
    role: ServiceOwner | TechnicalOwner | OperationsContact | BusinessOwner
    displayName
    contactPoint?
    validFrom
    validUntil?
    provenanceReference
    endProvenanceReference?
}
```

Responsibility records who is responsible for a Resource; it does not grant NAPMS authority.

## Domain operations

```text
CreateResource
SetResourceAddressSpace
ReplaceResourceAddressSpace
```

Exact command/API, transaction, ORM and persistence representation are architecture/implementation concerns.

## Cross-context contract

```text
AD ComponentPlacement.ResourceRef
        -> RC Resource
        -> CurrentResourceRealization
        -> AddressSpace? = HostAddress | Prefix
```

AD owns placement; RC owns Resource and AddressSpace. Address changes therefore do not change ApplicationDeployment or ComponentPlacement identity.

## Invariants

- Resource identity is stable across realization and responsibility changes;
- at most one AddressSpace is effective per Resource/time;
- missing current AddressSpace is explicit unresolved realization;
- Resource Scope Affiliation, Resource Responsibility and actor authority are separate meanings;
- consumers use opaque ResourceRef plus published RC projections, not RC-private fact identity.
