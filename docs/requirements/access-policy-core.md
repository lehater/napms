# Access Policy product requirements

## Purpose

Access Policy owns current authoritative semantic Policy Rule truth after Access Governance grants or withdraws authorization. It does not own request, approval or withdrawal workflow.

## Authorization subject

```text
GovernedInteractionSubject =
    InteractionContractRevisionRef
  + sourceApplicationDeploymentRef
  + destinationApplicationDeploymentRef
```

ComponentPlacements, ResourceRefs and Resource AddressSpace are not Policy Rule semantic identity. Ordinary placement/address changes therefore do not create a different subject while ApplicationDeployment continuity remains.

## Requirements

- for one governed subject there is at most one authoritative current Policy Rule meaning;
- equivalent, retried or concurrent grants do not create duplicate authoritative Rules;
- multiple Needs/Requests may support one Rule without duplicating semantic authorization;
- rejected Requests create no deny Rule;
- `AuthorizationWithdrawn` makes the subject no longer effectively authorized without rewriting governance provenance;
- earlier grants do not silently restore authorization after withdrawal;
- a later `AuthorizationGranted` for the same subject may re-establish current authorization after current AG obligations are satisfied;
- AP does not infer obligation changes from AD/RC data and does not decide whether reapproval is required; AG expresses authorization changes through grant/withdrawal facts;
- effective authorized-policy queries distinguish authorized-empty, denied, unknown/ambiguous and technical failure where those outcomes are relevant to the query contract;
- technical materialization failure does not erase semantic authorization truth;
- translation to placements, AddressSpace, enforcement placement, configured-policy comparison, rendering and execution is downstream.

## Acceptance examples

1. One required side approved and the other pending -> no effective authorization.
2. Both required sides approve and AG publishes `AuthorizationGranted` -> one authoritative Rule for the governed subject.
3. An authorized side withdraws and AG publishes `AuthorizationWithdrawn` -> the subject stops contributing to effective policy.
4. Resource AddressSpace changes -> Rule identity unchanged.
5. Ordinary ComponentPlacement/Resource migration inside the same logical ApplicationDeployment -> Rule identity unchanged. AG determines whether approval obligations changed materially.
6. After withdrawal, a later AG `AuthorizationGranted` may re-establish current authorization for the same subject.
7. InteractionContractRevision or logical ApplicationDeployment identity changes -> different subject.
8. Missing placement/address truth -> semantic Rule remains while authorization remains granted; technical materialization reports unresolved.

## Ownership boundary

AG owns bilateral governance and approval-obligation semantics. AP reacts only to explicit `AuthorizationGranted` / `AuthorizationWithdrawn` facts. Required Policy Materialization and all technical realization concerns remain downstream of AP.
