# Application Catalogue Target Boundary

Status: `accepted for I31; implementation pending`.

Date: 2026-09-10.

## Purpose

Define how the ADR-012 target Application Catalogue is introduced without changing existing downstream bounded-context identities or transferring semantic ownership between contexts.

## Ownership

Application Communication Catalogue owns:

- Application Definition, Component and Interaction Definition identity/structure;
- Application Deployment and Deployment Interaction identity/structure;
- interaction-scoped source/destination Resource binding facts;
- the internal compatibility projection to existing Component Deployment/DCS identities;
- retirement dependency orchestration for ACC-owned mutations.

Resource Catalogue continues to own Resource identity and Resource facts.

Connectivity Requirements, Connectivity Decision and Access Policy continue to own their respective business records and lifecycle/effectiveness semantics.

Authority Management continues to own mutation admission.

## Compatibility boundary

Existing downstream consumers retain their local semantic identity shape:

```text
sourceComponentDeploymentId
destinationComponentDeploymentId
dcsContractRevisionId
```

ACC exposes target-authored current interactions through an adapter from `DeploymentInteraction` to the existing `DirectedInteractionIdentity` contract.

The mapping is:

```text
DeploymentInteraction
  -> ACC compatibility projection
      -> source compatibility ComponentDeployment
      -> destination compatibility ComponentDeployment
      -> current immutable DcsRevision
  -> DirectedInteractionIdentity
```

No downstream context imports `ApplicationDeployment` or `DeploymentInteraction` domain types merely to support I31.

## Resource resolution

The existing ACC resolution flow may continue resolving the compatibility source/destination Component Deployment IDs to temporal Resource bindings.

Target application services create/end those compatibility bindings from stronger target commands scoped by:

```text
deploymentInteractionId + side + resourceReference
```

The persistence adapter is responsible for translating target binding ownership into the compatibility rows required by the existing resolver.

## Traffic projection

Interaction Definition traffic is current ACC truth. DCS revision remains immutable downstream snapshot truth.

When a permitted traffic edit affects Active Deployment Interactions, ACC application logic creates replacement current DCS snapshots for all affected interactions before the operation succeeds. Existing downstream references are never rewritten.

Traffic edit admission consumes dependency ports owned by ACC application code:

```text
ConnectivityRequirementDependencyPort
ConnectivityDecisionDependencyPort
AccessRuleDependencyPort
```

Adapters translate the exact current compatibility triple into each peer context's query model and return owner-defined active/effective references.

No peer repository table is read directly by ACC Domain/Application code.

## Retirement dependency boundary

ACC owns the decision to admit or reject retirement of its entities. To evaluate cross-context incoming references it consumes explicit dependency-query ports.

The peer adapters return only the information required for admission and explanation:

```text
dependency kind
stable reference
optional display/reference metadata
```

The target dependency summary groups these results and provides counts/drill-downs. Peer business lifecycle remains defined by the peer context; ACC does not infer active/effective state from foreign database columns.

## External correlation values

Application owner, Application Deployment company and Application Deployment scope are correlation/reference data only.

- Company is not introduced as a NAPMS aggregate.
- Responsibility Scope remains externally owned as established by ADR-011.
- Owner reference does not become Actor identity or Authority assignment.
- Environment is ACC-owned descriptive deployment context, not Network Environment Operations identity.

Future directory/company/scope discovery is implemented through optional adapters and does not change ACC stable IDs or command authority.

## Legacy coexistence

Pre-I31 Component Deployment/DCS/binding rows remain readable by existing downstream adapters.

Target-created compatibility Component Deployments are distinguishable in persistence through an explicit mapping to `deploymentInteractionId` and side. The implementation must not identify them by display-name convention.

Legacy rows without that mapping remain legacy truth. They are not synthesized into target Application Deployments.

During coexistence, existing downstream interaction discovery may return both legacy interactions and target compatibility interactions as required by current product flows. Target catalogue Web/API authoring uses target identities only.

## Dependency direction

```text
ACC Domain
  <- ACC Application / owned ports
      <- ACC adapters / composition

peer Domain/Application
  <- peer adapters
      <- ACC dependency adapters at composition boundary
```

The implementation must preserve inward dependency direction and avoid shared mutable domain models.

## Consequences

- I31 changes the ACC user/write model without a cross-context identity migration;
- compatibility logic remains an ACC adapter/application concern rather than leaking into Web or peer domains;
- cross-context blockers are explicit port calls rather than direct persistence coupling;
- target Resource binding semantics reuse existing proven downstream resolution mechanics;
- optional enterprise reference discovery can be added later without changing the target domain model.
