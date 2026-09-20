# Tactical domain — Application Communication

Status: ACCEPTED after Source Corpus amendment 02

## Aggregate: Application

Identity: `ApplicationRef`.

State:
- immutable non-empty name;
- Component children;
- aggregate version.

### Component

Identity: `ComponentRef`.

State:
- immutable non-empty name;
- owning ApplicationRef.

Invariants:
- a Component belongs to exactly one Application;
- Component identity does not depend on Deployment, Resource or network address.

Operations:
- RegisterApplication
- AddComponent
- ReadApplication
- ResolveComponent

Consistency:
- Component creation is atomic under Application aggregate version;
- Application name/Component names are immutable in selected MVP.

## Aggregate: Interaction

Identity: `InteractionRef`.

Immutable subject:
- sourceComponentRef;
- destinationComponentRef;
- optional purpose/description.

State:
- immutable published InteractionRevision children;
- aggregate version used only to serialize revision publication.

Invariants:
- Interaction is directed;
- source and destination Components must both resolve, but MAY belong to different Applications;
- there is no blanket same-Application invariant;
- one Interaction represents one independently meaningful communication reason;
- distinct reasons remain distinct Interactions even when Component pair and traffic semantics happen to be equal;
- Interaction cannot be used for Access Policy until at least one revision exists.

Operations:
- DefineInteraction
- PublishInteractionRevision
- ReadInteraction
- ResolveInteractionRevision

Creation of an Interaction is independent from mutating either referenced Application aggregate. Component references are validated through public owner reads inside the same Application Communication context; referenced Applications/Components are not written.

## Entity: InteractionRevision

Identity: `InteractionRevisionRef`, immutable after publication.

State:
- one or more TrafficClause values;
- createdAt/provenance.

TrafficClause:
- protocol: normalized protocol name or numeric protocol identifier;
- source port ranges;
- destination port ranges.

Invariants:
- revision traffic meaning is non-empty and internally valid;
- source/destination ports are allowed only for protocols whose accepted semantics use ports;
- empty port set means unrestricted on that side where ports are applicable, never “unknown”;
- published revision is immutable;
- changing decision-relevant traffic meaning creates a new revision;
- traffic representation is provider/firewall-neutral;
- unsupported protocol-specific semantics are rejected rather than approximated.

The selected MVP does not invent protocol-specific fields such as ICMP type/code without accepted source input.

## Consistency boundaries

Two independent aggregates exist inside this Bounded Context:

1. **Application aggregate** — Application + Components; version serializes Component creation.
2. **Interaction aggregate** — Interaction + immutable Revisions; version serializes revision publication.

Defining a cross-Application Interaction performs read-only validation of both ComponentRefs and writes only the new Interaction aggregate. No multi-Application write transaction or shared aggregate is introduced.
