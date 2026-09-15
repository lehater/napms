# First implementation MVP — Required Access Matrix

Status: `G1 accepted`.

## Purpose

The user can describe intended application communications, deployments and resource address realization, then obtain one complete vendor-neutral required access matrix, inspect it as a table and export the same result.

No governance, authorization, firewall placement, configured-state comparison or device execution is required.

## User journey

1. Define Applications, Components and directed Interactions in ACC.
2. Select an exact immutable `InteractionContractRevision`.
3. Define source and destination `ApplicationDeployment` identities in AD.
4. Define current `Component -> Resource` placements in AD.
5. Define current `Resource -> AddressSpace` realization in RC.
6. Select the interaction/deployment triples to include.
7. Materialize the complete current Required Access Matrix.
8. Inspect the result as a table.
9. Export the same vendor-neutral result; CSV is sufficient.

## Semantic scope

```text
ACC
  Application / Component / Interaction
  immutable InteractionContractRevision
        +
AD
  ApplicationDeployment
  current Set<(ComponentRef, ResourceRef)>
        +
RC
  Resource
  current AddressSpace = HostAddress | Prefix
        |
        v
Required Access Matrix materialization
```

The materialization is an application/workflow composition, not a Bounded Context. It owns no independent Application, Deployment, Resource or authorization truth.

## Selection input

One selection item is exactly:

```text
InteractionContractRevisionRef
+ sourceApplicationDeploymentRef
+ destinationApplicationDeploymentRef
```

The selection is materialization input, not an Access Policy Rule and not a claim of organizational authorization. A durable selection aggregate is not required.

## Materialization

For every selected item the workflow shall:

1. load the exact `InteractionContractRevision` from ACC;
2. resolve its source and destination Components;
3. load the selected source and destination `ApplicationDeployment` records from AD;
4. verify that each deployment belongs to the Application owning the corresponding endpoint Component;
5. load the complete current placement set for each endpoint Component;
6. resolve every referenced Resource through RC to its current `AddressSpace`;
7. expand every source placement × destination placement × traffic alternative combination;
8. emit vendor-neutral required-access rows without provider/firewall semantics.

The workflow must never choose an arbitrary placement when several exist.

## Output

A successful materialization produces one global `Required Access Matrix` for the submitted selection.

Each row preserves at least:
- source `AddressSpace`;
- destination `AddressSpace`;
- vendor-neutral traffic meaning from the exact contract revision;
- provenance to the interaction revision, source/destination deployments and source/destination Resources.

The table may expose practical traffic columns such as protocol and port/range. `HostAddress` and `Prefix` are both valid values. Output is not partitioned by firewall, device, ACL or `ComparisonScope`.

## Completeness

A successful matrix is complete for the submitted selection. Materialization is `Unresolved` when completeness cannot be proven, including missing/mismatched interaction revision, deployment, placement, Resource or AddressSpace truth.

Missing data is never interpreted as an empty policy and never silently omitted from a successful result. A UI may show diagnostics for `Unresolved` but must not present a partial row set as complete.

The MVP operates on current owner truth only. Time-travel/as-of policy queries are not part of this slice. A successful materialization must still use mutually coherent reads; the consistency mechanism is an S3 Architecture decision.

## Non-goals

The first implementation does not require Business Connectivity, Access Governance, Authority Management, Access Policy, Network Enforcement Placement, firewall/ACL selection, Technical Access Evidence, configured-policy interpretation, Access Policy Realization, drift/remediation, provider rendering, Network Environment Operations or device configuration/execution.

These capabilities remain part of the complete target model but do not widen this implementation slice.

## Acceptance examples

1. One HTTPS interaction with one source and one destination placement produces one row.
2. Two source placements and three destination placements produce every applicable source × destination row for every traffic alternative.
3. Several selected triples appear in one global matrix, not separate firewall-specific policies.
4. A Prefix remains a Prefix; it is not expanded into hosts merely to produce output.
5. Missing AddressSpace for a required Resource makes the result `Unresolved`.
6. The displayed table and downloaded export represent the same successful materialization result.
7. No output row implies approval, authorization, firewall placement, configuration or enforcement.
