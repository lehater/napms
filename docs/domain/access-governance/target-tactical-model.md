# Access Governance — target Tactical DDD model

Status: `S2 MVP Tactical checkpoint aligned to accepted G1 behavior 2026-09-15`.

## Purpose

Own bilateral access-governance history and current authorization decisions for one governed interaction subject, while keeping Application Deployment, Resource Catalogue, Authority Management and Access Policy semantic ownership separate.

The Tactical model is intentionally limited to the first MVP happy path. It does not add generalized scope algebra, workflow orchestration, persistence schema or implementation protocol.

## Governed subject

```text
GovernedInteractionSubject {
    interactionContractRevisionRef       // ACC
    sourceApplicationDeploymentRef       // AD
    destinationApplicationDeploymentRef  // AD
}
```

The subject identity is stable across ordinary ComponentPlacement replacement, Resource replacement and Resource address change while the same logical ApplicationDeployments and InteractionContractRevision remain.

A material InteractionContractRevision change or replacement of either logical ApplicationDeployment creates a different subject.

## Inputs for obligation determination

AG determines current approval obligations from published upstream truth without taking ownership of that truth:

```text
GovernedInteractionSubject
+ AD current ComponentPlacements for each endpoint Component
+ RC effective ResourceScopeAffiliation facts for placed Resources
+ AM EffectiveAuthority(actor, action, scope, time)
```

Ownership remains:

- ACC: Interaction / Component semantics;
- AD: ApplicationDeployment and ComponentPlacement truth;
- RC: Resource and ResourceScopeAffiliation truth;
- AM: actor/action/scope/time authority;
- AG: obligation, decision, grant and withdrawal semantics.

## MVP obligation resolution

For the first happy path, a selectable/authorizable subject must resolve to exactly one distinct applicable Responsibility Scope on each governance side.

```text
SourceApprovalObligation {
    side = Source
    responsibilityScopeRef
}

DestinationApprovalObligation {
    side = Destination
    responsibilityScopeRef
}
```

Source and destination obligations remain semantically distinct even if both happen to reference the same Responsibility Scope.

If either side resolves to zero or more than one distinct applicable Responsibility Scope, obligations are unresolved and AG fails closed. The subject is not selectable/authorizable for the MVP path.

This is an AG MVP boundary only. It does not prohibit RC from representing several distinct Resource Scope Affiliations.

## Aggregate 1 — AccessRequest

`AccessRequest` owns the immutable historical request/decision record for one deliberate submission.

```text
AccessRequest {
    accessRequestId
    subject: GovernedInteractionSubject
    processConnectivityNeedRef
    businessJustification
    approvalBasis: ApprovalBasisSnapshot
    sourceDecision?
    destinationDecision?
    submittedAt
    submittedBy
}
```

`ApprovalBasisSnapshot` records the semantic basis used for the request and decisions without copying ownership of AD/RC/AM data. For MVP it must preserve enough evidence/provenance to explain:

- which source-side and destination-side Responsibility Scopes formed the obligations;
- the logical time/as-of basis used;
- the relevant upstream evidence/provenance references.

Exact serialization and persistence shape are downstream concerns.

### ApprovalDecision

Each required side may produce at most one terminal decision for a given Request in the MVP flow:

```text
ApprovalDecision {
    side: Source | Destination
    result: Approved | Rejected
    actorRef
    decidedAt
    authorityEvidenceRef
    provenanceRef
}
```

AM authority is checked at decision time for the corresponding side/scope/action. Resource owner/administrator/contact metadata is not approval authority.

A rejected side makes that Request rejected. Rejection remains historical and creates no semantic deny Policy Rule.

When both required sides are Approved, the Request is approval-complete, but AG may publish a grant only if the current obligations still materially match the approved basis. This prevents stale approvals from granting after a scope/placement change has changed the obligations.

The exact internal Request state representation is not domain-critical; an enum such as `Pending | Approved | Rejected` is an implementation choice as long as the observable invariants above hold.

## Aggregate 2 — GovernedAuthorization

Historical Request truth is not current authorization truth.

AG therefore maintains current authorization semantics independently per governed subject:

```text
GovernedAuthorization {
    subject: GovernedInteractionSubject
    effectiveGrant?: AuthorizationGrant
}

AuthorizationGrant {
    authorizationGrantId
    approvalBasisRef
    grantedAt
    provenanceRef
}
```

Absence of `effectiveGrant` means the subject is not currently authorized. No separate `Suspended` product state is required for MVP.

