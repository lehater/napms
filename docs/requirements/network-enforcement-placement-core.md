# Network Enforcement Placement requirements

## Purpose

For each technical source/destination address pair, identify every known Firewall that is a relevant candidate enforcement location and the distinct ACL/policy names on that Firewall where the pair may be affected.

A candidate means relevance to inspect or affect, not proof of end-to-end traversal. NEP answers where traffic may be affected; it does not decide what policy change is required.

## Input and output

Input:

```text
TrafficPair {
    pairId
    sourceAddress
    destinationAddress
}
```

Each pair produces its own result:

```text
TrafficPairResult {
    pairId
    enforcementLocations[0..N]
}

EnforcementLocation {
    firewallId
    accessListNames[0..N]
    metadata {
        snapshotCollectedAt?
        decisionSource: Routing | IncludeOverride
    }
}
```

Candidate ordering has no route meaning. A candidate Firewall remains in the result even when no relevant ACL/policy name can be determined; `accessListNames=[]` is valid.

## Firewall catalogue and acquisition

NEP maintains the Firewall information required to identify and acquire enforcement state, including stable `firewallId`, name, management/platform information and administrative state `Active | Inactive`.

Active Firewalls participate in acquisition and candidate calculation. Inactive Firewalls remain registered but do not participate.

Per-Firewall acquisition behavior is independently configurable for polling interval, stale-data threshold and connection/operation timeout. Secret material remains external and is referenced opaquely.

NEP calculates from the latest successful network state available for a Firewall. A failed newer acquisition does not erase the last successful state.

The state used for one result must provide mutually coherent routing/interface and ACL binding/name facts. When state contributes to a result, `snapshotCollectedAt` truthfully identifies the freshness of those decision-critical facts. Acquisition/session mechanics belong to Architecture.

Configured ACL/policy bodies are not required for NEP candidate selection.

## Stale and missing state

If the latest successful state exceeds the configured stale threshold, NEP diagnoses `CURRENT_STATE_STALE` and still calculates from that state. The result exposes the snapshot timestamp so downstream consumers can apply their own freshness policy.

If no successful network-state snapshot exists, routing evidence is unavailable and NEP diagnoses `CURRENT_STATE_MISSING`. Missing state on one Firewall does not prevent independently determinable results for other Firewalls or Traffic Pairs.

A matching Include override that has no routing/interface condition may still establish candidate relevance without a network snapshot.

## Routing evidence

Routing relevance exists when at least one applicable local resolution places source and destination on different interfaces.

If source or destination cannot be resolved from otherwise available state, routing contributes false and NEP diagnoses `ROUTE_LOOKUP_MISS`; override evaluation still runs.

All relevant routing alternatives are considered. ECMP/multipath alternatives are not collapsed arbitrarily. Routing contexts such as VRFs are respected; because `TrafficPair` does not select a routing context, every applicable context is considered.

Local routing branches/contexts are calculation evidence, not required public output.

## Candidate overrides

```text
CandidateOverrideRule {
    ruleId
    firewallId
    state: Active | Inactive
    effect: Include | Exclude
    sourceAddressRanges[0..N]
    destinationAddressRanges[0..N]
    sourceInterface?
    destinationInterface?
}
```

Only Active rules participate. Empty address-range collections mean `ANY`; omitted interface conditions mean `ANY`.

Within one rule, source ranges are alternatives and destination ranges are alternatives, producing full-mesh matching: `ANY(sourceAddressRanges) AND ANY(destinationAddressRanges)`.

Address conditions evaluate directly against the queried pair. A specified interface condition matches only when routing/interface evidence contains an applicable local alternative satisfying that condition. If both interface conditions are specified, one local alternative must satisfy both.

An override with no interface conditions does not require routing/interface resolution.

Precedence is:

```text
Include > Exclude > Routing
```

Precedence applies after matching rules are determined. A matching Include establishes candidate relevance even without routing evidence when its own conditions are satisfied. Otherwise a matching Exclude suppresses the candidate; otherwise routing evidence determines candidate membership.

## Candidate metadata

`decisionSource` is `Routing` when routing established candidate relevance and `IncludeOverride` when an Include override established it.

`snapshotCollectedAt` is the freshness timestamp of network state actually used for that result. It is null when no applicable network snapshot contributed, such as a routing-independent Include before any successful acquisition.

Override-rule age is not network-state freshness.

## ACL/policy names

For every candidate Firewall, NEP derives all ACL/policy names relevant to the pair from every applicable local routing alternative and returns their distinct union.

Parallel/equal-cost alternatives may use different policies and all relevant names are preserved. A candidate with no known relevant policy name remains a valid candidate.

Interfaces, local branches, routing contexts, attachment kinds, direction/evaluation position and provider binding topology may be used internally but are not part of the current public result contract.

## Ownership boundary

NEP does not require or own configured ACL/policy bodies to answer candidate placement. It does not compute required-vs-configured drift, design policy changes, render provider configuration or execute mutation.

Downstream consumers may use `firewallId + accessListName` as a comparison/inspection locator under their own contracts.

## Partial availability

Acquisition failure, missing state or stale state for one Firewall does not prevent results for other independent Firewalls or Traffic Pairs. Operational acquisition diagnostics remain observability facts and are not copied into every successful candidate result unless part of the public contract above.

## Acceptance examples

1. Each TrafficPair receives its own unordered candidate list.
2. Source resolves to `inside` and destination to `outside` on a Firewall -> routing candidate.
3. Both resolve only to the same interface -> not a routing candidate absent overrides.
4. Destination lookup misses -> routing contributes false; a routing-independent Include may still include the Firewall.
5. No successful snapshot -> routing cannot include the Firewall, but a matching routing-independent Include may return it with `accessListNames=[]` and `snapshotCollectedAt=null`.
6. Matching Include and Exclude -> Include wins.
7. Multiple source/destination ranges in one override match their full mesh.
8. Interface-constrained Include requires matching interface evidence; an otherwise identical unconstrained Include does not.
9. ECMP alternatives are all evaluated and their distinct policy names are unioned.
10. A candidate with no relevant policy binding is still returned with an empty policy-name set.
11. Multiple applicable VRFs are all considered because the input selects none.
12. Stale latest-successful state is still used, diagnosed as stale and exposed with its timestamp.
13. A failed new acquisition does not erase an older successful snapshot.
14. Failure on one Firewall does not fail independent Firewall/pair results.
15. Firewalls may use different acquisition timing/timeout settings without changing NEP semantics.
16. NEP candidate selection does not require ACL/policy body acquisition.
17. One result exposes a single snapshot timestamp only when it truthfully represents the decision-critical network facts used for that result.
