# ADR-017 — NEP Candidate and Policy Attachment Contract

Status: `superseded for MVP target by ADR-018; retained as decision history`.

Date: 2026-09-12.

Superseded by: `ADR-018-nep-firewall-current-state-candidate-model.md`.

ADR-017 remains useful as the decision that first made the unordered candidate set primary over the I19 proven-path model. ADR-018 subsequently revalidated the Tactical DDD and supersedes the candidate identity, query-time, interface/attachment and acquisition details below where they conflict.

## Context

The implemented I19 Network Enforcement Placement model can represent a stronger proven forwarding path and ordered enforcement placements. I26 later added a weaker unordered Network Context candidate set for sources that can identify relevant network/enforcement devices without proving traversal.

For the MVP target, forwarding path is not known. The useful business question is instead:

> for one technical source/destination address pair, which enforcement devices are relevant candidates, and for each candidate which interface/policy attachment points are relevant if the traffic traverses that candidate?

Consumers need the returned device and policy locator data to obtain configured policy contents from Technical Access Evidence and perform desired-vs-configured analysis. NEP itself must not own or duplicate ACL/policy contents.

## Decision

### 1. Candidate set is the primary MVP NEP output

For one exact technical source/destination address pair and explicit logical time, NEP returns an unordered set of `EnforcementCandidate` values.

Candidate membership means only:

```text
this device is relevant enough to inspect for this source/destination pair
```

It does **not** mean:

- traffic is proven to traverse the device;
- candidate order is known;
- the candidate is a true positive;
- the candidate is necessary or sufficient for connectivity;
- absence of a candidate proves no path or no enforcement.

The MVP contract must not manufacture a forwarding path from indirect relevance evidence.

### 2. Domain semantics are per address pair; batching is transport/application concern

The domain query is one `TrafficRelation`:

```text
sourceAddress
destinationAddress
asOf
```

An API/application service may batch many pairs in one call for efficiency, but each pair is evaluated independently and produces its own candidate result.

### 3. Each candidate exposes source-supported interface context

For each candidate device, NEP may expose the source-supported interface pair relevant to the queried traffic:

```text
ingressInterfaceRef?
egressInterfaceRef?
```

These values are candidate context, not proof of actual packet traversal.

If the source cannot determine one or both interfaces, NEP preserves that uncertainty instead of inventing an interface.

### 4. Each candidate exposes all relevant policy/ACL attachments

For each candidate, NEP returns zero or more `PolicyAttachment` values that would evaluate the traffic **if the traffic traverses that candidate**.

A policy attachment contains enough locator information for a downstream consumer to correlate configured evidence:

```text
policyRef?          # source-native/stable reference when available
policyName?         # source-visible policy/ACL name when available
attachmentKind      # ingress | global | egress | vendor-specific
interfaceRef?       # absent for global/non-interface attachment
direction?          # inbound | outbound | vendor-specific/none
```

The model does not assume Cisco semantics. A Cisco-like source may expose ingress, global and egress policy attachments; another vendor may expose only one global policy or another source-specific set.

Cardinality is:

```text
EnforcementCandidate -> PolicyAttachment [0..N]
```

### 5. Device/policy locator is the integration seam to Technical Access Evidence

NEP owns relevance and attachment location, not configured policy contents.

The downstream composition may use:

```text
providerDeviceRef
+ policyRef and/or policyName
```

to retrieve the corresponding configured policy evidence from Technical Access Evidence.

Technical Access Evidence remains the owner of captured/imported/configured ACL/policy entries and their provenance.

NEP must not copy ACL entries into its candidate result.

### 6. Proven path remains optional stronger knowledge, not an MVP requirement

The existing I19 proven-path capability may remain as an optional stronger source capability and current-runtime/history concept.

It must not be required by MVP consumers and must not be inferred from the candidate set.

When only candidate evidence exists:

```text
candidate != proven traversal
candidate set != route
candidate order has no network meaning
```

### 7. NEP does not decide policy correctness or generate changes

NEP does not:

- decide whether traffic is authorized;
- inspect ACL/policy entry contents;
- decide whether configured policy satisfies desired policy;
- produce Add/Remove/Replace/No-op;
- render vendor configuration;
- execute device changes.

Those are downstream composition/realization/rendering/execution concerns.

## Target contract

```text
TrafficRelation
    sourceAddress
    destinationAddress
    asOf

        -> EnforcementCandidate[]

EnforcementCandidate
    providerDeviceRef
    logicalFirewallRef?
    ingressInterfaceRef?
    egressInterfaceRef?
    policyAttachments[]
    provenance
    knowledgeGaps[]

PolicyAttachment
    policyRef?
    policyName?
    attachmentKind
    interfaceRef?
    direction?
```

## Required invariants

1. Candidate output is unordered.
2. Candidate membership never asserts proven traversal.
3. No route/path is synthesized from candidate membership.
4. Interface references are returned only when supported by source facts.
5. Each candidate exposes every policy attachment known by the source to be relevant for the pair/candidate combination.
6. A candidate may have zero policy attachments.
7. Global policy attachments do not require an interface reference.
8. Vendor-specific attachment topology is preserved rather than forced into Cisco-only ingress/global/egress semantics.
9. NEP returns policy locators, not policy contents.
10. Technical Access Evidence remains the source of configured ACL/policy entry contents.

## Consequences

- NEP becomes directly useful to desired-vs-configured comparison without pretending to know the route;
- candidate device/interface/policy output provides the exact lookup seam required by Technical Access Evidence;
- the stronger I19 path model is no longer a prerequisite for the MVP;
- current runtime may require migration because existing candidate output does not yet carry the complete policy-attachment contract.
