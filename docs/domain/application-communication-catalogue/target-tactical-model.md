# Application Communication Catalogue — Tactical DDD model

Status: `current target`.

## Purpose

Own stable Application, Component and Interaction meaning plus immutable vendor-neutral traffic-contract revisions. Deployment, Resource and address realization are outside ACC.

## Aggregate — ApplicationDefinition

```text
ApplicationDefinition {
    applicationRef
    components: Set<Component>
    interactions: Set<Interaction>
}
```

`ApplicationDefinition` is the consistency owner for Components and directed Interaction identity inside one Application.

## Component

```text
Component {
    componentRef
    applicationRef
}
```

A Component belongs to exactly one Application for its lifetime. Name/type/metadata do not participate in semantic identity.

## Interaction

```text
Interaction {
    interactionRef
    applicationRef
    sourceComponentRef
    destinationComponentRef
    currentContractRevisionRef
}
```

Invariants:

- source and destination belong to the owning Application;
- self-interaction is valid;
- one directed `(sourceComponentRef, destinationComponentRef)` pair identifies at most one Interaction inside the Application;
- direction matters;
- endpoints are immutable for one Interaction identity;
- traffic changes create a new contract revision and do not change Interaction identity.

## InteractionContractRevision

```text
InteractionContractRevision {
    interactionContractRevisionRef
    interactionRef
    trafficAlternatives[1..N]
    provenanceRef
}
```

A published revision is immutable and remains resolvable by its reference. Exactly one published revision is current for an Interaction at a time.

Revision invariants:

- every revision belongs to exactly one Interaction;
- at least one vendor-neutral traffic alternative exists;
- the complete alternative set is one atomic communication contract;
- consumers may not silently use only a preferred subset;
- materially changed traffic creates a new revision reference;
- changing the current revision does not change Interaction identity.

## TrafficAlternative

A traffic alternative is a vendor-neutral protocol/service/port selector. Provider-native ACL syntax, Firewall identity, Resource address and placement are excluded.

Semantically duplicate alternatives are not repeated inside one revision.

## Domain operations

```text
CreateApplicationDefinition
AddComponent
DeclareInteraction(sourceComponentRef, destinationComponentRef, initialTraffic)
ReviseInteractionTraffic(interactionRef, newTraffic)
```

`DeclareInteraction` creates the Interaction and its initial immutable revision. `ReviseInteractionTraffic` creates a new immutable revision and makes it current. Semantically unchanged traffic need not create revision churn.

## Published contracts

```text
ApplicationRef
ComponentRef
InteractionRef
InteractionContractRevisionRef
ResolveInteractionContractRevision(revisionRef)
CurrentInteractionContractRevision(interactionRef)
```

A resolved revision exposes owning InteractionRef, endpoint ComponentRefs, complete traffic alternatives and provenance required for explanation.

## Cross-context invariants

- AD consumes ApplicationRef/ComponentRef and owns deployment/placement;
- governance may reference an exact InteractionContractRevisionRef;
- technical compositions preserve every traffic alternative;
- consumers use public semantic contracts, not ACC-private persistence identity.
