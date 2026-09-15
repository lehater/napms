# Access Policy product requirements

Status: `G1 target behavior retained; governed subject aligned 2026-09-15`.

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
- effective authorized-policy queries distinguish authorized-empty, denied, unknown/ambiguous and technical failure;
- technical materialization failure does not erase semantic authorization truth;
- translation to AD placements, RC AddressSpace, NEP placement, configured-policy comparison, rendering and execution is downstream.

## Acceptance examples

1. One side approved and the other pending -> no effective authorization.
2. Both required sides approve -> one authoritative Rule for the governed subject.
3. Either authorized side withdraws -> subject stops contributing to effective policy.
4. Resource address/prefix changes -> Rule identity unchanged.
5. Ordinary ComponentPlacement/Resource migration within the same logical ApplicationDeployment -> Rule subject identity unchanged; any changed approval obligations are handled by AG according to the still-open S1 behavior.
6. InteractionContractRevision or logical ApplicationDeployment identity changes -> different subject.
7. Missing placement/address evidence -> semantic Rule remains; RPM reports unresolved technical materialization.

## Upstream blocker

AP must not invent the effect of changed approval obligations. AG's S1 decisions on scope changes/overlap are upstream of any AP transition semantics that depend on them.
