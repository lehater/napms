# Network Enforcement Placement — MVP Candidate Contract

Status: `accepted MVP target by ADR-017; implementation migration pending`.

Date: 2026-09-12.

Decision: `../../decisions/ADR-017-nep-candidate-policy-attachment-contract.md`.

## Purpose

For one technical source/destination address pair and explicit logical time, identify the unordered set of enforcement-device candidates that are relevant enough to inspect, and expose the source-supported interface and policy/ACL attachment information needed by downstream consumers.

NEP does not claim a forwarding path unless a separate stronger source can actually prove one.

## Traffic Relation

Domain semantics are per pair:

```text
TrafficRelation
    sourceAddress
    destinationAddress
    asOf
```

An outer API/application service may batch many pairs, but each pair is evaluated independently.

## Enforcement Candidate

An `EnforcementCandidate` means only that the source considers a device/enforcement identity relevant to the queried pair.

It is not proof that traffic traverses the device and carries no semantic ordering.

Target shape:

```text
EnforcementCandidate
    providerDeviceRef
    logicalFirewallRef?
    ingressInterfaceRef?
    egressInterfaceRef?
    policyAttachments[]
    provenance
    knowledgeGaps[]
```

`ingressInterfaceRef` and `egressInterfaceRef` are returned only when supported by source facts. They describe candidate context, not proven traversal.

## Policy Attachment

For each candidate, NEP exposes zero or more policy/ACL attachments that are relevant **if traffic traverses that candidate**.

```text
PolicyAttachment
    policyRef?
    policyName?
    attachmentKind
    interfaceRef?
    direction?
```

`attachmentKind` is source-normalized only to the degree supported by the vendor/source contract. Expected values include:

```text
ingress
global
egress
vendor-specific
```

A Cisco-like source may expose ingress-interface inbound ACL, global ACL and egress-interface outbound ACL. Another vendor may expose only a global policy or a different set of attachment locations.

The model therefore does not require exactly three attachment points and does not force non-Cisco devices into Cisco semantics.

## Integration with Technical Access Evidence

NEP returns policy locators, not policy contents.

A downstream composition may use:

```text
providerDeviceRef
+ policyRef and/or policyName
```

to retrieve configured ACL/policy evidence from Technical Access Evidence.

Technical Access Evidence owns the captured/imported/configured policy entries and provenance. NEP does not copy or interpret those entries.

## Candidate-set semantics

A candidate result contains:

```text
TrafficRelation
+ EnforcementCandidate[]
+ result provenance
+ knowledge gaps
```

Invariants:

- candidate output is unordered;
- `candidate != proven traversal`;
- candidate set is not a route;
- absence of a candidate does not prove no path or no enforcement;
- candidates may be incomplete or false-positive according to source quality;
- no universal probability/confidence score is invented;
- missing interface/policy knowledge is preserved as a knowledge gap;
- each candidate exposes every policy attachment known by the source to be relevant for that pair/candidate combination;
- policy attachment cardinality is `0..N`.

## Relationship to the implemented I19 path model

The existing I19 model remains a valid stronger optional/current-runtime capability when a source can truthfully prove a path:

```text
TrafficRelation -> ForwardingPath -> ordered TraversalPoint[]
```

It is not the MVP prerequisite and must not be synthesized from candidate evidence.

For MVP consumers:

```text
TrafficRelation -> EnforcementCandidate[]
```

is the primary NEP contract.

## Ownership boundary

NEP owns:

- candidate relevance semantics;
- source-supported candidate ingress/egress interface context;
- source-supported policy/ACL attachment location and locator metadata;
- Logical Firewall correlation where available;
- candidate provenance and knowledge gaps.

NEP does not own:

- Resource or application-domain endpoint identity;
- desired Access Rule state;
- ACL/policy contents;
- configured technical evidence;
- desired-vs-configured reconciliation;
- Add/Remove/Replace/No-op decisions;
- vendor configuration rendering;
- device execution.
