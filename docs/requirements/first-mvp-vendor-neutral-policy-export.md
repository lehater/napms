# First implementation MVP — Full Vendor-Neutral Policy Export

Status: `G1 accepted`.

## Purpose

The first application goal is to establish current effective Access Policy truth and export that policy as one complete vendor-neutral technical policy view that can be inspected as a table and downloaded in a data format suitable for downstream access-list processing.

The export is intentionally independent of any concrete firewall, device, ACL name or provider syntax.

## Selected semantic scope

```text
AP
  current effective Policy Rules
        +
ACC
  immutable InteractionContractRevision traffic semantics
        +
AD
  ApplicationDeployment + current ComponentPlacement -> ResourceRef
        +
RC
  Resource + current AddressSpace = HostAddress | Prefix
        |
        v
Full Vendor-Neutral Policy Export
        |
        +--> table
        `--> CSV/vendor-neutral data export
```

The export is an application/workflow composition, not a Bounded Context. It owns no independent Application, Deployment, Resource, Policy Rule or authorization truth.

## Product journey

1. Define Applications, Components and directed Interactions in ACC.
2. Define source and destination `ApplicationDeployment` identities in AD.
3. Define current `Component -> Resource` placements in AD.
4. Define current `Resource -> AddressSpace` realization in RC.
5. Establish current effective Policy Rule truth in AP through the accepted policy-creation/authorization path.
6. Request the complete current effective policy export for the applicable AP policy set.
7. Materialize every effective Policy Rule into vendor-neutral technical rows using ACC + AD + RC truth.
8. Inspect the complete result as a table.
9. Export the same materialized result as CSV; the serialized form must preserve the same policy meaning as the table.

This MVP does not introduce a direct Policy Rule creation bypass around AP semantics. It requires the product to reach authoritative current AP policy truth, then export that truth completely.

## Policy input

Access Policy is the semantic starting point for export.

Only current effective Policy Rules in the export policy set participate. Inactive, withdrawn or otherwise non-effective rules remain AP truth but do not generate current export rows.

A successful export is complete for the AP policy set being exported. The product must not silently export only a subset while presenting it as the full policy.

## Materialization

For every effective Policy Rule the workflow shall:

1. load the exact governed subject from AP;
2. load the exact immutable `InteractionContractRevision` from ACC;
3. resolve its source and destination Components and complete vendor-neutral traffic alternatives;
4. load the referenced source and destination `ApplicationDeployment` records from AD;
5. verify deployment/Application consistency for the endpoint Components;
6. load the complete current placement set for each endpoint Component;
7. resolve every referenced Resource through RC to its current `AddressSpace`;
8. expand every source placement × destination placement × traffic-alternative combination;
9. emit vendor-neutral policy rows while preserving Policy Rule and source provenance.

The workflow must never choose an arbitrary placement when several exist.

## Output

Each successful row preserves at least:

- source `AddressSpace`;
- destination `AddressSpace`;
- protocol/service semantics;
- port or port range where the traffic contract defines one;
- reference to the contributing AP Policy Rule;
- reference to the exact ACC interaction revision;
- source and destination ApplicationDeployment provenance;
- source and destination Resource provenance.

The tabular representation should expose practical access-list-oriented columns such as:

```text
Source Address
Destination Address
Protocol
Source Port/Range      # when semantically applicable
Destination Port/Range # when semantically applicable
Policy Rule / provenance
```

`HostAddress` and `Prefix` are both valid vendor-neutral address values. A Prefix remains a Prefix and is not expanded into individual hosts merely to produce output.

The export is not partitioned by firewall, device, ACL, provider or `ComparisonScope`.

## Completeness

Materialization is successful only when completeness can be proven for the full effective AP policy set being exported.

The result is `Unresolved` when a required fact is missing, stale, ambiguous or mismatched, including at least:

- effective Policy Rule truth cannot be established;
- an exact InteractionContractRevision cannot be resolved;
- a required source/destination ApplicationDeployment is missing or mismatched;
- a required ComponentPlacement set is incomplete or unavailable;
- a referenced Resource is missing;
- a required Resource has no current AddressSpace;
- any other missing input prevents proving that every effective rule has been materialized completely.

Missing data is never interpreted as empty policy and is never silently omitted from a successful export. Diagnostics may expose the unresolved cause, but a partial row set must not be presented as the complete policy.

The MVP operates on current owner truth. Time-travel/as-of policy export is not required for the first target slice unless retained as an as-built compatibility requirement. A successful materialization still requires mutually coherent reads; the consistency mechanism is an S3 Architecture decision.

## Non-goals

The first MVP does not require:

- Network Enforcement Placement or firewall selection;
- ACL/policy-name discovery;
- device/provider context;
- Technical Access Evidence or configured-state comparison;
- Access Policy Realization drift/remediation;
- provider-specific rendering;
- Network Environment Operations or device configuration/execution.

Those capabilities remain part of the complete target model but do not widen this first implementation goal.

## Acceptance examples

1. One effective HTTPS Policy Rule with one source and one destination placement produces one row with source address, destination address, TCP and destination port 443.
2. Two source placements and three destination placements produce every applicable source × destination row for every traffic alternative of the contributing effective Policy Rule.
3. Several effective Policy Rules appear in one complete vendor-neutral policy result rather than separate firewall/device policy views.
4. A Prefix remains a Prefix in output.
5. A missing AddressSpace for any required Resource makes the full export `Unresolved` rather than silently omitting the affected rule.
6. The displayed table and downloaded CSV represent the same successful materialization result.
7. No exported row implies firewall placement, configured reality, provider syntax or execution state.
8. A non-effective AP Policy Rule does not contribute current export rows.

## Relationship to current as-built export

`policy-export-core.md` remains the reconstructable as-built normalized desired-policy export contract. This selected MVP establishes the target implementation goal and uses current target ownership/vocabulary: AP + ACC + AD + RC -> complete vendor-neutral policy export.
