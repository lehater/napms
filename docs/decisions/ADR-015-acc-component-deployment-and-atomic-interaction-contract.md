# ADR-015 — ACC Component Deployment and Atomic Interaction Contract

Status: `superseded as target on 2026-09-15; retained for rationale and migration history`.

Date: 2026-09-12. Amended 2026-09-14. Superseded 2026-09-15 by the accepted Application Deployment boundary and Interaction-template clarification.

## Historical decision

ADR-015 established two useful conclusions that remain valid:

- Interaction is directed Component-to-Component communication with immutable atomic traffic revisions;
- cross-context references are opaque semantic identities rather than shared persistence/navigation.

It also placed `ComponentDeployment -> ResourceRef` inside ACC and defined:

```text
DirectedInteractionIdentity =
    sourceComponentDeploymentRef
  + destinationComponentDeploymentRef
  + interactionContractRevisionRef
```

Those deployment-ownership and subject-identity parts are now superseded.

## Current target replacement

```text
ACC
  Application / Component / InteractionContractRevision

AD
  ApplicationDeployment
  ComponentPlacement -> ResourceRef

RC
  Resource -> effective AddressSpace [0..1] = HostAddress | Prefix
```

Current governed subject:

```text
GovernedInteractionSubject =
    interactionContractRevisionRef
  + sourceApplicationDeploymentRef
  + destinationApplicationDeploymentRef
```

ACC therefore no longer owns ComponentDeployment or Resource binding. `ResourceEndpoint` is not part of the current target realization model.

## Why retained

This ADR remains useful only to explain the design path and migration from legacy/current runtime identities. It must not be used as current target authority. Current authority is `docs/domain/strategic-model.md`, `docs/domain/context-map.md`, ACC `target-model.md`, AD `boundary.md`, and RC `target-realization-model.md`.
