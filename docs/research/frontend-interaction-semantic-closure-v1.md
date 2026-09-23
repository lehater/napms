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
| Submit Access Request | Need → Interaction Revision → source/destination Deployment dependency graph | blocked: no authoritative candidate source/query for the admissible chain |
| Attach Policy Rule justification | Connectivity Need reference contract | blocked: no authoritative candidate source/query for matching/current Needs |
| Edit/Rename Application | visible edit intent exists | blocked: no accepted mutation operation |
| Edit/Rename Component | visible edit intent exists | blocked: no accepted mutation operation |
| Direct detail navigation | parent + direct-link semantics | closed |

## Access Request dependency proof

The authoring contract explicitly models:

```text
Current Connectivity Need
  → Interaction Revision
    → Source Deployment
    → Destination Deployment
```

Source and Destination Deployment are constrained by the selected revision's endpoint Components. The backend remains authoritative for AP-01/AP-02 admission.

The current machine interface can validate submitted IDs but does not expose an authoritative candidate query that lets the UI construct this admissible chain without inventing cross-aggregate joins. Therefore the Screen/View contract deliberately omits candidate sources and strict closure remains REJECTED.

Four independent UUID text inputs cannot satisfy this contract.

## Policy Rule justification

`AttachJustificationRequest.needRef` is a stable identity, but the machine interface currently exposes no authoritative candidate query for current/matching Connectivity Needs. The UI must not derive that candidate set from incidental local data. Strict closure remains REJECTED until that upstream read capability is accepted.

## Mutation gap

APPLICATION-DETAIL still declares edit intent for Application/Component. Current OpenAPI has create/read operations but no accepted rename/update Application or Component operation.

The Screen/View contract does not invent those mutations. The action findings remain intentional blockers until Product/Domain/Application/Machine Interface establish the mutation semantics or the edit intent is removed from accepted Human Interface knowledge.

## Next design work

P0:
1. define authoritative Access Request candidate/read capability that returns admissible Need + exact revision + source/destination Deployment candidates;
2. define authoritative Policy Rule justification Need candidate capability;
3. resolve Application/Component edit intent against accepted mutation semantics.

P1:
4. expose human-readable display projection for Access Request and Policy Rule subject references in machine reads, not only opaque IDs;
5. add project-specific acceptance cases for stale/dependent candidate invalidation.

P2:
6. generate User Task Map, Workspace Map, Action Matrix, Reference Dependency Map and State Transition Map from the canonical contracts.
