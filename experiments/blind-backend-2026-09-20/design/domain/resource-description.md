# Tactical domain — Resource Description

Status: ACCEPTED candidate

## Aggregate: Resource

Identity: `ResourceRef` opaque stable identifier.

State:
- displayName;
- SiteRef? plus descriptive Site information resolved through Resource domain-owned Site records;
- responsibility assignments: role OWNER or ADMINISTRATOR, GroupRef, validity interval;
- ResourceEndpoint children;
- version for concurrency.

Invariants:
- ResourceRef never derives from address.
- Owner/Administrator references are organizational groups and grant no security authority.
- Site/Responsibility/history semantics remain Resource-domain facts.

Operations:
- RegisterResource
- RenameResource
- SetSite
- AssignResponsibility / EndResponsibility
- AddEndpoint
- SetEndpointAddress / ClearEndpointAddress
- ReadResourceCurrent / ReadResourceHistory

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
- GroupRef, SiteRef.
- EffectiveInterval with half-open time semantics `[from,to)`.

## Consistency boundary

One Resource aggregate mutation, including endpoint/current-address and responsibility temporal validity, commits atomically. Cross-Resource uniqueness is not assumed except identifier uniqueness.
