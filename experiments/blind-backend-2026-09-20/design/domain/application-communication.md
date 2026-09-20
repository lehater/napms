# Tactical domain — Application Communication

Status: ACCEPTED candidate

## Aggregate: Application

Identity: `ApplicationRef`.

Children:
- Component(`ComponentRef`, name);
- Interaction(`InteractionRef`, sourceComponentRef, destinationComponentRef, purpose, revisions).

Invariants:
- Component belongs to exactly one Application.
- Interaction is directed and references Components belonging to the same Application definition for this MVP.
- One Interaction represents one independently meaningful communication reason.
- Distinct reasons remain distinct Interactions even with equal traffic semantics.
- Interaction has at least one published revision before it can be used by Access Policy.

## Entity: InteractionRevision

Identity: `InteractionRevisionRef`, immutable after publication.

State:
- one or more TrafficClause values;
- createdAt/provenance.

TrafficClause:
- protocol: normalized protocol name or IANA protocol number;
- optional source port ranges;
- optional destination port ranges.

Invariants:
- revision traffic meaning is non-empty and internally valid;
- source/destination ports are permitted only for protocols whose semantics use ports;
- an omitted port set means unrestricted ports for that side, not an unknown value;
- revision is immutable once referenced/published;
- modifying decision-relevant traffic meaning creates a new revision rather than rewriting an old one;
- traffic representation is semantic/source-neutral, not provider/firewall syntax.

The MVP does not invent protocol-specific fields such as ICMP type/code without accepted product evidence. A protocol whose accepted meaning cannot be expressed by protocol plus applicable port ranges must be rejected as unsupported rather than approximated.

## Operations

- RegisterApplication
- AddComponent
- DefineInteraction
- PublishInteractionRevision
- ReadApplication
- ResolveInteractionRevision

## Consistency boundary

Application, its Components, Interaction identities and publication of one new immutable revision are committed atomically per Application aggregate version.
