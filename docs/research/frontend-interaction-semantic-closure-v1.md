# NAPMS frontend interaction semantic closure

Status: materialized on research branch; implementation intentionally blocked by unresolved upstream interaction semantics.

## Confirmed model

NAPMS adopts the Harness strict interaction-closure model without adding a project-local UI semantic authority.

The canonical chain remains:

```text
Requirements / Journey
  → Domain + Security + Machine Interface
  → Human Interface + Navigation
  → Screen/View semantic closure
  → Presentation provider
  → Frontend Architecture / Component / Verification / Test
  → Frontend Implementation
```

Screen/View acceptance is now evaluated for every required workspace.

## Materialized closure

The project now records:

- task trace for every required workspace;
- deterministic route parent/direct-link semantics;
- explicit success/cancel transitions for authoring/workflow routes;
- exhaustive accepted HTTP outcome handling;
- explicit command-backed user actions;
- human-readable reference identity plus stable technical identity;
- authoritative candidate source where the existing API already provides one;
- explicit dependency edges for dependent selections.

## Scenario status

| Scenario | Materialized semantics | Status |
|---|---|---|
| Create Application | task, create command, route, complete outcomes | closed |
| Add Component | existing addComponent command and route outcomes | closed |
| Create Interaction | source/destination Component candidate operations and stable submitted refs | closed |
| Create Deployment | Component/Resource display-selection contracts via listComponents/listResources | closed |
| Declare Connectivity Need | Interaction candidates plus participant derived from selected Interaction endpoints | closed |
| Submit Access Request | one task-oriented composite candidate carrying current Need + exact Interaction Revision + source/destination Deployment tuple | blocked: `listAccessRequestCandidates` is not yet an accepted machine operation |
| Attach Policy Rule justification | matching current Connectivity Need reference contract | blocked: `listPolicyRuleJustificationCandidates` is not yet an accepted machine operation |
| Edit/Rename Application | visible edit intent exists | blocked: no accepted mutation operation |
| Edit/Rename Component | visible edit intent exists | blocked: no accepted mutation operation |
| Direct detail navigation | parent + direct-link semantics | closed |

## Access Request dependency proof

The domain/application semantics form the dependency:

```text
Current Connectivity Need
  → owning Interaction
  → selected immutable Interaction Revision
  → source/destination Components
  → matching source/destination Component Deployments
```

The user task does not require four independent choices. The Screen/View contract therefore models one composite `access-request-subject` candidate whose stable identity is:

```text
[needRef, interactionRevisionRef, sourceDeploymentRef, destinationDeploymentRef]
```

The proposed application query `listAccessRequestCandidates` owns construction of admissible tuples and their human-readable labels. `submitAccessRequest` still receives the stable IDs and independently revalidates current Need, revision ownership, deployment endpoint compatibility and scoped authority.

This is simpler than a four-picker dependency graph and proves that four independent UUID text inputs are not an acceptable realization. Until the candidate query exists, strict closure remains REJECTED.

## Policy Rule justification

`AttachJustificationRequest.needRef` is a stable identity, but the machine interface currently exposes no authoritative candidate query for current/matching Connectivity Needs. The UI must not derive that candidate set from incidental local data. Strict closure remains REJECTED until that upstream read capability is accepted.

## Mutation gap

APPLICATION-DETAIL still declares edit intent for Application/Component. Current OpenAPI has create/read operations but no accepted rename/update Application or Component operation.

The Screen/View contract does not invent those mutations. The action findings remain intentional blockers until Product/Domain/Application/Machine Interface establish the mutation semantics or the edit intent is removed from accepted Human Interface knowledge.

## Next design work

P0:
1. define `listAccessRequestCandidates` as a task-oriented application query returning admissible Need + exact revision + source/destination Deployment tuples;
2. define `listPolicyRuleJustificationCandidates` for current Needs matching a selected PolicyRule subject;
3. enforce matching-Need semantics in the justification mutation path, not only currentness;
4. resolve Application/Component edit intent against accepted mutation semantics.

P1:
5. expose human-readable display projection for Access Request and Policy Rule subject references in machine reads, not only opaque IDs;
6. add project-specific acceptance cases for stale/dependent candidate invalidation.

P2:
7. generate User Task Map, Workspace Map, Action Matrix, Reference Dependency Map and State Transition Map from the canonical contracts.
