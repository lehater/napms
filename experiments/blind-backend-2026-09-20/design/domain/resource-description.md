# Tactical domain — Resource Description

Status: ACCEPTED candidate after Coding-Agent Challenge 01

## Aggregate: Resource

Identity: `ResourceRef` opaque stable identifier.

State:
- immutable `displayName` in the selected MVP;
- current `SiteRef?`;
- Site assignment history;
- current responsibility per role: OWNER -> ResponsibilityGroupRef? and ADMINISTRATOR -> ResponsibilityGroupRef?, plus assignment history;
- ResourceEndpoint children;
- version for optimistic concurrency.

Invariants:
- ResourceRef never derives from address.
- Resource displayName is non-empty after trimming.
- Owner/Administrator references are organizational groups and grant no security authority.
- SiteRef and ResponsibilityGroupRef must resolve to records owned by this context at mutation time.
- changing/clearing Site preserves prior Site assignment facts and effective dates.
- at most one current OWNER assignment and at most one current ADMINISTRATOR assignment exist at any instant.
- setting a role to a different group atomically closes the prior current assignment and opens the new assignment.
- clearing a role closes the prior assignment.
- setting an already-current group is a semantic no-op.
- responsibility replacement/clear preserves prior assignment facts and effective dates.
- all current/historical Resource facts needed for explanation remain Resource-domain truth.

Operations:
- RegisterResource
- SetSite / ClearSite
- SetResponsibility / ClearResponsibility
- AddEndpoint
- SetEndpointAddress / ClearEndpointAddress
- ReadResourceCurrent / ReadResourceHistory

No Resource rename/delete operation is part of the selected MVP.

## Aggregate: Site

Identity: `SiteRef`.

State:
- non-empty name;
- optional description/location text.

Purpose: reusable stable Site identity referenced by many Resources. No physical-facility taxonomy is invented.

Operations:
- RegisterSite
- ReadSite

Site records are immutable in the selected MVP.

## Aggregate: ResponsibilityGroup

Identity: `ResponsibilityGroupRef`.

State:
- non-empty displayName;
- optional externalReference.

Purpose: minimal organizational group/team identity required for Resource Owner/Administrator responsibility. It is deliberately not an authentication principal, role, or authorization scope.

Operations:
- RegisterResponsibilityGroup
- ReadResponsibilityGroup

ResponsibilityGroup records are immutable in the selected MVP.

## Entity: ResourceEndpoint

Identity: `EndpointRef`, stable within Resource lifecycle.

State:
- current AddressRealization? = HostAddress | Prefix;
- address-history entries with effectiveFrom/effectiveTo and changedBySubject.

Invariants:
- zero or one current address realization per Endpoint;
- changing/clearing address preserves EndpointRef and prior address facts;
- a Resource may have multiple Endpoints;
- HostAddress and Prefix remain semantically distinct;
- Prefix is not expanded into hosts by this context.

## Value objects

### HostAddress
- one IPv4 or IPv6 address literal;
- no CIDR suffix;
- stored/emitted in canonical textual form;
- IPv4 and IPv6 remain distinct families;
- an IPv4-mapped IPv6 address remains IPv6 and is not silently “unmapped” to IPv4.

### Prefix
- one IPv4 or IPv6 CIDR prefix;
- prefix length is valid for its family;
- all host bits must already be zero on input;
- input with host bits set is rejected rather than silently masked, because silent masking could change intended access meaning;
- stored/emitted in canonical network-prefix textual form.

### EffectiveInterval
Half-open time semantics `[from,to)`.

Address normalization is semantic validation. It must never silently broaden/narrow an address or prefix.

## Consistency boundary

One Resource mutation, including endpoint/address, Site and responsibility temporal state, commits atomically against one Resource version. Site and ResponsibilityGroup are independent immutable aggregates referenced by stable IDs. Cross-aggregate uniqueness is not assumed except identifier uniqueness.
