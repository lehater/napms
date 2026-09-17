# First implementation MVP — Full Vendor-Neutral Policy Export

Status: `G1 revalidated for concrete Component deployments and current-rule revision semantics 2026-09-16`.

## Purpose

The first application goal is to establish current effective Access Policy truth and export that policy as one complete vendor-neutral technical policy view that can be inspected as a table and downloaded in a data format suitable for downstream access-list processing.

The export is intentionally independent of any concrete firewall, device, ACL name or provider syntax.

## Selected semantic scope

```text
current effective Policy Rules
        +
ACC immutable InteractionContractRevision traffic semantics
        +
concrete source/destination Component Deployments
        +
RC Resource + current AddressSpace
        |
        v
Full Vendor-Neutral Policy Export
        |
        +--> table
        `--> CSV/vendor-neutral data export
```

The export is an application/workflow composition, not a Bounded Context. It owns no independent Application, Component Deployment, Resource, Policy Rule or authorization truth.

## Product journey

1. Define one Application with its Components and directed Interactions; an Interaction never crosses Application boundaries.
2. Create immutable Interaction Contract Revisions containing the vendor-neutral traffic alternatives for each Interaction.
3. Define concrete Component Deployments, each representing one Component deployed on exactly one Resource for the first MVP.
4. Define the current Resource -> AddressSpace realization in RC.
5. Propose access between one concrete source Component Deployment and one concrete destination Component Deployment using one exact Interaction Contract Revision.
6. Establish current effective Policy Rule truth through the accepted governance/authorization path. A pending or rejected proposal does not replace an already effective rule revision.
7. Request the complete current effective policy export for the applicable policy set.
8. Materialize every effective Policy Rule into vendor-neutral technical rows using the exact rule revision, the concrete endpoint Component Deployments and RC Resource realization.
9. Inspect the complete result as a table.
10. Export the same materialized result as CSV; the serialized form must preserve the same policy meaning as the table.

Evidence-derived recognition may produce an access proposal/candidate for the same governance path, but evidence does not itself establish effective policy.

## Policy input

Only current effective Policy Rules in the exported policy set participate.

For one concrete directed source/destination Component Deployment pair, the Rule's current exact Interaction Contract Revision defines the effective traffic semantics. A pending or rejected proposal for another revision does not contribute export rows until it becomes the accepted current rule semantics.

Inactive, withdrawn or otherwise non-effective rules/history remain explainable policy/governance truth but do not generate current export rows.

A successful export is complete for the policy set being exported. The product must not silently export only a subset while presenting it as the full policy.

## Materialization

For every effective Policy Rule the workflow shall:

1. identify the exact source and destination Component Deployment references carried by the Rule;
2. load the exact immutable Interaction Contract Revision referenced by the Rule;
3. resolve the revision's owning Interaction, endpoint Components and complete vendor-neutral traffic alternatives;
4. verify that the source Component Deployment realizes the Interaction source Component and the destination Component Deployment realizes the destination Component;
5. resolve each Component Deployment to its exactly one Resource reference for the first MVP;
6. resolve each referenced Resource through RC to its current AddressSpace;
7. emit the vendor-neutral row(s) for every traffic alternative while preserving Policy Rule and source provenance.

The workflow no longer expands a whole-Application deployment through a placement Cartesian product. Independent replicas of the same Component are independent Component Deployments and therefore participate through their own Policy Rules.

## Output

Each successful row preserves at least:

- source `AddressSpace`;
- destination `AddressSpace`;
- protocol/service semantics;
- port or port range where the traffic contract defines one;
- reference to the contributing Policy Rule;
- reference to the exact ACC Interaction Contract Revision;
- source and destination Component Deployment provenance;
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

The export is not partitioned by firewall, device, ACL or provider.

## Completeness

Materialization is successful only when completeness can be proven for the full effective policy set being exported.

The result is `Unresolved` when a required fact is missing, stale, ambiguous or mismatched, including at least:

- effective Policy Rule truth cannot be established;
- an exact Interaction Contract Revision cannot be resolved;
- a referenced source/destination Component Deployment is missing;
- a Component Deployment does not realize the expected Interaction endpoint Component;
- a Component Deployment cannot be resolved to its required Resource;
- a referenced Resource is missing;
- a required Resource has no current AddressSpace;
- any other missing input prevents proving that every effective Rule has been materialized completely.

Missing data is never interpreted as empty policy and is never silently omitted from a successful export. Diagnostics may expose the unresolved cause, but a partial row set must not be presented as the complete policy.

The MVP operates on current owner truth. Time-travel/as-of policy export is not required for the first target slice unless retained as an as-built compatibility requirement. A successful materialization still requires mutually coherent reads; the consistency mechanism is an S3 Architecture decision.

## Non-goals

The first MVP does not require:

- Network Enforcement Placement or firewall selection;
- ACL/policy-name discovery;
- device/provider context;
- configured-state comparison or remediation;
- provider-specific rendering;
- Network Environment Operations or device configuration/execution;
- several simultaneous addresses/interfaces per Resource;
- container/pod/runtime-instance identity beyond the accepted Component Deployment concept.

Technical Access Evidence may be an upstream source for evidence-derived proposals, but configured-state comparison is not required to produce this first vendor-neutral policy export.

## Acceptance examples

1. One effective HTTPS Policy Rule from `CD-A1` to `CD-B1`, whose Resources resolve to two HostAddresses, produces one row with source address, destination address, TCP and destination port 443.
2. The same Component deployed separately as `CD-A1` and `CD-A2` does not automatically produce two rows from one Rule; each concrete deployment relationship must be represented by effective policy truth.
3. A proposal to change an effective Rule from revision R1/TCP-443 to R2/TCP-8443 contributes R1 while pending or rejected, and R2 only after accepted authorization changes current policy.
4. Several effective Policy Rules appear in one complete vendor-neutral policy result rather than separate firewall/device policy views.
5. A Prefix remains a Prefix in output.
6. A missing AddressSpace for any required Resource makes the full export `Unresolved` rather than silently omitting the affected Rule.
7. The displayed table and downloaded CSV represent the same successful materialization result.
8. No exported row implies firewall placement, configured reality, provider syntax or execution state.
9. A non-effective/withdrawn Policy Rule does not contribute current export rows.

## Relationship to current as-built export

`policy-export-core.md` remains the reconstructable as-built normalized desired-policy export contract. It may use compatibility Component Deployment/DCS and logical `asOf` semantics that differ from this target MVP. The target migration must preserve reconstructability without allowing those compatibility identities to override the accepted target behavior above.
