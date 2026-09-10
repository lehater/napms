# Network Context Candidate Set — I26

Status: `accepted I26 WP0 Tactical DDD extension`.

Date: 2026-09-10.

## Purpose

Extend Network Enforcement Placement with a weaker read/query concept for sources that can identify network/enforcement objects relevant to a source/destination pair but cannot prove a forwarding path or traversal order.

This extension does not supersede the I19 `ForwardingPath` model. A proven path remains a stronger optional capability for sources that can truthfully supply it.

## Ubiquitous language

**Network Context** is source-supported knowledge about network/enforcement objects relevant to one Traffic Relation at one logical time.

A **Network Context Candidate** is one provider/device or enforcement identity that a contributing source says is relevant to that Traffic Relation.

Candidate membership means only relevance according to the source contract. It is not a claim that:
- traffic definitely traverses the candidate;
- the candidate occupies a particular position;
- the candidate is necessary or sufficient for connectivity;
- an Access Rule exists;
- configured technical access exists;
- the candidate is a true positive.

## Ownership

Network Enforcement Placement owns:
- the normalized candidate-set read semantics;
- stable Logical Firewall identity where a candidate can be correlated to it;
- provider realization and Enforcement Attachment correspondence already owned by NEP;
- attributable candidate provenance and Network Context knowledge gaps.

NEP does not own:
- application/domain endpoint resolution;
- requirement/decision/policy meaning;
- configured firewall rules or snapshots;
- resource owners/support contacts;
- consumer-specific Checker presentation.

## Candidate identity and shape

A candidate contains at minimum:
- `ProviderRealizationReference`;
- one or more provenance references.

Where the source/correspondence facts support them, it may additionally contain:
- `LogicalFirewallId`;
- `EnforcementAttachmentId`;
- `PathAttachmentReference` as an attachment identity, not a traversal-position claim;
- an opaque source relevance/quality label.

The source relevance label is preserved as source meaning. NEP does not convert it into a numeric probability or universal confidence scale.

## Candidate-set semantics

A `NetworkContextSnapshot` contains:
- zero or more candidates;
- `completeForPair`;
- zero or more knowledge gaps.

Candidate representation is canonicalized only for deterministic output. Canonical sorting has no network/path semantics.

`completeForPair` means only that the contributing source claims its candidate enumeration is complete for the represented pair/time. It does not imply that every candidate is a true positive.

An empty candidate set therefore means only “this source returned no candidates”. It is not `NoForwardingPath` or `NoEnforcement` unless a separately stronger source proves those states.

## Relationship to I19 proven path

```text
weaker capability
TrafficRelation -> NetworkContextCandidate[]

stronger optional capability
TrafficRelation -> ForwardingPath -> ordered TraversalPoint[] -> EnforcementPlacement[]
```

A source that can prove a path may be adapted to the weaker candidate contract by discarding traversal order. The reverse conversion is forbidden: an unordered candidate set cannot be promoted to a `ForwardingPath`.

## Temporal semantics

Every read requires explicit offset-aware `asOf`.

Candidate facts and supporting correspondence facts use their owning temporal/source contracts. Missing or conflicting time knowledge is preserved as a knowledge gap rather than resolved by wall-clock ordering.

## Consumer relationship

Checker consumes the weaker candidate-set contract because its requirement is to show relevant devices and related evidence, not to assert a route.

APR or another consumer that requires proven placement may continue to consume the stronger I19 path-based contract.

This difference is consumer requirement strength, not a new Bounded Context.

## Invariants

- no semantic ordering of candidates;
- no invented probability/confidence;
- no false `NoEnforcement` from absence of candidate evidence;
- provenance is mandatory per candidate;
- duplicate-equivalent candidate identity is rejected/canonicalized before exposure;
- candidate-set knowledge does not authorize or prove configured access.
