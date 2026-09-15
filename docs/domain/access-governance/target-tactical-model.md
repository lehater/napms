# Access Governance — Tactical DDD model

Status: `current target`.

## Purpose

Own bilateral governance history and current authorization for one governed interaction subject while keeping ACC, AD, RC, Authority Management and Access Policy ownership separate.

## Governed subject

```text
GovernedInteractionSubject {
    interactionContractRevisionRef
    sourceApplicationDeploymentRef
    destinationApplicationDeploymentRef
}
```

Subject identity is stable across ordinary placement, Resource and AddressSpace changes while the same logical deployments and contract revision remain.

## Approval obligations

AG resolves obligations from the governed subject plus current AD placements, RC Resource Scope Affiliations and AM EffectiveAuthority. ACC owns interaction meaning; AD owns placements; RC owns scope affiliation; AM owns actor authority.

Each governance side requires exactly one distinct applicable Responsibility Scope. Zero or several scopes on either side are unresolved and fail closed. Source and destination obligations remain separate even when they reference the same scope.

## AccessRequest

```text
AccessRequest {
    accessRequestId
    subject
    processConnectivityNeedRef
    businessJustification
    approvalBasis
    sourceDecision?
    destinationDecision?
    submittedAt
    submittedBy
}
```

A request preserves the obligation basis and provenance used for its decisions. Each side may record at most one terminal `Approved | Rejected` decision for that request. AM authority is checked for the corresponding side/scope/action at decision time. Rejection does not create a semantic deny Policy Rule.

## Current authorization

```text
GovernedAuthorization {
    subject
    effectiveGrant?: AuthorizationGrant
}
```

At most one effective grant exists for one exact subject. A grant requires both current obligations to be satisfied and the approved basis to materially match current obligations.

AG publishes only:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

Either authorized side may withdraw current consent. A material obligation change withdraws the current grant; materially unchanged obligations preserve it. Historical request/decision evidence is never rewritten and cannot silently restore a withdrawn grant.

## Operations

```text
SubmitAccessRequest
RecordApprovalDecision
GrantAuthorization
WithdrawAuthorization
ReevaluateAuthorizationObligations
```

## Invariants

- governed subject identity excludes placements, Resource identities and addresses;
- source and destination obligations are independent;
- current authorization requires both current obligations;
- stale approval basis cannot create or preserve a grant after material obligation change;
- rejection and withdrawal are distinct facts;
- Resource responsibility/contact metadata never substitutes for AM authority;
- Access Policy receives only explicit grant/withdrawal facts.
