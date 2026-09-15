# First implementation MVP — Required Access Matrix

Status: `G1 accepted product scope — project-owner decision 2026-09-15`.

Date: 2026-09-15.

## Purpose

Define the smallest implementation MVP that proves the application/deployment/resource model can produce a useful network-policy result without requiring governance, authorization, firewall placement, configured-state comparison or device execution.

The user shall be able to form a set of intended application communications, materialize them into a complete vendor-neutral required access matrix, inspect that matrix as a table and export the same policy representation.

This is the first implementation MVP. It is intentionally a strict subset of the wider accepted target-domain baseline.

## User journey

The minimum successful journey is:

1. define Applications, Components and directed Interactions in Application Communication Catalogue;
2. use an exact immutable `InteractionContractRevision` for each selected communication;
3. define source and destination `ApplicationDeployment` identities;
4. define current `Component -> Resource` placements in Application Deployment;
5. define current `Resource -> AddressSpace` realization in Resource Catalogue;
6. select the exact interaction/deployment triples to include in the policy;
7. materialize the complete current required access matrix;
8. inspect the result in a tabular view;
9. export the same vendor-neutral result in a downloadable representation.

No firewall or access-list placement is required for this journey.

## MVP semantic scope

Only these Bounded Context owners are required by the first implementation MVP:

```text
ACC
  Application / Component / Interaction
  immutable InteractionContractRevision
        |
        v
AD
  ApplicationDeployment
  current Set<(ComponentRef, ResourceRef)>
        |
        v
RC
  Resource
  current AddressSpace = HostAddress | Prefix
```

The materialization itself is an application/workflow composition. It is not a new Bounded Context and owns no independent Application, Deployment, Resource or authorization truth.

## Policy selection

Because Access Governance and Access Policy are outside this MVP, the workflow must not infer authorization.

For the first implementation MVP, one policy-selection item identifies exactly:

```text
InteractionContractRevisionRef
+ sourceApplicationDeploymentRef
+ destinationApplicationDeploymentRef
```

The selection is input to the materialization workflow. It is not an `Access Policy` Rule and does not claim that the communication has been organizationally approved or authorized.

The first version does not require a durable policy-selection aggregate. Persistence of the selection may be added only if a concrete user journey requires it.

## Required Access Matrix materialization

For every selected item, the workflow shall:

1. load the exact immutable `InteractionContractRevision` from ACC;
2. resolve the source and destination endpoint Components from that revision;
3. load the selected source and destination `ApplicationDeployment` records from AD;
4. verify that each deployment belongs to the Application that owns the corresponding endpoint Component;
5. load the complete current placement set for each endpoint Component;
6. resolve every referenced Resource through RC to its current `AddressSpace`;
7. expand every applicable source placement × destination placement × traffic alternative combination;
8. emit the resulting vendor-neutral required access rows without provider or firewall semantics.

The workflow must not choose one arbitrary placement when several are present.

## Output

A successful materialization produces one global `Required Access Matrix` for the requested selection.

Each row must preserve at least:

- source `AddressSpace`;
- destination `AddressSpace`;
- vendor-neutral traffic meaning from the exact `InteractionContractRevision`;
- provenance sufficient to trace the row back to the interaction revision, source/destination deployments and source/destination Resources that produced it.

The UI may flatten vendor-neutral traffic meaning into practical columns such as protocol and port/range where applicable.

The first MVP does not partition output by firewall, device, ACL or `ComparisonScope`.

`HostAddress` and `Prefix` remain valid `AddressSpace` values in this global matrix because no enforcement-placement interpretation is performed at this stage.

## Completeness and unresolved behavior

A successful matrix must be complete for the submitted policy selection.

Materialization is `Unresolved` rather than successfully partial when any selected item cannot be proven complete, including when:

- an exact interaction revision cannot be resolved;
- a selected deployment does not match the corresponding endpoint Application;
- required current placement truth is unavailable or ambiguous;
- a referenced Resource cannot be resolved;
- a required current Resource `AddressSpace` is missing or unavailable;
- any other required owner fact is unavailable in a way that prevents complete expansion.

Missing data must never be interpreted as an empty policy or silently omitted from a successful result.

A UI may show diagnostics for unresolved items, but it must not present an incomplete row set as a complete required policy.

## Current-state boundary

The first MVP operates on current owner truth only.

Historical `asOf` export, temporal placement history and historical Resource realization are not required. The implementation must still avoid mixing mutually inconsistent reads within one successful materialization attempt; the exact consistency mechanism belongs to S3 Architecture.

## Presentation and export

The first MVP requires:

- one tabular view of the complete Required Access Matrix;
- one downloadable representation of the same rows; CSV is sufficient;
- stable row provenance sufficient to explain why a row exists.

Provider-specific configuration syntax is explicitly not required.

## Explicit non-goals

The first implementation MVP does not require:

- Business Connectivity;
- Access Governance;
- Authority Management;
- Access Policy authorization or Rule lifecycle;
- Network Enforcement Placement;
- firewall/device/access-list selection;
- `ComparisonScope`;
- Technical Access Evidence;
- Provider Policy Interpreter;
- Access Policy Realization configured-vs-required comparison;
- drift detection or remediation intent;
- Provider Policy Renderer;
- Network Environment Operations;
- device configuration generation or execution;
- historical/as-of policy export;
- provider-specific policy syntax.

These remain valid parts of the wider target model and may be added in later vertical slices. They are not prerequisites for this MVP.

## Acceptance examples

1. One selected HTTPS interaction, one source placement and one destination placement produce one required access row.
2. One selected interaction with two source placements and three destination placements produces every applicable source × destination row for every traffic alternative.
3. Two selected interaction/deployment triples are materialized into one global table rather than separate firewall-specific policies.
4. A Resource represented by a Prefix remains a Prefix in the matrix; the MVP does not expand it into hosts merely to produce output.
5. Missing AddressSpace for one required Resource makes the materialization unresolved instead of silently omitting that communication.
6. The displayed table and downloaded export represent the same successful materialization result.
7. No output row implies that the communication is approved, authorized, placed on a firewall, configured or enforced.

## Relationship to the wider target model

The wider Strategic DDD baseline remains authoritative for the eventual product. This MVP deliberately stops before authorization and enforcement-placement semantics.

Later slices may introduce:

```text
Business Connectivity
    -> Access Governance
    -> Access Policy

Required access / authorized policy
    -> Network Enforcement Placement
    -> configured-state comparison / APR
    -> provider rendering
    -> Network Environment Operations
```

Those later capabilities must consume the same ACC, AD and RC owner truths rather than redefining them.
