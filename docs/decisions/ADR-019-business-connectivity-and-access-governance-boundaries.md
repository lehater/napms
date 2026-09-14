# ADR-019 — Separate Business Connectivity and Access Governance boundaries

Status: `accepted`.

Date: 2026-09-14.

Supersedes the MVP-scope assumptions of ADR-016 where it excluded connectivity-need and requester/approver capabilities.

## Context

The 2026-09-14 G1 revalidation established product behavior that ADR-016 intentionally omitted from the earlier MVP:

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

A Connectivity Need is application-semantic and independent from concrete ComponentDeployment, ResourceEndpoint or IP realization.

Business Connectivity does not authorize access and does not own Access Request/approval/revocation state.

### 2. Access Governance is a distinct Bounded Context

**Semantic center:** has the concrete deployed interaction received and retained the required consent from the responsible sides?

Access Governance owns:

- Access Request identity/history;
- concrete authorization subject correlation: source ComponentDeployment + destination ComponentDeployment + stable Interaction meaning;
- approval obligations for source and destination sides;
- side approval/rejection decisions and their provenance;
- bilateral grant evaluation;
- withdrawal/revocation of current consent;
- governance history sufficient to explain current and past authorization;
- production of authorization grant/withdrawal facts consumed by Access Policy.

Access Governance consumes Process-backed Need as business justification for deliberate requests. It does not own the Need lifecycle.

### 3. Authority Management remains separate

Authority Management owns whether actor A may perform action X for scope S at time T.

Access Governance consumes effective authority results for request, approval and revocation actions. It must not infer authority from Resource owner/administrator metadata and must not depend on Authority Management's private role/group representation.

### 4. Access Policy remains separate

Access Policy owns the current authoritative Policy Rule truth and effective authorized-policy projection.

It consumes authorization grant/withdrawal semantics from Access Governance. It does not re-run bilateral approval or own request/decision history.

Multiple Needs and approved Requests may support one semantic Policy Rule without producing duplicate current Rules.

### 5. Retire old CR/CD strategic boundaries as target owners

`Connectivity Requirements` and `Connectivity Decision` are no longer target Bounded Contexts for the revalidated product model.

Useful semantics from them are redistributed:

```text
old Connectivity Requirements
    -> Business Connectivity: Process-backed application-semantic Need

old Connectivity Decision
    -> Access Governance: side decisions, bilateral grant, rejection, revocation, provenance
```

Their existing domain/runtime artifacts remain migration and historical evidence until explicitly removed or migrated.

## Primary semantic contracts

### Business Connectivity -> Access Governance

Purpose: justify a deliberate concrete access request.

Published meaning required by Access Governance:

```text
ConnectivityNeedRef
BusinessProcessRef / explainable business basis
required Interaction meaning
current/applicable justification status
```

Consumer obligations:

- Access Governance must not convert Need existence into authorization;
- Access Governance preserves the justification basis used by a Request rather than rewriting history when the Need later changes;
- loss of a Need does not itself rewrite approvals or automatically revoke current authorization.

### Authority Management -> Access Governance

Purpose: determine whether an actor may perform request/approve/revoke action for the relevant side/scope/time.

Published meaning:

```text
actor + action + scope + time -> admitted | denied | unknown/ambiguous
+ sufficient authority provenance for decision audit
```

Access Governance must not reproduce role/group resolution logic.

### Access Governance -> Access Policy

Purpose: communicate current authorization changes for an exact semantic subject.

Published meaning:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

where `subject` is the concrete source/destination ComponentDeployment interaction identity accepted by the current requirements.

Access Policy must not reinterpret pending/rejected governance history as desired allow/deny policy.

## Consequences

- Business need and security consent can evolve independently without losing traceability.
- A Need may lead to many Requests; a Request refers to one concrete deployed authorization subject.
- Revocation does not destroy Need or historical approval facts.
- Access Policy receives a smaller stable semantic contract rather than peer-private workflow state.
- Authority Management remains reusable across catalogue, governance and operational actions.
- The old `Requirement -> Decision -> Rule` chain is no longer the target strategic model.
- Tactical DDD for Business Connectivity, Access Governance and Access Policy must be revalidated before G2 can pass for their affected semantics.

## Rejected alternative

A single combined Business Connectivity + Access Governance context was rejected because it would couple two independent lifecycles and authoritative facts: enduring business need and concrete bilateral security consent. The accepted requirements explicitly require those truths to survive/change independently.
