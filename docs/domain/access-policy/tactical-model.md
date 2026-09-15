# Access Policy — Tactical DDD model

## Purpose

Access Policy owns current authoritative semantic Policy Rule truth after Access Governance grants or withdraws authorization. AP does not run bilateral governance, infer actor authority or own technical realization.

## Rule semantic identity

```text
GovernedInteractionSubject =
    InteractionContractRevisionRef
  + sourceApplicationDeploymentRef
  + destinationApplicationDeploymentRef
```

ComponentPlacements, ResourceRefs and Resource AddressSpace are not Policy Rule identity.

For one governed subject there is at most one authoritative current Policy Rule meaning.

## Authorization handoff

AP consumes explicit AG facts:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

Pending or rejected Requests do not create deny Rules.

`AuthorizationGranted` makes the subject currently authorized. Equivalent or retried grants are idempotent in semantic effect and must not duplicate current Rule meaning.

`AuthorizationWithdrawn` removes current effective authorization. Earlier grants cannot reactivate the subject after withdrawal. A later explicit `AuthorizationGranted` may re-establish authorization for the same semantic subject.

## Obligation-change independence

AP does not inspect ComponentPlacement or ResourceScopeAffiliation changes to decide whether authorization remains valid. AG owns approval-obligation evaluation and emits grant or withdrawal facts when the authorization meaning changes.

AP therefore has no `Suspended` state and no duplicate bilateral approval model.

## Technical independence

Address changes, Resource replacement and ordinary placement changes do not redefine the Policy Rule subject while the source/destination ApplicationDeployment identities and InteractionContractRevision remain the same.

Technical materialization is downstream:

```text
Policy Rule subject
+ ACC traffic semantics
+ AD placements
+ RC Resource AddressSpace
+ NEP target relevance
-> RPM
```

Unresolved technical materialization does not erase semantic Policy Rule truth while the governed subject remains authorized. RPM reports technical incompleteness separately.

## Invariants

1. Policy Rule semantic identity is exactly the governed interaction subject.
2. At most one current authoritative Rule meaning exists per subject.
3. AP changes current authorization only from explicit AG grant or withdrawal facts.
4. Equivalent grant delivery is semantically idempotent.
5. AP does not infer approval obligations or actor authority.
6. Pending or rejected Requests create no deny Rule.
7. Withdrawal prevents earlier grants from silently restoring current authorization.
8. A later explicit grant may reactivate the same subject.
9. Placement, address or materialization failure is distinct from authorization withdrawal.
10. RPM consumes current effective Policy Rule truth plus published ACC/AD/RC/NEP projections; AP does not own RPM, APR comparison, provider rendering or execution.

Persistence representation, event delivery mechanics, schema/ORM choices and API payloads are Architecture or implementation concerns rather than AP domain semantics.
