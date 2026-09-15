# Application Communication Catalogue — Target Domain Model

Status: `S2 affected-edge revalidated; deployment ownership moved to Application Deployment`.

This document is the target ACC model. Earlier ACC-owned `ComponentDeployment`, Resource binding and `DirectedInteractionIdentity` semantics are superseded by the Application Deployment boundary decision.

## MVP modelling rule

For the current MVP, model only domain semantics required to complete the minimal end-to-end happy path. Preserve context boundaries and stable identities so richer behavior can be added later, but do not implement speculative extension points as current domain concepts.

In particular, revision workflows, richer lifecycle/state machines, replacement semantics and other history mechanisms are deferred unless the working happy path requires them. Audit/history needs may be satisfied by the existing audit/provenance mechanism without promoting every change into a domain revision model.

## Model

```text
ApplicationDefinition
  -> Component

ApplicationDefinition
  -> Interaction
      -> source Component
      -> destination Component
      -> traffic
```

### ApplicationDefinition

Stable ACC-owned identity grouping Components and their declared interactions. It describes the application definition, not a deployment of that application.

### Component

Stable ACC-owned application role inside exactly one Application Definition. The parent Application is immutable for the Component lifetime.

### Interaction

Stable ACC-owned directed communication template between two Components of the same Application Definition. Interaction describes a possible logical component-to-component communication; it does not know deployment, Resource, address or endpoint realization.

MVP invariants:

- both ends belong to the same Application Definition;
- self-interaction (`A -> A`) is valid;
- at most one Interaction exists for one directed Component pair inside an Application Definition;
- `A -> B` and `B -> A` are different Interactions;
- source and destination are immutable after creation; changing either end means creating another Interaction;
- traffic is part of the current Interaction state for MVP; a dedicated domain revision model is deferred.

If the same Component pair appears to need several independent Interactions, first challenge whether the Components actually contain several semantic roles that should be modelled as separate Components.

## Lifecycle baseline

NAPMS uses retirement rather than physical domain deletion unless a context explicitly requires otherwise. A domain object that is still used by an active dependency cannot be retired; the user must remove or retire blockers first. Historical identity/data may remain readable after retirement.

For MVP, do not add richer lifecycle machinery unless required by the happy path. Interaction keeps a stable identity. If support for restoring a previously retired Interaction is required, the same Interaction identity is reused rather than creating a second identity for the same directed Component pair.

## Published semantic contracts

ACC publishes only the identities and current communication meaning required by consumers:

```text
ApplicationRef
ComponentRef
InteractionRef
current traffic contract
```

Application Deployment consumes Application/Component identities and owns where Components are placed. Downstream contexts combine ACC Interaction identity with AD deployment identities when they need a concrete governed/deployed subject. ACC does not own or publish a concrete deployment pair.

## Resource realization semantics

None belong to ACC. The current chain is:

```text
ACC Interaction/Component semantics
+ AD ComponentPlacement -> ResourceRef
+ RC Resource -> effective HostAddress | Prefix
```

Deployments can use the declared Interaction to derive technically possible interactions between concrete realizations/placements of its Components. The derivation and resulting policy/rule semantics do not belong to ACC.

Address changes do not alter ACC Interaction identity.

## Cross-context rule

Consumers treat published references as opaque semantic identities rather than relational foreign keys into ACC storage.

## Deliberately deferred beyond MVP

- dedicated `InteractionContractRevision` domain workflow and immutable revision history;
- richer ACC lifecycle states and restoration workflows beyond what the happy path requires;
- persistence/repository structure;
- migration from the implemented legacy ApplicationDeployment / DeploymentInteraction shape;
- richer communication-contract semantics not required by the first end-to-end scenario.

Endpoint selection is not an ACC deferred question: the current target deliberately has no endpoint model.
