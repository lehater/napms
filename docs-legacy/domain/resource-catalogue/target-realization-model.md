# Resource Catalogue — Target realization semantics

Status: `S2 simplified target revalidated for current scope 2026-09-16`.

Date: 2026-09-16.

## Purpose

Define the minimum Resource/address semantics required by current access-policy materialization. Endpoint/interface/VIP/listener modelling is intentionally deferred until a demonstrated use case requires it.

## Current target model

```text
Resource
    ResourceId
    ...
    -> effective AddressSpace [0..1] at a logical time

AddressSpace = HostAddress | Prefix
```

For the current scope, one Resource has at most one effective `AddressSpace` at one logical time. When present, it is either one host address or one network prefix.

`AddressSpace` is Resource Catalogue truth. Application Deployment references only `ResourceRef` from each concrete `ComponentDeployment`; it does not copy an IP/prefix and does not select an endpoint.

## Address realization

Address realization is a temporal/current fact of the Resource, not Resource identity.

Current rules:

- changing the effective host address or prefix does not change `ResourceId`;
- it therefore does not change a ComponentDeployment that refers to the same Resource identity;
- the value is the corporate-visible address/prefix meaningful for access management;
- Resource Catalogue does not calculate NAT; it records the already meaningful corporate-visible realization;
- absence of a current AddressSpace is valid and must be distinguishable from an empty set of required access;
- historical realization changes must remain explainable; exact persistence/versioning remains Tactical.

## Published materialization contract

Conceptually:

```text
CurrentResourceRealization
    resourceRef
    addressSpace? : HostAddress | Prefix
    asOf
    resolution/completeness state
    provenance/freshness reference
```

Required-policy materialization resolves each source/destination `ComponentDeployment.ResourceRef` through this contract. A missing/unresolved AddressSpace makes affected materialization unresolved; it is not silently omitted.

A Prefix remains a Prefix. Materialization is not required to enumerate every host address inside it.

Evidence Access Recognition may also consume address-to-Resource correlation semantics where exact source qualification permits it. Ambiguous/missing correlation remains unresolved and does not create policy truth.

## Explicit current limitation

The current target does **not** model several simultaneous addresses/prefixes, multiple interfaces, management/data separation, VIPs, deployment-specific network exposure or `ResourceEndpoint` identity. These are future extensions only if a confirmed use case requires them.

This limitation is deliberate: the target model prefers one Resource -> one effective host-or-prefix realization over speculative endpoint abstractions.

## Tactical alignment

`tactical-model.md` implements this target semantic shape with `ResourceAddressFact` history and a derived `CurrentResourceRealization` projection.

Existing curation/history guarantees remain where compatible: stable Resource identity, temporal explainability/provenance, Resource Scope Affiliation and Resource Responsibility. Persistence/versioning mechanics remain downstream implementation concerns.
