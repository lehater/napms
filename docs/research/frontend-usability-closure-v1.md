# Frontend usability closure research v1

Status: Stages 1 and 2A implemented; Stage 2B implementation in progress. This file is non-canonical; accepted semantics remain owned by Product, Interface, Domain, HTTP and Verification artifacts.

## Trigger

Hands-on use of the seeded NAPMS dataset exposed four recurring symptoms:

1. loaded detail screens do not expose a visible return/back action;
2. many relationships are rendered as raw stable identifiers instead of recognizable entity labels;
3. many relationship inputs require recalling and typing identifiers instead of selecting candidates;
4. some entity detail views appear non-editable even where Screen/View wording suggests editing.

These symptoms share a usability surface but have different causes and must not be patched as one UI batch.

## Findings

### P1 — navigation continuity needs route hierarchy, not a generic Back button

The immediate symptom came from `DetailPattern`: feature screens supplied `onReturn`, while the MUI provider exposed it only in failure/empty states and even hard-coded `Back to Resources`.

The broader requirement is stronger than restoring that button. Users need stable location context and the ability to return to any conceptual ancestor regardless of browser visit history. The accepted direction is therefore route-derived breadcrumbs:

- breadcrumbs represent canonical workspace/route containment, not browser history;
- ancestor crumbs navigate to deterministic canonical parents;
- the current crumb is non-navigable;
- stable IDs stay in the route but are not primary breadcrumb copy;
- human-readable current-entity labels can replace generic `Resource`/`Application`/`Deployment` labels once Stage 2A supplies them.

The generic Detail-level Back action is therefore removed from normal loaded navigation. Create/edit flows still need explicit cancellation semantics in addition to breadcrumbs when abandoning draft input matters.

Routes such as `/interactions/new` have only a workspace-level parent today; if later UX requires return to a specific Application context, the route/context contract must carry that parent explicitly rather than reconstructing it from browser history.

### P1 — entity-reference presentation is a cross-screen design/API gap

Raw identifiers are primary presentation for relationships across Resources, Applications/Interactions, Deployments, Business Connectivity, Access Requests and Policy Rules.

The target rule is not “hide UUIDs”:

- stable IDs remain canonical technical identity and command payloads;
- when an entity has an accepted recognizable label, that label is primary and the stable ID is secondary inspectable/copyable context;
- entities without an accepted business name, such as AccessRequest or PolicyRule, may still use their stable ID as their own identity while referenced entities are rendered human-readably.

Current HTTP projections often expose only IDs, so this cannot be solved correctly by presentation code alone. It also disproves the current frontend-architecture assumption that existing HTTP projections already contain every fact required by browser screens.

### P1 — relationship selection must prefer recognition over identifier recall

Replacing all ID text fields with unconstrained preload-all dropdowns would be another local workaround. There are at least three selection classes:

1. simple owner reference — choose one Resource, Component, Site or Responsibility Group;
2. dependent reference — after choosing an Interaction, the participant Component must be one of its endpoints;
3. workflow-constrained subject — Access Request deployments, Interaction Revision and Connectivity Need must form a semantically valid subject.

Direction:

- simple references use search-backed recognition with human labels and stable IDs as values;
- dependent references derive later candidates from earlier choices;
- workflow-constrained subjects use task-oriented candidate/read contracts instead of unrelated UUID fields;
- backend validation remains authoritative; frontend narrowing is usability, not authority;
- large catalogues require search/paging semantics rather than loading arbitrary complete lists into a select.

### P1 — Application/Component editability is an upstream semantic gap

`APPLICATION-DETAIL` declares `edit-application`, `add-or-edit-component` and `add-or-edit-interaction`, but:

- it is the only required workspace excluded from `semantic_contract_pilot`;
- it has no complete machine-checked semantic contract;
- OpenAPI exposes create Application, add Component, create Interaction and publish revision, but no update/rename Application or Component operation;
- the Application domain/application service likewise has create/add semantics but no rename/update command.

Therefore adding an Edit button now would invent unsupported domain/API behavior. The edit semantics must be resolved upstream before frontend implementation.

## Engineering-knowledge observation

Pinned Harness already uses “recognition over recall for identifiers and choices” as a Human Interface Quality lens, but current Screen/View semantic closure does not force explicit reference-display or reference-selection semantics.

This is a reusable engineering-knowledge gap, but it is not a Harness Core problem. First define and prove the NAPMS Interface/API contract. If the contract generalizes cleanly, upstream reusable guidance/evaluator behavior to Harness with an acceptance fixture and then repin NAPMS.

## Staged remediation

### Stage 1 — navigation continuity

- define breadcrumbs as canonical route/workspace hierarchy in Interface Design;
- render breadcrumbs in the application shell, independent of concrete detail screens;
- make every ancestor crumb navigate to its deterministic parent route;
- keep current crumb non-navigable and avoid raw UUIDs as primary breadcrumb copy;
- keep explicit Cancel only where an authoring mode needs abandonment semantics;
- verify direct deep links and in-app transitions render the same breadcrumb hierarchy.

### Stage 2A — human-readable relationship display

Pilot on Application/Interaction and Deployment:

- Component: Component name plus Application context, ID secondary;
- Resource: display name, ID secondary;
- Deployment: Component label plus Resource label, Deployment ID secondary;
- Interaction: source/destination Component labels plus purpose, Interaction ID secondary.

Prefer authoritative read projections over ad-hoc frontend N+1 joins. The selected implementation composes labels on the backend read/application boundary from owner contracts: Component names remain owned by Application Communication Catalogue and Resource display names remain owned by Resource Catalogue. Stable references remain unchanged.

### Stage 2B — simple searchable pickers

Selected implementation:

- add a global paged `listComponents` read contract because Components may participate across Application boundaries;
- candidate labels are `Component name — Application name`, while `componentRef` remains the submitted value;
- reuse `listResources` for Resource candidates because it already provides server-side search/paging and `displayName`;
- expose a provider-neutral searchable reference-picker field; MUI Autocomplete is only the downstream provider implementation;
- commands continue to submit stable IDs and backend validation remains authoritative.

### Stage 2C — dependent/task-oriented pickers

Design constrained selection for:

- Business Connectivity: Interaction first, then endpoint participant Component;
- Access Request: eligible subject selection rather than four independent identifiers;
- Policy Rule justification: recognizable Connectivity Need context.

This may require new backend read/query projections and must follow canonical Interface/API design.

### Stage 3 — editability closure

Resolve Application/Component mutation semantics through Product/Domain/API ownership:

- decide mutable facts;
- define concurrency/history semantics;
- add domain/application commands;
- expose OpenAPI operations;
- complete `APPLICATION-DETAIL.semantic_contract`;
- include `APPLICATION-DETAIL` in semantic-contract coverage;
- only then expose Edit controls.

## Acceptance target

The overall issue is closed when:

- every detail/editor flow has deterministic parent/cancel navigation;
- ordinary relationship tasks do not require memorizing stable IDs;
- recognizable labels are primary wherever accepted semantics provide one;
- technical IDs remain inspectable and remain command/reference identity;
- dependent pickers do not misrepresent frontend narrowing as authority;
- every visible edit action is backed by an accepted command and machine-checked Screen/View contract.
