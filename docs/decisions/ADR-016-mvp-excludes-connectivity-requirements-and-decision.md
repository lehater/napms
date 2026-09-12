# ADR-016 — MVP excludes Connectivity Requirements and Connectivity Decision

Status: `accepted`.

Date: 2026-09-12.

## Context

The implemented product currently contains first-class `Connectivity Requirements` and `Connectivity Decision` bounded contexts. They model, respectively:

- a declared connectivity need that is distinct from authorization;
- an immutable `Allowed | NotAllowed` decision that can precede Access Rule materialization.

For the current MVP this workflow is not required. The MVP must remain focused on describing application communication, resources, authority and authoritative desired Access Rules without forcing an additional `Requirement -> Decision -> Rule` lifecycle.

This decision changes MVP scope only. It does not claim that connectivity-need or explicit approval/denial concepts are invalid for future product growth.

## Decision

### 1. Remove both contexts from MVP scope

The following bounded contexts are **not part of the MVP target**:

- `Connectivity Requirements`;
- `Connectivity Decision`.

They are deferred to post-MVP work and must not be required by target MVP use cases, APIs, UI navigation, persistence design or cross-context contracts.

### 2. Access Policy is the MVP authorization truth

For MVP, an actor admitted by `Authority Management` may create/materialize an `AccessRule` directly from a valid ACC-published directed-interaction subject.

The MVP flow is:

```text
Application Communication Catalogue
    -> valid DirectedInteractionIdentity

Authority Management
    -> actor/action/scope admission

DirectedInteractionIdentity + admitted actor
    -> Access Policy
    -> AccessRule
```

There is no mandatory intermediate `ConnectivityRequirement` or `ConnectivityDecision` record.

The existence of an authoritative `AccessRule` is the MVP statement that the interaction is authorized to exist.

### 3. Minimal provenance remains on Access Rule creation

Removing the two contexts does not remove audit/provenance needs. Access Policy must retain enough creation provenance to explain who created the Rule, when, and under which governance/authority scope.

Exact Access Policy aggregate and persistence fields are decided by the Access Policy target-model review, not by this ADR.

### 4. No durable NotAllowed/required-but-not-authorized state in MVP

MVP does not require persistence of:

- a standalone declared connectivity need;
- a durable `NotAllowed` decision;
- requester/approver workflow state;
- Requirement-to-Policy alignment;
- Decision supersession/validity workflow.

If these capabilities are reintroduced later, they must integrate without changing the semantic identity of existing Access Rules.

### 5. Existing runtime implementation is legacy/current-state, not MVP target

Current code, schemas, APIs and UI for Connectivity Requirements and Connectivity Decision may remain temporarily while the target domain is being revalidated.

Their existence in the current runtime must not be used as evidence that they belong to the MVP target.

Removal/disablement of existing implementation is a separate migration/cleanup task after the target models that depend on this decision are accepted.

## Consequences

- MVP domain flow is smaller and has fewer mandatory bounded-context dependencies;
- Access Policy no longer depends on a final Connectivity Decision for target MVP Rule creation;
- product UX does not need Needs/Decisions workspaces for MVP;
- existing Requirement/Decision runtime remains explainable as historical/current implementation until cleanup;
- post-MVP reintroduction remains possible without redefining ACC or Access Rule semantic identity.
