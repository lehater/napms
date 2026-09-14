# Access Governance — target Tactical DDD model

Status: `S2 target candidate`.

Date: 2026-09-14.

Strategic owner: **Access Governance** per ADR-019.

Accepted behavior: `docs/requirements/access-governance-g1.md`.

## Purpose

Own explainable bilateral security consent for one concrete deployed interaction while keeping business Need, actor authority evaluation and current Policy Rule truth in their respective contexts.

The core question is:

> Has this exact concrete deployed interaction received and retained consent from both responsible sides, and what history explains that state?

## AuthorizationSubject

`AuthorizationSubject` is a value object identified by trusted external references:

```text
sourceComponentDeploymentRef
+ destinationComponentDeploymentRef
+ interactionContractRevisionRef
```

The referenced ACC interaction must structurally match the two ComponentDeployments.

The subject does not contain IP/Endpoint realization. Address/Endpoint change on the same Resource therefore does not change the subject. Replacing either ComponentDeployment or changing to a materially different Interaction revision yields a different subject requiring new authorization.

## AccessRequest

### Identity

`AccessRequestId` is a stable identity for one explicit attempt to obtain bilateral authorization for one AuthorizationSubject under one recorded business justification basis.

A Request is historical governance evidence. It is not the current authorization itself.

### Immutable historical basis

Once submitted, a Request preserves at least:

- `AccessRequestId`;
- exact `AuthorizationSubject`;
- requester actor reference;
- submission time;
- referenced Connectivity Need / Business Process basis used at submission;
- source/destination governance scope references required for the approval obligations;
- resulting side decisions/provenance or references to them.

Later Need/Process metadata changes do not rewrite the submitted Request.

### Lifecycle meaning

Minimal semantic states required by current behavior are:

```text
Pending
Approved
Rejected
```

`Approved` means both required side obligations were validly approved for this explicit authorization action. `Rejected` means at least one required side rejected while this Request was pending.

Revocation of already granted current authorization does **not** mutate the historical Request from `Approved` to `Rejected`.

Exact cancellation/expiry/admin-abandon semantics are deferred until required.

## ApprovalObligation

Each ordinary AccessRequest creates exactly two semantic obligations:

```text
SourceSide
DestinationSide
```

An `ApprovalObligation` is identified within the Request by its side. It owns whether that required side remains unresolved or has a valid side decision.

Required invariants:

1. Source and destination obligations are independent.
2. Approval order is irrelevant.
3. One approved side cannot authorize the Request while the other is unresolved.
4. A rejection of either required side prevents that Request from becoming Approved.
5. The same actor may satisfy both only when Authority Management independently admits that actor for each obligation's action/scope.
6. Owner/administrator Resource metadata is never substituted for effective approval authority.

## SideDecision

A side decision is immutable governance history for one ApprovalObligation.

Semantic content includes:

```text
side
outcome = Approve | Reject
actorRef
decisionTime
reason? 
governanceScopeRef
authorityBasis/provenance
```

A decision is valid only when Authority Management returns an unambiguous effective admission for the corresponding actor/action/scope/time.

Later role/group changes do not rewrite a historically valid SideDecision.

Whether SideDecision receives a globally stable standalone ID or is identified by Request + Side + decision occurrence is not required by current external behavior and is deferred unless audit/reference use cases require it.

## CurrentConsent

Current authorization consent is **subject-level state**, not a property of one arbitrary historical Request.

Conceptually each AuthorizationSubject has two current consent dimensions:

```text
SourceConsent
DestinationConsent
```

Each side is semantically either currently granted or not currently granted, with provenance of the explicit authorization action that established/withdrew it.

The current subject is authorized only when:

```text
SourceConsent = Granted
AND
DestinationConsent = Granted
```

This distinction is required so that multiple historical approved Requests cannot silently keep authorization alive after one authorized side withdraws consent for the current subject.

## AuthorizationGrant

`AuthorizationGrant` is the domain fact emitted when a new explicit valid authorization action establishes both required current consents for one AuthorizationSubject.

It carries sufficient provenance to correlate the grant with the explicit Request/side decisions that established it.

The exact representation may be a fact/revision associated with the subject-level consent aggregate; it does not need an independently mutable lifecycle.

Repeated processing of the same already-established authorization basis must not create semantically duplicate concurrent grants for the same action.