There is at most one effective grant for one exact governed subject.

### Grant

AG may establish `effectiveGrant` only when:

1. both current required governance sides are satisfied;
2. the approved obligation basis materially matches the current resolved obligations;
3. no unresolved zero-scope or multi-scope condition exists.

AG then publishes:

```text
AuthorizationGranted(subject, provenance)
```

Equivalent/retried processing must not create multiple current grants for the same subject; exact idempotency mechanism is implementation detail.

### Explicit side withdrawal

Either authorized governance side may later withdraw its current consent when AM admits the withdrawal action for that side/scope/time.

Withdrawal removes the current effective grant and publishes:

```text
AuthorizationWithdrawn(subject, provenance)
```

The historic approved Request and its decisions are not rewritten. They also cannot silently recreate `effectiveGrant` after withdrawal.

### Obligation-change withdrawal

An ordinary placement, Resource or address change does not by itself alter current authorization.

AG re-evaluates the semantic approval obligations. If the current source/destination obligation pair is materially unchanged, the effective grant remains valid.

If the obligation pair materially changes, AG removes the effective grant and publishes `AuthorizationWithdrawn` with provenance identifying the obligation-change cause.

The same governed subject may later be granted again only from approval evidence satisfying the then-current obligations. Historical approvals for a superseded obligation basis are insufficient by themselves.

Whether still-valid individual consent can be reused across a partially changed obligation set is deliberately deferred. The MVP invariant is only that no effective grant may exist unless all current obligations are satisfied.

## Minimal semantic operations

The Tactical model needs only these domain meanings:

```text
SubmitAccessRequest
RecordApprovalDecision
GrantAuthorization
WithdrawAuthorization
ReevaluateAuthorizationObligations
```

These are semantic operations, not frozen API/command names.

`SubmitAccessRequest` requires a selectable subject with resolvable source/destination obligations.

`RecordApprovalDecision` preserves actor/time/authority/provenance evidence and never mutates earlier decision history into a different meaning.

`GrantAuthorization` establishes current authorization only from a current matching bilateral approval basis.

`WithdrawAuthorization` removes current authorization because an authorized side withdrew consent or another accepted withdrawal cause applies.

`ReevaluateAuthorizationObligations` preserves a grant when obligations are materially unchanged and withdraws it when they materially change.

## Published handoff to Access Policy

AG publishes only current authorization facts needed by AP:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

AP does not evaluate bilateral approvals, Resource Scope Affiliations or actor authority.

Request pending/rejection facts do not create semantic deny Policy Rules.

## MVP invariants

1. Governed subject identity is independent from placement, Resource identity and Resource AddressSpace changes.
2. A submitted Request preserves its business justification and approval basis as historical evidence.
3. Source and destination approval obligations are independent.
4. MVP obligation resolution requires exactly one distinct Responsibility Scope per side.
5. Grant requires both current obligations to be satisfied.
6. A stale approval basis cannot create or preserve a grant after obligations materially change.
7. Either authorized side may withdraw current consent without approval from the other side.
8. Rejection and withdrawal are different facts.
9. Historical Requests/approvals cannot silently restore withdrawn authorization.
10. At most one effective grant exists for one governed subject.
11. Resource responsibility/contact metadata never substitutes for AM authority.
12. AP handoff is only explicit `AuthorizationGranted` / `AuthorizationWithdrawn`.

## Deliberately deferred beyond this MVP checkpoint

- generalized overlapping Responsibility Scope semantics;
- scope hierarchy/precedence;
- mandatory approval by every overlapping scope;
- partial-consent reuse optimization after one obligation changes;
- time-bounded grants beyond the already required evidence timestamps;
- delegation/escalation/quorum workflows;
- reminder/notification workflow;
- a distinct Suspended state;
- persistence schema, ORM entities, REST payloads, queues, retries and locking/version fields.

## Tactical coherence result

The accepted G1 behavior is now expressible without Tactical invention:

- `AccessRequest` owns historical request/approval evidence;
- `GovernedAuthorization` owns current effective authorization per governed subject;
- the separation prevents historical approved Requests from acting as current authorization;
- Q1 selection and Q3 fail-closed scope resolution provide deterministic MVP obligations;
- Q2 obligation-change behavior maps to withdrawal/regrant without changing subject identity or adding Suspended;
- AG -> AP remains a two-fact grant/withdrawal contract.

No remaining S1 product blocker prevents the first Access Governance happy path from proceeding downstream. Additional Tactical detail should be added only when implementation or a concrete journey requires it.
