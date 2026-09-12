# Application Catalogue Domain Migration Roadmap

Status: `planned`.

Decision: `../decisions/ADR-015-acc-component-deployment-and-atomic-interaction-contract.md`.
Target model: `../domain/application-communication-catalogue/target-model.md`.
Target requirements: `../requirements/application-catalogue-domain-target.md`.

## Purpose

Migrate the implemented I31 `ApplicationDeployment` / `DeploymentInteraction` model to the accepted ACC target without rewriting historical downstream truth.

This roadmap does not authorize redesign of Access Policy or Resource Catalogue internals. Those contexts are reviewed separately.

## Gate 0 — model lock

Completed by ADR-015:

- Component is the deployment unit;
- Component Deployment to Resource is a separate temporal binding;
- Interaction is directed between Components;
- decision-relevant traffic is an immutable atomic contract revision;
- concrete deployed interaction identity is the three-part ACC published subject;
- cross-context IDs are opaque and do not use SQL foreign keys across bounded contexts;
- endpoint-specific deployment binding is explicitly unresolved.

No implementation phase may weaken these invariants without a superseding ADR.

## Gate 1 — migration design

Before production code changes, document:

- mapping of existing I31 Application Deployments and Deployment Interactions to target Component Deployments where trustworthy mapping exists;
- treatment of I31 rows that cannot be mapped without inventing business facts;
- preservation of existing Component Deployment/DCS/downstream references;
- transition API/read compatibility strategy;
- lifecycle and retirement behavior during coexistence.

No automatic migration may infer missing Company, Component, Resource, interaction or endpoint facts.

## Gate 2 — target domain/application implementation

Implement target ACC domain behavior:

- Component Deployment commands/lifecycle;
- temporal Deployment Resource Bindings;
- Interaction Definition and immutable Interaction Contract Revision;
- atomic Traffic Alternative contract validation;
- Directed Interaction identity validation/publication.

Required tests must encode every invariant listed in ADR-015.

## Gate 3 — persistence and API migration

Persist target identities and revisions without cross-context foreign keys.

Adapters may preserve compatibility reads for historical/current downstream consumers while migration is in progress. Compatibility code must remain outside peer domain models.

## Gate 4 — UI migration

Replace I31 Application Deployment / Deployment Interaction authoring with Component Deployment and interaction-contract workflows.

The endpoint/network-exposure question must remain absent from UI until separately decided.

## Gate 5 — remove obsolete I31 target path

Only after target data/API/UI are proven and required historical references remain explainable:

- stop new I31 Application Deployment authoring;
- retire obsolete compatibility-only write paths;
- retain historical read/provenance where referenced;
- update `tactical-model.md`, current-state and current-architecture docs to the new implemented state.

## Completion criteria

Migration is complete only when:

1. runtime code no longer treats Application as the deployment unit;
2. Component Deployment is the user/domain deployment identity;
3. Resource binding changes preserve Component Deployment identity;
4. interaction traffic revisions are immutable and atomic;
5. published directed-interaction subjects are validated by ACC;
6. no cross-context persistence FK is required;
7. historical downstream references remain explainable and unchanged;
8. current-state/tactical documentation is updated only after the runtime actually reaches the target.
