# Access Policy product requirements

Status: `G1 target behavior aligned with accepted Access Governance MVP behavior 2026-09-15`.

## Purpose

Access Policy owns current authoritative semantic Policy Rule truth after Access Governance grants or withdraws authorization. It does not own request/approval/revocation workflow.

## Authorization subject

```text
GovernedInteractionSubject =
    InteractionContractRevisionRef
  + sourceApplicationDeploymentRef
  + destinationApplicationDeploymentRef
```

ComponentPlacements, ResourceRefs and Resource `HostAddress | Prefix` realization are not Policy Rule semantic identity. Ordinary placement/address changes therefore do not create a different subject while ApplicationDeployment continuity remains.

## Requirements

- for one exact governed subject there shall be at most one authoritative current Policy Rule meaning;
- equivalent/retried/concurrent grants shall not create duplicate authoritative Rules;
- multiple Needs/Requests may support one Rule without duplication;
- rejected Requests create no deny Rule;
- `AuthorizationWithdrawn` makes the subject no longer effectively authorized without rewriting historical governance provenance;
- old historical grants cannot silently restore current authorization;
- a later `AuthorizationGranted` for the same governed subject may re-establish current authorization after AG has satisfied the then-current approval obligations;
- AP does not infer obligation changes from AD/RC data and does not decide whether reapproval is required; AG owns that decision and expresses it only through explicit grant/withdrawal facts;
- effective authorized-policy queries distinguish authorized-empty, denied, unknown/ambiguous and technical failure;
- technical materialization failure does not erase semantic authorization truth;
- translation to AD placements, RC AddressSpace, NEP placement, configured-policy comparison, rendering and execution is downstream.

## Acceptance examples

1. One side approved and the other pending -> no effective authorization.
2. Both required sides approve and AG publishes `AuthorizationGranted` -> one authoritative Rule for the governed subject.
3. Either authorized side withdraws and AG publishes `AuthorizationWithdrawn` -> subject stops contributing to effective policy.
4. Resource address/prefix changes -> Rule identity unchanged.
5. Ordinary ComponentPlacement/Resource migration within the same logical ApplicationDeployment -> Rule subject identity unchanged. If AG determines that approval obligations are materially unchanged, current authorization remains. If AG determines they materially changed, AG publishes `AuthorizationWithdrawn` and AP stops treating the subject as currently authorized.
6. After such withdrawal, a later AG `AuthorizationGranted` for the same subject re-establishes current authorization without creating a different subject identity.
7. InteractionContractRevision or logical ApplicationDeployment identity changes -> different subject.
8. Missing placement/address evidence -> semantic Rule remains while authorization remains granted; RPM reports unresolved technical materialization.

## Upstream alignment

The former Access Governance blocker is closed for the MVP path. AG now owns and has accepted the consequence of changed approval obligations. AP remains intentionally ignorant of the bilateral reason for a transition and reacts only to explicit `AuthorizationGranted` / `AuthorizationWithdrawn` facts.
