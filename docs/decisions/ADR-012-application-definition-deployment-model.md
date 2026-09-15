# ADR-012 — Application Definition and Deployment Model

Status: `current as-built design decision`.

## Role

This ADR records the consequential design choice embodied by the current implemented Application Catalogue. It remains project documentation because reconstructing the current system requires this model and its trade-offs.

It does **not** define current target bounded-context ownership. Current target semantics are owned by `docs/requirements/application-catalogue-domain-target.md`, `docs/domain/application-communication-catalogue/target-tactical-model.md`, `docs/domain/application-deployment/tactical-model.md` and the Strategic model.

## Context

The implemented product needed an application-oriented authoring model in which users define reusable application communication and then deploy an Application as a whole, selecting a normal subset of interactions and binding Resources in the context of each selected interaction.

The design also had to preserve compatibility with downstream contracts that consume Component Deployment and immutable DCS identities.

## Decision

### Application Definition

An Application Definition represents reusable application structure independent of Company/deployment context:

```text
Application Definition
  -> Components
  -> Interaction Definitions
```

An Interaction Definition belongs to one Application Definition and contains:

```text
source Component
destination Component
traffic alternatives: 1+
```

Traffic alternatives support several protocol/port alternatives for the same component pair.

### Application Deployment

The current implemented authoring model uses `ApplicationDeployment` as the user-facing deployment unit:

```text
Application Deployment
  -> Application Definition
  -> Company / Environment / Scope context
  -> selected Deployment Interactions
```

A Deployment may select any subset of the Application Definition's Interaction Definitions. Partial selection is normal rather than an override/error.

A selected Deployment Interaction uses the Definition's source Component, destination Component and traffic semantics. The implemented model has no Deployment-specific traffic/endpoint override.

### Interaction-scoped Resource bindings

Resource bindings are scoped to one selected interaction and one side:

```text
ApplicationDeployment
  -> DeploymentInteraction
      -> InteractionDefinition
      -> Source Resource Bindings[]
      -> Destination Resource Bindings[]
```

The same Component may therefore resolve to different Resource sets in different Deployment Interactions. These bindings are not global Component-to-Resource identity and are not copied into Interaction Definition.

### Definition versioning and overrides

The implemented model has no separate Application Definition version aggregate and no generic Deployment override/merge mechanism. Current Definition changes therefore follow the explicit safety constraints in ADR-013 and the as-built ACC Tactical model.

### Lifecycle

Normal product hard delete is absent. The implemented catalogue lifecycle is:

```text
Active -> Retired
```

Retirement is terminal and dependency-blocked. Active dependants must be cleared first. Retired identities remain persisted where required for reference integrity and explanation.

## UI consequence

Applications exposes two primary working sets:

```text
Applications
  Definitions
  Deployments
```

Definition detail exposes `Overview`, `Components`, `Interactions`, `Deployments`.

Deployment detail is centered on a dense connectivity table:

```text
Source Component | Source Resources | Destination Component | Destination Resources | Traffic
```

One row represents one selected Deployment Interaction. Resource collections are summarized by count and drill down to bounded server-backed lists. Large traffic sets use compact summary plus detail on demand. Potentially unbounded lists use server-side search/filter/sort/paging.

## As-built compatibility consequence

The current implementation also has downstream contracts that consume:

```text
sourceComponentDeploymentId
+ destinationComponentDeploymentId
+ dcsContractRevisionId
```

Therefore the user-facing Application Deployment / Deployment Interaction model cannot by itself replace those compatibility identities. ADR-013 defines the internal projection that preserves them without exposing them as normal authoring concepts.

## Current target relationship

The current target model preserves the useful user/business concepts but assigns ownership differently:

- ACC owns Application, Component, Interaction and immutable `InteractionContractRevision`;
- Application Deployment is a separate target Bounded Context;
- target AD owns current `(ComponentRef, ResourceRef)` placement sets;
- `DeploymentInteraction` and ACC-owned interaction-side Resource binding are **as-built compatibility concepts**, not target semantic ownership;
- the target governed subject uses exact `InteractionContractRevisionRef + sourceApplicationDeploymentRef + destinationApplicationDeploymentRef`.

This distinction lets the current implementation be reconstructed without making its compatibility model the future domain model.

## Consequences

- the current UI mental model is Application Definition + Application Deployment;
- a Deployment may use any subset of its Definition's interactions;
- Resource sets are interaction-side-specific in the implemented catalogue;
- no generic override/versioning machinery is required by the current implementation;
- retirement and dependency explanation preserve referenced state instead of hard deletion;
- compatibility with downstream Component Deployment/DCS identity is an explicit internal concern rather than a user-facing authoring model.