## Withdrawal / Revocation

Withdrawal acts on the **current AuthorizationSubject consent**, not merely on one historical AccessRequest.

Either side with current effective revoke authority for its corresponding scope may withdraw that side's consent.

Consequences:

```text
source withdrawal OR destination withdrawal
    -> current subject no longer authorized
    -> AuthorizationWithdrawn fact
```

Required invariants:

1. Withdrawal requires no approval from the opposite side.
2. Withdrawal does not delete or rewrite historical Request/SideDecision/Grant provenance.
3. Withdrawal does not delete the Connectivity Need.
4. Old equivalent approved Requests cannot automatically restore authorization after withdrawal.
5. Reauthorization requires a new explicit authorization action that re-establishes both required consents under current authority.
6. Removing the cause of revocation does not itself restore consent.

Exact UX command names and storage/state representation remain downstream.

## Aggregate/invariant boundary

The minimal semantic consistency boundary is one **AuthorizationSubject governance record/case** that can enforce current source/destination consent and serialize explicit grant/withdrawal meaning for that subject.

Historical AccessRequests remain independently identified records associated with the subject and provide the explicit approval actions that may establish new current consent.

This model is intentionally not named after a database aggregate/class. Its domain responsibility is:

> preserve current bilateral consent for one AuthorizationSubject so historical approvals cannot contradict explicit current withdrawal.

A future implementation may realize this boundary in different storage shapes as long as the invariant remains atomic and explainable.

## Domain operations / decisions

### Submit request

Inputs:
- trusted AuthorizationSubject from ACC references;
- current Process-backed Connectivity Need/business basis from Business Connectivity;
- requester identity;
- admitted request authority for source scope.

Result:
- new AccessRequest with SourceSide and DestinationSide obligations.

### Decide side

Inputs:
- pending Request/side obligation;
- actor/outcome/reason;
- effective authority result and provenance for that side/scope/time.

Result:
- immutable SideDecision;
- obligation becomes resolved;
- if either Reject -> Request Rejected;
- if both Approve -> Request Approved and explicit authorization action may establish current bilateral consent / emit AuthorizationGranted.

### Withdraw side consent

Inputs:
- AuthorizationSubject;
- side;
- actor/reason;
- effective revoke authority/provenance.

Result:
- that side's current consent withdrawn;
- subject becomes not authorized;
- AuthorizationWithdrawn emitted for Access Policy consumption.

### Reauthorize

After withdrawal, a new explicit AccessRequest/authorization action is required. Historical approved Requests are evidence only and cannot be replayed as current consent without a new valid decision action.

## Cross-context contracts

### Business Connectivity -> Access Governance

Consumes:
- ConnectivityNeedRef;
- Process/business basis;
- required Interaction meaning;
- current/applicable justification status.

Need is justification, not permission.

### ACC -> Access Governance

Consumes trusted exact AuthorizationSubject references. Access Governance does not own ComponentDeployment/Interaction lifecycle.

### Authority Management -> Access Governance

Consumes effective actor/action/scope/time result plus sufficient authority provenance. Role/group internals remain private to Authority Management.

### Access Governance -> Access Policy

Publishes subject-level facts:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

Pending/rejected Request state is not interpreted as semantic deny policy.

## Authoritative vs derived state

Authoritative in Access Governance:
- AccessRequest history;
- approval obligations;
- SideDecision history;
- current bilateral consent state per AuthorizationSubject;
- grant/withdrawal provenance.

External truth:
- Need/Process meaning;
- ComponentDeployment/Interaction identity;
- actor authority;
- Policy Rule state.

Derived:
- `Request Approved` from both side decisions;
- `subject currently authorized` from current source + destination consent.

## Explicit non-goals

- business Need lifecycle;
- Resource/Endpoint address realization;
- role/group membership resolution;
- current Policy Rule lifecycle;
- firewall/network realization;
- centralized mandatory approver;
- durable deny policy created from rejection.

## Remaining non-blocking questions

- exact time-bounded authorization semantics/representation;
- request cancellation/expiry behavior;
- whether SideDecision requires an externally addressable standalone ID;
- how overlapping responsibility scopes select the applicable side approval scope;
- policy for responsibility-scope changes after authorization;
- exact naming of the subject-level current-consent aggregate/entity in implementation.
