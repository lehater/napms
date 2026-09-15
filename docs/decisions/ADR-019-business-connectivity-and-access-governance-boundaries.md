# ADR-019 — Separate Business Connectivity and Access Governance boundaries

Status: `accepted current target decision`.

Date: 2026-09-14; governed-subject contract aligned 2026-09-15.

## Context

Requirements revalidation established product behavior that the earlier minimal authorization model did not cover:

- deliberate access requires Process-backed business justification through a Connectivity Need;
- a Connectivity Need exists independently from a concrete Access Request and may survive deployment replacement or access revocation;
- ordinary authorization requires independent source-side and destination-side consent;
- either authorized side may withdraw current consent without the other side's approval;
- request/approval/revocation history must remain explainable;
- Access Policy owns current authoritative Policy Rule truth but does not run the bilateral governance workflow.

The previous `Connectivity Requirements` and `Connectivity Decision` contexts do not match these semantics. Preserving their names/boundaries would either mix application-semantic business need with concrete deployment authorization or force bilateral governance back into a single global `Allowed | NotAllowed` decision.

## Decision

### 1. Business Connectivity is a distinct Bounded Context

**Semantic center:** why is application connectivity needed by the business?

Business Connectivity owns:

- Business Process identity/meaning and organizational responsibility needed for connectivity justification;
- Connectivity Need identity/lifecycle;
- the fact that a Process requires an application-level Interaction from a dependent participant/role perspective;
- business attribution and current business-justification reconciliation;
- business importance/criticality semantics when later specified.

A Connectivity Need is application-semantic and references stable ACC Interaction meaning. It is independent from concrete ApplicationDeployment, ComponentPlacement, Resource and IP realization.

Business Connectivity does not authorize access and does not own Access Request/approval/revocation state.

### 2. Access Governance is a distinct Bounded Context

**Semantic center:** has the concrete governed interaction received and retained the required consent from the responsible sides?

Access Governance owns:

- Access Request identity/history;
- exact authorization-subject correlation;
- approval obligations for source and destination sides;
- side approval/rejection decisions and their provenance;
- bilateral grant evaluation;
- withdrawal/revocation of current consent;
- governance history sufficient to explain current and past authorization;
- production of authorization grant/withdrawal facts consumed by Access Policy.

The exact governed subject is:

```text
GovernedInteractionSubject
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
```

The immutable `InteractionContractRevisionRef` fixes decision-relevant traffic semantics. The source/destination `ApplicationDeploymentRef` values identify the two logical deployments whose current placement/scope facts determine governance obligations. Component placements, ResourceRefs and addresses do not become subject identity.

Access Governance consumes Process-backed Need as business justification for deliberate requests. It does not own the Need lifecycle.

### 3. Authority Management remains separate

Authority Management owns whether actor A may perform action X for scope S at time T.

Access Governance consumes effective authority results for request, approval and revocation actions. It must not infer authority from Resource owner/administrator metadata and must not depend on Authority Management's private role/group representation.

### 4. Access Policy remains separate

Access Policy owns the current authoritative Policy Rule truth and effective authorized-policy projection for the exact governed subject.

It consumes authorization grant/withdrawal semantics from Access Governance. It does not re-run bilateral approval or own request/decision history.

Multiple Needs and approved Requests may support one semantic Policy Rule without producing duplicate current Rules for the same governed subject.

### 5. Retire old CR/CD strategic boundaries as target owners

`Connectivity Requirements` and `Connectivity Decision` are not target Bounded Contexts for the revalidated product model.

Useful semantics from them are redistributed:

```text
old Connectivity Requirements
    -> Business Connectivity: Process-backed application-semantic Need

old Connectivity Decision
    -> Access Governance: side decisions, bilateral grant, rejection, revocation, provenance
```

Existing runtime artifacts may remain as as-built compatibility/migration evidence until migrated. Their physical existence does not restore them as target semantic owners.

## Primary semantic contracts

### Business Connectivity -> Access Governance

Purpose: justify a deliberate concrete access request.

Published meaning required by Access Governance:

```text
ConnectivityNeedRef
BusinessProcessRef / explainable business basis
InteractionRef
current/applicable justification status
```

Consumer obligations:

- Access Governance must not convert Need existence into authorization;
- Access Governance preserves the justification basis used by a Request rather than rewriting history when the Need later changes;
- loss of a Need does not itself rewrite approvals or automatically revoke current authorization.

### ACC + AD + RC -> Access Governance

Purpose: supply exact governed subject and current obligation-resolution facts without transferring semantic ownership.

Published meaning:

```text
ACC:
  InteractionContractRevisionRef
  sourceComponentRef
  destinationComponentRef

AD:
  sourceApplicationDeploymentRef + complete current source placements
  destinationApplicationDeploymentRef + complete current destination placements

RC:
  ResourceRef -> current ResponsibilityScopeRef affiliation
```

Access Governance correlates these facts to derive source/destination approval obligations. Missing, unavailable or ambiguous required scope evidence fails closed; it is not interpreted as no obligation.

### Authority Management -> Access Governance

Purpose: determine whether an actor may perform request/approve/withdraw action for the relevant side/scope/time.

Published meaning:

```text
actor + action + scope + time -> admitted | denied | unknown
+ sufficient authority provenance for decision audit
```

Access Governance must not reproduce role/group resolution logic.

### Access Governance -> Access Policy

Purpose: communicate current authorization changes for one exact semantic subject.

Published meaning:

```text
AuthorizationGranted(GovernedInteractionSubject, provenance)
AuthorizationWithdrawn(GovernedInteractionSubject, provenance)
```

Access Policy must not reinterpret pending/rejected governance history as desired allow/deny policy.

## Identity and change consequences

A material ACC traffic change creates a new immutable `InteractionContractRevisionRef`, therefore a new governed subject. An ordinary placement or Resource address change does not create a new subject because placements/addresses are not subject identity.

When placement/scope changes materially alter approval obligations, Access Governance owns reevaluation of current consent and may emit withdrawal. Access Policy reacts only to explicit governance grant/withdrawal facts; it does not independently infer obligation changes.

## Consequences

- Business need and security consent can evolve independently without losing traceability.
- A Need may lead to many Requests; a Request refers to one exact governed interaction subject.
- Revocation does not destroy Need or historical approval facts.
- Access Policy receives a smaller stable semantic contract rather than peer-private workflow state.
- Authority Management remains reusable across catalogue, governance and operational actions.
- The old `Requirement -> Decision -> Rule` chain is not the target strategic model.
- Subject identity is stable across ordinary placement/address changes but changes with an immutable interaction-contract revision.
- Current target Tactical models for BC, AG, AP, ACC, AD, RC and AM remain the authority for detailed invariants.

## Rejected alternative

A single combined Business Connectivity + Access Governance context was rejected because it would couple two independent lifecycles and authoritative facts: enduring business need and concrete bilateral security consent. The accepted requirements require those truths to survive/change independently.
