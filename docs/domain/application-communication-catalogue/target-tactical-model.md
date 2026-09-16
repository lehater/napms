# Application Communication Catalogue — target Tactical DDD model

Status: `S2 MVP Tactical model revalidated 2026-09-16`.

## Purpose

Own stable application/component/interaction meaning and immutable traffic-contract snapshots that downstream policy governance can reference historically without importing deployment or Resource realization.

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
2. cross-Application Interaction is invalid;
3. self-interaction is valid;
4. at most one Interaction exists for one directed `(sourceComponentRef, destinationComponentRef)` pair inside one ApplicationDefinition;
5. `A -> B` and `B -> A` are different Interactions;
6. source/destination are immutable for the Interaction lifetime;
7. changing an endpoint means a different Interaction identity;
8. traffic changes do **not** change Interaction identity; they create a new contract revision.

## Immutable child entity — InteractionContractRevision

```text
InteractionContractRevision {
    interactionContractRevisionRef
    interactionRef
    trafficAlternatives[1..N]
    provenanceRef
}
```

`InteractionContractRevision` has stable identity because Policy Rule change history and current effective rules may refer to one exact traffic snapshot. It is immutable once published.

It is not a separate aggregate or editable workflow object in the MVP. It is owned by its Interaction/ApplicationDefinition aggregate and has no independent mutable lifecycle.

### Revision invariants

1. every revision belongs to exactly one Interaction;
2. a revision contains at least one vendor-neutral traffic alternative;
3. the complete alternative set is one atomic communication contract;
4. downstream consumers may not authorize/materialize only a preferred subset of one revision;
5. a material change to traffic semantics creates a new `InteractionContractRevisionRef`;
6. old revision references remain historically resolvable and are never silently rewritten;
7. exactly one published revision is current for an Interaction at a time;
8. changing the ACC-current revision does not silently alter any existing Policy Rule; an existing Rule continues to use its exact effective revision until its own accepted change lifecycle moves it to another revision.

No sequence number, semantic version string, supersession graph or ACC-side approval workflow is required by the MVP domain.

## TrafficAlternative value

A traffic alternative is a vendor-neutral value describing one allowed communication alternative for the Interaction contract, including protocol/service/port semantics accepted by current requirements.

Provider-native ACL syntax, Firewall identity, Resource address and deployment are not part of this value.

Two traffic alternatives with the same semantic meaning are not duplicated inside one revision.

## Minimal domain operations

```text
CreateApplicationDefinition
AddComponent
DeclareInteraction(sourceComponentRef, destinationComponentRef, initialTraffic)
ReviseInteractionTraffic(interactionRef, newTraffic)
Retire semantic objects only where accepted lifecycle rules require it
```

`DeclareInteraction` creates the Interaction and its initial immutable contract revision.

`ReviseInteractionTraffic` creates a new immutable revision and makes it ACC-current. It does not mutate an already published revision and does not change downstream Policy Rules automatically.

If proposed traffic is semantically unchanged, no new semantic revision is required merely to manufacture version churn.

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

A resolved exact revision provides enough public information to recover:

- owning InteractionRef;
- source/destination ComponentRefs via that Interaction;
- complete immutable traffic alternatives;
- provenance/reference needed for explanation.

A downstream Policy Rule therefore does not need to duplicate `InteractionRef` next to an exact revision merely to recover the Interaction.

## Cross-context invariants

- Application Deployment consumes `ComponentRef` and owns concrete ComponentDeployment identity/Resource relation;
- Access Policy uses exact `InteractionContractRevisionRef` for proposed/current traffic semantics and verifies its endpoint Components against concrete Component Deployments;
- RPM resolves the exact immutable revision and preserves all traffic alternatives;
- Evidence Access Recognition may match observed traffic only against public ACC semantics and may not mutate ACC truth;
- no consumer uses ACC-private persistence identity or SQL foreign keys.

## Lifecycle classification

The current target retains the existing minimal retirement baseline for Application/Component/Interaction identities where active dependencies permit retirement.

InteractionContractRevision itself remains immutable historical contract truth and is never edited/retired out from under historical references.

## Deliberately deferred

- explicit revision-number/version-string policy;
- branch/draft/publish workflow for revisions;
- change-request/approval workflow for catalogue editing;
- richer traffic vocabulary outside the first MVP contract;
- migration from the implemented I31 ACC-owned deployment/binding runtime;
- provider/runtime/network realization concepts.

## Tactical coherence result

The revalidated ACC model keeps its existing aggregate boundary and corrects only affected downstream semantics:

- Interaction remains the stable intra-Application directed component-pair template;
- immutable InteractionContractRevision is the exact decision-relevant traffic snapshot;
- revision references are sufficient to recover Interaction/endpoints;
- ACC-current revision change never silently changes Policy Rule identity or effective traffic;
- deployment, governance and Resource realization remain outside ACC.
