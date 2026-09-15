# ADR-012 — Application Definition and Deployment Model

Status: `current as-built design decision`.

Date: 2026-09-10.

## Role

This ADR records the consequential design embodied by the current implemented Application Catalogue. It remains project documentation because reconstructing the current system requires this model, its trade-offs and its compatibility constraints.

It governs reconstruction of the as-built I31 model. Current target semantics are owned by `docs/requirements/application-catalogue-domain-target.md`, `docs/domain/application-communication-catalogue/target-model.md`, `docs/domain/application-communication-catalogue/target-tactical-model.md`, `docs/domain/application-deployment/tactical-model.md` and the Strategic model.

## Context

The current I27 Application Communication Catalogue models:

```text
Application
  -> Component
      -> Component Deployment

DCS Revision
  -> Source Component Deployment
  -> Destination Component Deployment

Deployment Resource Binding
  -> Component Deployment
  -> Resource
```

This was implemented and remained the runtime contract that I31 had to preserve while introducing a different user-facing deployment boundary: users deploy an Application as a whole, select a normal subset of interactions defined by that Application, and bind source/destination Resources in the context of each selected interaction.

The design stays KISS-oriented: no Application-definition versioning, no deployment overrides/exceptions and no hard delete.

## Decision

### Application Definition

An Application represents a reusable definition independent of Company/deployment context.

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

Traffic alternatives support multiple protocols and port/range sets for the same component pair, for example:

```text
TCP (80, 443, 8000-8010)
UDP (443)
```

### Application Deployment

`ApplicationDeployment` is the implemented user-facing deployment unit.

```text
Application Deployment
  -> Application Definition
  -> Company / environment / scope context
  -> selected Deployment Interactions
```

A Deployment may select any subset of the Application Definition's Interaction Definitions. Partial selection is normal and is not an error, override or exception.

A selected interaction keeps the Definition semantics unchanged. Source Component, destination Component, protocol and ports are not overridden in Deployment.

If a different communication definition is required, it is represented by another Application Definition in this implemented model.

### Interaction-scoped resource bindings

Resource bindings are scoped to one selected interaction and one side of that interaction:

```text
ApplicationDeployment
  -> DeploymentInteraction
      -> InteractionDefinition
      -> Source Resource Bindings[]
      -> Destination Resource Bindings[]
```

The same Component may therefore resolve to different Resource sets in different Deployment Interactions.

Bindings are not copied into Interaction Definition and are not global Component-to-Resource assignments.

### Versioning and overrides

Application Definition versioning is not part of the current implemented model.

A Definition edit changes the current definition used by all active Deployments that select the affected Interaction Definition, subject to the safety constraints in ADR-013 and the as-built ACC Tactical model.

Deployment-specific traffic overrides and exceptions are not part of the current implemented model. No generic overlay/merge mechanism exists.

### Lifecycle

Normal product hard delete is absent.

Lifecycle is:

```text
Active -> Retired
```

Retirement is terminal.

An entity cannot be retired while any active incoming reference depends on it. The user must first remove or retire active dependants. Retired entities remain persisted for historical/reference integrity and are excluded from normal working lists unless required to explain an existing historical reference.

This rule applies consistently to catalogue entities and relations where retirement exists.

## UI consequence

Applications expose two top-level working sets:

```text
Applications
  Definitions
  Deployments
```

Definition detail exposes `Overview`, `Components`, `Interactions`, `Deployments`.

Deployment detail is centered on one dense connectivity table. One row represents one selected Interaction Definition enriched with source/destination Resource counts:

```text
Source Component | Source Resources | Destination Component | Destination Resources | Traffic
```

Resource collections are always summarized by count (`1 resource`, `327 resources`). The count is the drill-down target; resource names are not concatenated into an unbounded cell. Drill-down opens a server-paged/searchable/filterable resource table.

Large traffic sets use the same progressive disclosure rule: short sets may render inline, otherwise render a compact count/summary with detail on demand.

Potentially unbounded tables use server-side search/filter/sort/paging and fixed compact row presentation.

## Compatibility with the pre-I31 implementation

This ADR does not rewrite ADR-006 or ADR-009 retroactively. They describe the preceding implemented model accurately.

I31 had to reconcile these existing contracts:

- `ComponentDeployment` was the deployment identity consumed by downstream Connectivity Requirement, Decision and Access Rule semantics;
- `DcsRevision` referenced source/destination `ComponentDeployment` identities;
- `DeploymentResourceBinding` belonged directly to `ComponentDeployment`;
- the Web requirements and screen map exposed the I27 hierarchy.

The implemented I31 compatibility design therefore had to define how `ApplicationDeployment`, `InteractionDefinition`, `DeploymentInteraction` and interaction-scoped Resource bindings project into the existing downstream semantic identities without silently rewriting historical policy truth. ADR-013 is that compatibility decision.

## Relationship to current target

The current target preserves the useful application/deployment concepts but assigns semantic ownership differently:

- ACC owns Application, Component, Interaction and immutable `InteractionContractRevision`;
- Application Deployment is a separate target Bounded Context;
- target AD owns current `(ComponentRef, ResourceRef)` placement sets;
- `DeploymentInteraction` and ACC-owned interaction-side Resource binding are as-built compatibility concepts rather than target semantic ownership;
- the target governed subject uses exact `InteractionContractRevisionRef + sourceApplicationDeploymentRef + destinationApplicationDeploymentRef`.

This distinction lets the current implementation be reconstructed without making its compatibility model the future domain model.

## Consequences

Current as-built consequences are:

- deployment semantics match the implemented product mental model: deploy one Application, use any subset of its defined interactions;
- resource realization is contextual to each selected interaction in the as-built catalogue;
- Deployment UI remains compact for hundreds/thousands of interactions and resources;
- no exceptions, overlays, Definition revisions or hard-delete workflow are required by the current implementation;
- the pre-I31 downstream Component Deployment/DCS contracts remain valid through an explicit internal compatibility projection;
- the current system can be reconstructed while target ACC/AD ownership remains independently documented.
