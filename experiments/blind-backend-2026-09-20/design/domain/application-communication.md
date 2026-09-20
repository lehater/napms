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
- protocol;
- one or more traffic clauses containing destination port or port range where the protocol uses ports;
- createdAt/provenance.

Invariants:
- revision traffic meaning is non-empty and internally valid;
- revision is immutable once referenced/published;
- modifying decision-relevant traffic meaning creates a new revision rather than rewriting an old one;
- traffic representation is semantic/source-neutral, not provider/firewall syntax.

## Operations

- RegisterApplication
- AddComponent
- DefineInteraction
- PublishInteractionRevision
- ReadApplication
- ResolveInteractionRevision

## Consistency boundary

Application, its Components, Interaction identities and publication of one new immutable revision are committed atomically per Application aggregate version.
