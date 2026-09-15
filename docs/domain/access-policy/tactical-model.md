# Access Policy — target Tactical DDD model

Status: `S2 MVP edge checkpoint aligned with accepted Access Governance and downstream RPM contracts 2026-09-15`.

## Purpose

Own current authoritative semantic Policy Rule truth after Access Governance grants or withdraws authorization. AP does not run bilateral governance.

## Rule semantic identity

```text
GovernedInteractionSubject =
    InteractionContractRevisionRef
  + sourceApplicationDeploymentRef
  + destinationApplicationDeploymentRef
```

ComponentPlacements, ResourceRefs and Resource AddressSpace are not Policy Rule identity.

For one exact governed subject there is at most one authoritative current Policy Rule meaning. Equivalent/retried grants must not create duplicate authoritative Rules.

## Authorization handoff

AP consumes only explicit AG facts:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

Pending/rejected Requests do not create deny Rules.

`AuthorizationGranted` makes the subject currently authorized. A later equivalent/retried grant is idempotent in semantic effect and must not duplicate current Rule meaning.

`AuthorizationWithdrawn` removes current effective authorization without rewriting historical governance provenance. Old historical grants cannot silently reactivate a withdrawn subject.

A later explicit `AuthorizationGranted` may re-establish current authorization for the same governed subject after AG has satisfied the then-current obligations. This is reactivation of the same subject, not a new semantic subject.

## Obligation-change independence

AP does not inspect ComponentPlacement or ResourceScopeAffiliation changes to decide whether authorization should survive.

AG owns that behavior:

```text
obligations materially unchanged
    -> no AG withdrawal
    -> AP current authorization remains

obligations materially changed
    -> AG AuthorizationWithdrawn
    -> AP current authorization removed

current obligations later satisfied
    -> AG AuthorizationGranted
    -> AP current authorization re-established
```

AP therefore needs no `Suspended` state and no duplicate bilateral approval model.

## Technical independence

Address changes, Resource replacement and ordinary placement changes do not redefine the Policy Rule subject while the source/destination ApplicationDeployment identities and InteractionContractRevision remain the same.

Technical materialization is downstream:

```text
Policy Rule subject
+ ACC traffic semantics
+ AD placements
+ RC Resource HostAddress | Prefix
+ NEP target relevance
-> RPM
```

A missing or temporarily unresolved technical materialization does not erase semantic Policy Rule truth while the subject remains authorized. RPM surfaces that technical incompleteness separately.

## MVP invariants

1. Policy Rule semantic identity is exactly the governed interaction subject.
2. At most one current authoritative Rule meaning exists per subject.
3. AP changes current authorization only from explicit AG grant/withdrawal facts.
4. AP does not infer approval obligations or actor authority.
5. Rejected/pending Requests create no deny Rule.
6. Withdrawal does not rewrite governance history.
7. Historical grants cannot silently restore current authorization.
8. A later explicit grant may reactivate the same subject.
9. Technical placement/address/materialization failure is distinct from semantic authorization withdrawal.

## Deliberately deferred

- exact persistence representation of Rule reactivation/revision history;
- time-bounded authorization beyond explicit upstream facts;
- provenance projection/storage details;
- delivery/idempotency mechanism for AG events;
- persistence schema, ORM shape and API payloads.

## Tactical coherence result

The former upstream AG blocker is closed for the MVP path. Access Policy requires no new product behavior to accommodate placement/scope-driven obligation changes: existing `AuthorizationGranted` / `AuthorizationWithdrawn` semantics are sufficient.

The downstream contract is also explicit: RPM consumes only current effective Policy Rule truth plus published ACC/AD/RC/NEP projections. AP does not own technical materialization, APR comparison, provider rendering or execution.
