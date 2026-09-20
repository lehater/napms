# Tactical domain — Resource Description

Status: ACCEPTED candidate

## Aggregate: Resource

Identity: `ResourceRef` opaque stable identifier.

State:
- displayName;
- SiteRef?;
- responsibility assignments: role OWNER or ADMINISTRATOR, ResponsibilityGroupRef, validity interval;
- ResourceEndpoint children;
- version for concurrency.

Invariants:
- ResourceRef never derives from address.
- Owner/Administrator references are organizational groups and grant no security authority.
- Site/Responsibility/history semantics remain Resource-domain facts.
- SiteRef and ResponsibilityGroupRef must resolve to records owned by this context at mutation time.

Operations:
- RegisterResource
- RenameResource
- SetSite
- AssignResponsibility / EndResponsibility
- AddEndpoint
- SetEndpointAddress / ClearEndpointAddress
- ReadResourceCurrent / ReadResourceHistory

## Aggregate: Site

Identity: `SiteRef`.

State:
- name;
- optional description/location text;
- version.

Purpose: reusable stable Site identity referenced by many Resources. No physical-facility taxonomy is invented.

Operations:
- RegisterSite
- UpdateSite
- ReadSite

## Aggregate: ResponsibilityGroup

Identity: `ResponsibilityGroupRef`.

State:
- displayName;
- optional externalReference;
- version.

Purpose: minimal organizational group/team identity required for Resource Owner/Administrator responsibility. It is deliberately not an authentication principal, role, or authorization scope.

Operations:
- RegisterResponsibilityGroup
- UpdateResponsibilityGroup
- ReadResponsibilityGroup

## Entity: ResourceEndpoint

Identity: `EndpointRef`, stable within Resource lifecycle.

State:
- current AddressRealization? = HostAddress | Prefix;
- address-history entries with effectiveFrom/effectiveTo and provenance.

Invariants:
- zero or one current address realization per Endpoint in the admitted source evidence;
- changing address preserves EndpointRef;
- a Resource may have multiple Endpoints;
- HostAddress and Prefix remain semantically distinct; Prefix is not expanded into hosts by this context.

## Value objects

- HostAddress: normalized IP host address.
- Prefix: normalized network prefix.
- EffectiveInterval with half-open time semantics `[from,to)`.

## Consistency boundary

One aggregate mutation commits atomically. Resource endpoint/current-address and responsibility temporal validity are inside the Resource aggregate; Site and ResponsibilityGroup are independent aggregates referenced by stable IDs. Cross-aggregate uniqueness is not assumed except identifier uniqueness.
