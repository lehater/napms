# Network Context Candidate Boundary — I26

Status: `accepted I26 WP0 architecture contract`.

Date: 2026-09-10.

## Purpose

Define the weaker NEP read boundary required by Checker without weakening or fabricating the stronger I19 proven-path contract.

## Dependency direction

```text
NEP Domain candidate model
    ^
    |
NEP Application ReadNetworkContext + consumer-owned port
    ^
    |
source adapter / composition
```

The boundary preserves the existing rules:
- NEP Domain/Application import no peer bounded context;
- provider/device references remain opaque normalized references;
- no Access Policy, TAE, Resource Catalogue or APR SQL is read from NEP core;
- consumer composition may join owner outputs outside those owners.

## Read contract

```text
ReadNetworkContext(
    TrafficRelation(sourceIp, destinationIp),
    asOf,
    inputProvenance?
)
  -> NetworkContextResult
       candidates[]
       completeForPair
       knowledgeGaps[]
```

Each candidate carries:
- provider realization reference;
- attributable provenance;
- optional Logical Firewall / Enforcement Attachment / Path Attachment correspondence when source facts support it;
- optional opaque source relevance label.

Candidate order is deterministic serialization only and has no route/traversal meaning.

## Relationship to proven path

The existing I19 path query remains available to consumers that require and can support stronger placement proof.

Allowed adaptation:

```text
proven path/placements
    -> discard traversal order
    -> unordered Network Context candidates
```

Forbidden adaptation:

```text
unordered candidates
    -X-> synthesize ForwardingPath
```

Checker depends on the weaker contract.

## Source and persistence strategy

I26 does not require a new durable candidate store. A Network Context adapter may:
- read a source that natively returns candidate-set knowledge;
- project an existing stronger NEP capture to candidates;
- use a deterministic local stub for the supported local target while a real source is absent.

A future source-specific durable adapter is introduced only when a concrete integration requires it.

## Failure semantics

- missing/partial candidate knowledge -> result with `completeForPair=false` and attributable knowledge gaps;
- source ambiguity -> preserve all candidates/gaps; do not select a winner;
- no candidates -> empty candidate set, not `NoForwardingPath` or `NoEnforcement`;
- unsupported relevance semantics -> omit `sourceRelevance` rather than invent a score.

## Checker composition

Checker may compose Network Context candidates with:
- Resource Catalogue endpoint/resource projections;
- ACC/application communication projections;
- Requirement/Decision/Access Policy projections;
- TAE snapshots and technical entries;
- Resource Responsibility projections.

Those joins are owned by the Checker application/read composition. They do not move truth ownership into NEP.
