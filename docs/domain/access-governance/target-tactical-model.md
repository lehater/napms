# Access Governance — target Tactical DDD model

Status: `DIRTY after 2026-09-15 AD boundary change; affected subject/obligation semantics require Tactical revalidation`.

The previously accepted bilateral-consent model remains valid in principle: Access Request history, independent source/destination obligations, `Grant = source AND destination consent`, either-side withdrawal, immutable decision provenance, and Access Policy handoff remain AG responsibilities.

The previous Tactical model is superseded where it used ACC-owned ComponentDeployment identities.

## Current strategic subject

```text
GovernedInteractionSubject {
    interactionContractRevisionRef       // ACC
    sourceApplicationDeploymentRef       // AD
    destinationApplicationDeploymentRef  // AD
}
```

This subject is stable across ordinary ComponentPlacement replacement, Resource replacement and Resource address change while ApplicationDeployment continuity remains.

## Inputs for obligation determination

AG must derive approval obligations from current applicable placements/resources without moving their ownership:

```text
GovernedInteractionSubject
+ AD ComponentPlacements for source/destination ApplicationDeployments
+ RC effective ResourceScopeAffiliation facts
+ AM EffectiveAuthority for actor/action/scope/time
```

AD owns placement truth; RC owns scope affiliation; AM owns actor authority; AG owns obligation/consent behavior.

## Preserved invariants

- Request history is not current authorization itself.
- Source and destination obligations are independent.
- Both required sides must approve before grant.
- Either authorized side may withdraw its consent.
- Historical approved Requests cannot silently restore withdrawn consent.
- Rejected Requests create no semantic deny Policy Rule.
- Resource owner/administrator/contact metadata is not approval authority.
- `AuthorizationGranted` / `AuthorizationWithdrawn` are the AP handoff.

## Active S1 blockers before Tactical G2

1. Which source/destination ApplicationDeployment pairs are selectable for an Access Request?
2. What happens to current authorization when placement/scope changes alter approval obligations?
3. What approval obligations apply when several Responsibility Scopes simultaneously apply to one side?

Until those behaviors are accepted, exact ApprovalObligation cardinality/selection, reapproval transitions and final AG aggregate/state representation must not be frozen.
