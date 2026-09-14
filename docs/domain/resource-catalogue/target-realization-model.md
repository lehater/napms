# Resource Catalogue — Target realization semantics

Status: `S2 accepted for required-policy materialization`.

Date: 2026-09-14.

## Purpose

Define only the Resource/Endpoint/address semantics required by current access-policy materialization. Curation commands, persistence and migration remain separate concerns.

## Model

```text
Resource
    -> ResourceEndpoint [0..N]
        -> current AddressRealization [0..1] for MVP
```

### ResourceEndpoint

A `ResourceEndpoint` is a stable logical L3 presence/interface of one Resource.

Invariants:

- Endpoint identity is independent from its current address;
- changing an address does not create a new Endpoint;
- an Endpoint may exist before any address is known;
- one Resource may have several Endpoints when they remain one logical access-management Resource;
- Endpoint identity is Resource Catalogue truth and is not owned by ACC or Access Policy.

### AddressRealization

Address realization is a temporal/current fact of one Endpoint, not Endpoint identity.

For MVP:

- at most one address realization is current for one Endpoint at one logical time;
- the value may represent one host address or a network prefix;
- the value is the corporate-visible address/prefix meaningful for access management;
- local/private addresses hidden behind NAT are not substituted when the corporate network uses a translated address/prefix;
- Resource Catalogue does not calculate NAT; it records the already meaningful corporate-visible realization;
- absence of a current address is valid and must be distinguishable from an empty set of required access.

Historical realization changes must remain explainable, but the exact persistence/versioning mechanism is not defined here.

## Published materialization contract

For a Resource and logical/effective time, Resource Catalogue can publish conceptually:

```text
CurrentResourceRealization
    resourceRef
    endpoints[]
        endpointRef
        corporateAddressOrPrefix?
    asOf
    provenance/freshness reference
```

Consumers must treat Endpoint and Resource references as opaque catalogue identities.

Required-policy materialization considers every current Endpoint of the Resource. An Endpoint with no current address makes affected semantic authorization technically unresolved; it is not silently omitted as though no access were required.

## Relationship to existing curation model

`tactical-model.md` remains evidence and accepted semantics for the earlier I27 curation slice where compatible. Its older `ResourceRealizationVersion -> EndpointAddress` representation must not be used to imply that Endpoint identity is recreated with every realization version. This document is the current target owner for Endpoint/address identity semantics used by materialization.
