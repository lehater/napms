# Application Catalogue Target Boundary

Status: `accepted and implemented through I31`.

Date: 2026-09-10.

## Purpose

Define how the ADR-012 Application Catalogue model is implemented without changing existing downstream bounded-context identities or transferring semantic ownership between contexts.

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

ACC exposes current target-authored interactions through an adapter from `DeploymentInteraction` to the existing `DirectedInteractionIdentity` contract.

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

The existing ACC resolution flow continues resolving the compatibility source/destination Component Deployment IDs to temporal Resource bindings.

Target application services create/end those compatibility bindings from stronger commands scoped by:

```text
deploymentInteractionId + side + resourceReference
```

The persistence adapter translates target binding ownership into the compatibility rows required by the existing resolver.

Resource-set UI rows combine ACC-owned effective membership with Resource Catalogue-owned display data and effective Responsibility Scope. This is a read-composition concern, not a transfer of ownership.

The I31 bounded query projection may therefore compose owner schemas at the composition/read-model boundary when they are available in one PostgreSQL deployment. That projection:

- is query-only and owns no domain fact;
- performs no mutation, lifecycle or authority decision;
- uses one explicit `asOf` for all temporal membership/scope facts in one response;
- applies search/filter/sort/paging and totals in the server query rather than loading an unbounded child collection;
- is not an ACC or RC persistence adapter and does not permit either bounded context to read the other's schema.

If owner schemas later move to separate stores, this query composition can be replaced by owner query ports or a derived read store without changing ACC identity or the public authoring contract.

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

The dependency summary groups these results and provides counts/drill-downs. Peer business lifecycle remains defined by the peer context; ACC does not infer active/effective state from foreign database columns.

## External correlation values

Application owner, Application Deployment company and Application Deployment scope are correlation/reference data only.

- Company is not introduced as a NAPMS aggregate.
- Responsibility Scope remains externally owned as established by ADR-011.
- Owner reference does not become Actor identity or Authority assignment.
- Environment is ACC-owned descriptive deployment context, not Network Environment Operations identity.

Future directory/company/scope discovery is implemented through optional adapters and does not change ACC stable IDs or command authority.

## Legacy coexistence

Pre-I31 Component Deployment/DCS/binding rows remain readable by existing downstream adapters.

Target-created compatibility Component Deployments are distinguishable in persistence through an explicit mapping to `deploymentInteractionId` and side. The implementation does not identify them by display-name convention.

Legacy rows without that mapping remain legacy truth. They are not synthesized into Application Deployments.

During coexistence, existing downstream interaction discovery may return both legacy interactions and target compatibility interactions as required by current product flows. Catalogue Web/API authoring uses target identities only.

## Dependency direction

```text
ACC Domain
  <- ACC Application / owned ports
      <- ACC adapters / composition

peer Domain/Application
  <- peer adapters
      <- ACC dependency adapters at composition boundary

ACC + RC read facts
  -> query-only composition projection
      -> target HTTP read model
```

The implementation preserves inward dependency direction and avoids shared mutable domain models.

## Consequences

- I31 changes the ACC user/write model without a cross-context identity migration;
- compatibility logic remains an ACC adapter/application concern rather than leaking into Web or peer domains;
- cross-context blockers are explicit port calls rather than direct persistence coupling;
- bounded cross-context UI projections may be composed outside owner adapters without transferring mutation semantics;
- target Resource binding semantics reuse existing proven downstream resolution mechanics;
- optional enterprise reference discovery can be added later without changing the current domain model.
