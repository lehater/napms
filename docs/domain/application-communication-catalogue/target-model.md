# Application Communication Catalogue — Target Domain Model

Status: `S2 affected-edge revalidated; deployment ownership moved to Application Deployment`.

This document is the target ACC model. Earlier ACC-owned `ComponentDeployment`, Resource binding and `DirectedInteractionIdentity` semantics are superseded by the Application Deployment boundary decision.

## Model

```text
ApplicationDefinition
  -> Component

ApplicationDefinition
  -> InteractionDefinition
      -> source Component
      -> destination Component
      -> InteractionContractRevision
          -> TrafficAlternative [1..N]
```

### ApplicationDefinition

Stable ACC-owned identity grouping Components and their declared interactions.

### Component

Stable ACC-owned application role inside one Application Definition. The parent Application is immutable for the Component lifetime.

### InteractionDefinition

Stable ACC-owned directed communication template between two Components. Interaction does not know deployment, Resource, address or endpoint realization.

### InteractionContractRevision

Immutable decision-relevant communication contract revision of one Interaction Definition. Changing decision-relevant traffic creates a new revision.

### TrafficAlternative

Vendor-neutral traffic selector (`protocol`, source-port constraint, destination-port constraint). All alternatives in one revision form one atomic contract; independently governed subsets are separate Interaction Definitions.

## Published semantic contracts

ACC publishes:

```text
ApplicationRef
ComponentRef
InteractionRef
InteractionContractRevisionRef
complete immutable traffic contract
```

Application Deployment consumes Application/Component identities and owns where Components are placed. Governance combines ACC interaction revision identity with AD deployment identities:

```text
GovernedInteractionSubject {
    interactionContractRevisionRef       // ACC
    sourceApplicationDeploymentRef       // AD
    destinationApplicationDeploymentRef  // AD
}
```

ACC does not own or publish a concrete deployment pair.

## Resource realization semantics

None belong to ACC. The current chain is:

```text
ACC Interaction/Component semantics
+ AD ComponentPlacement -> ResourceRef
+ RC Resource -> effective HostAddress | Prefix
```

Address changes do not alter ACC Interaction identity or immutable contract revision.

## Cross-context rule

Consumers treat published references as opaque semantic identities rather than relational foreign keys into ACC storage.

## Deferred questions

- richer ACC lifecycle states not required by current behavior;
- persistence/repository structure;
- migration from the implemented legacy ApplicationDeployment / DeploymentInteraction shape.

Endpoint selection is not an ACC deferred question: the current target deliberately has no endpoint model.