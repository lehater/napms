# Application Communication Catalogue — target Tactical DDD model

Status: `S2 MVP Tactical model aligned 2026-09-15`.

## Purpose

Own stable application/component/interaction meaning and immutable traffic-contract snapshots that downstream governance can reference historically without importing deployment or Resource realization.

The target intentionally excludes ACC-owned deployment, Resource binding and endpoint/address semantics.

## Aggregate — ApplicationDefinition

```text
ApplicationDefinition {
    applicationRef
    components: Set<Component>
    interactions: Set<Interaction>
}
```

`ApplicationDefinition` is the consistency owner for Components and directed Interaction identity inside one application definition.

## Entity — Component

```text
Component {
    componentRef
    applicationRef
}
```

A Component belongs to exactly one ApplicationDefinition for its lifetime. Moving a Component to another Application is not a mutation of the same Component identity.

Descriptive name/type/metadata do not participate in semantic identity.

## Entity — Interaction

```text
Interaction {
    interactionRef
    applicationRef
    sourceComponentRef
    destinationComponentRef
    currentContractRevisionRef
}
```

An Interaction is the stable directed communication template between two Components of the same ApplicationDefinition.

### Interaction identity invariants

1. source and destination Components belong to the same ApplicationDefinition;
2. self-interaction is valid;
3. at most one Interaction exists for one directed `(sourceComponentRef, destinationComponentRef)` pair inside one ApplicationDefinition;
4. `A -> B` and `B -> A` are different Interactions;
5. source/destination are immutable for the Interaction lifetime;
6. changing an endpoint means a different Interaction identity;
7. traffic changes do **not** change Interaction identity; they create a new contract revision.

## Immutable child entity — InteractionContractRevision

Downstream governance requires an immutable reference to the exact traffic semantics that were approved.

```text
InteractionContractRevision {
    interactionContractRevisionRef
    interactionRef
    trafficAlternatives[1..N]
    provenanceRef
}
```

`InteractionContractRevision` has stable identity because historical Access Requests/Policy Rules may refer to one exact revision. It is immutable once published.

It is not a separate aggregate or editable workflow object in the MVP. It is owned by its Interaction/ApplicationDefinition aggregate and has no independent mutable lifecycle.

### Revision invariants

1. every revision belongs to exactly one Interaction;
2. a revision contains at least one vendor-neutral traffic alternative;
3. the complete alternative set is one atomic communication contract;
4. downstream consumers may not authorize/materialize only a preferred subset of one revision;
5. a material change to traffic semantics creates a new `InteractionContractRevisionRef`;
6. old revision references remain historically resolvable and are never silently rewritten;
7. exactly one published revision is current for an Interaction at a time;
8. changing the current revision does not change Interaction identity but does change the governed subject for new/current authorization because governance keys on revisionRef.

No sequence number, semantic version string, supersession graph or approval workflow is required by the MVP domain. Those are optional future representation/workflow concerns.

## TrafficAlternative value

A traffic alternative is a vendor-neutral value describing one allowed communication alternative for the Interaction contract, including the protocol/service/port semantics accepted by the current ACC requirements.

Provider-native ACL syntax, Firewall identity, Resource address and placement are not part of this value.

Two traffic alternatives with the same semantic meaning are not duplicated inside one revision.

## Minimal domain operations

```text
CreateApplicationDefinition
AddComponent
DeclareInteraction(sourceComponentRef, destinationComponentRef, initialTraffic)
ReviseInteractionTraffic(interactionRef, newTraffic)
Retire semantic objects only where accepted lifecycle rules require it
```

These are domain meanings, not frozen API names.

`DeclareInteraction` creates the Interaction and its initial immutable contract revision.

`ReviseInteractionTraffic` creates a new immutable revision and makes it current. It does not mutate an already published revision.

If the proposed traffic is semantically unchanged, no new semantic revision is required merely to manufacture version churn.

## Lifecycle classification

The current target retains the existing minimal retirement baseline for Application/Component/Interaction identities where active dependencies permit retirement.

No richer state machine is needed for the first happy path.

InteractionContractRevision itself is immutable historical contract truth; it is not edited/retired out from under downstream historical references.

## Published contracts

ACC publishes opaque semantic references and immutable/current contract meaning:

```text
ApplicationRef
ComponentRef
InteractionRef
InteractionContractRevisionRef
ResolveInteractionContractRevision(revisionRef)
CurrentInteractionContractRevision(interactionRef)
```

Exact transport/API shapes are downstream concerns.

A resolved revision provides enough information to recover:

- owning InteractionRef;
- source/destination ComponentRefs via that Interaction;
- complete immutable traffic alternatives;
- provenance/reference needed for explanation.

## Cross-context invariants

- AD consumes only ApplicationRef/ComponentRef and owns deployment/placement.
- AG/AP use `InteractionContractRevisionRef` in the governed subject.
- RPM resolves the exact immutable revision and must preserve all traffic alternatives.
- no consumer uses ACC-private persistence identity or SQL foreign keys.

## Deliberately deferred

- explicit revision-number/version-string policy;
- branch/draft/publish workflow for revisions;
- change-request/approval workflow for catalogue editing;
- richer traffic vocabulary outside the first MVP contract;
- migration from the implemented I31 ACC-owned deployment/binding runtime;
- provider/runtime/network realization concepts.

## Tactical coherence result

The target ACC model now closes the previously inconsistent revision edge:

- Interaction remains the stable directed component-pair template;
- immutable `InteractionContractRevision` is the exact decision-relevant traffic snapshot;
- material traffic change creates a new revision, not a new Interaction;
- historical approvals can continue referencing the exact revision they approved;
- downstream governed subject semantics need no implementation invention.
