# Access Policy — target Tactical DDD model

Status: `S2 affected-edge candidate; subject identity aligned, AG behavior blockers remain upstream`.

## Purpose

Own current authoritative semantic Policy Rule truth after Access Governance grants or withdraws authorization. AP does not run bilateral governance.

## Rule semantic identity

```text
GovernedInteractionSubject =
    InteractionContractRevisionRef
  + sourceApplicationDeploymentRef
  + destinationApplicationDeploymentRef
```

This replaces the former ComponentDeployment triple. ComponentPlacements, ResourceRefs and Resource AddressSpace are not Policy Rule identity.

For one exact governed subject there is at most one authoritative current Policy Rule meaning. Equivalent/retried grants must not create duplicate authoritative Rules.

## Authorization handoff

AP consumes only explicit AG facts:

```text
AuthorizationGranted(subject, provenance)
AuthorizationWithdrawn(subject, provenance)
```

Pending/rejected requests do not create deny Rules. Withdrawal removes current effective authorization without rewriting historical governance provenance. Old grants cannot silently reactivate a withdrawn subject.

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

## Remaining Tactical work

Exact Rule revision/reactivation representation, time-bounded authorization and provenance projection remain Tactical. AG's active S1 questions about changed approval obligations must be resolved before AP can freeze behavior that depends on those transitions.
