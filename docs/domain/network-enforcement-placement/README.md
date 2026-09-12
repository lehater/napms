# Network Enforcement Placement domain

## Accepted MVP target

The accepted MVP NEP boundary is defined by:

- `../../decisions/ADR-018-nep-firewall-current-state-candidate-model.md` — normative Firewall/current-state/candidate decision;
- `target-tactical-model.md` — canonical Tactical DDD model and ERD;
- `network-context.md` — concise query/output semantics;
- `../../requirements/network-enforcement-placement-core.md` — observable target requirements and acceptance examples.

The MVP contract is:

```text
AnalyzeTrafficPairs(TrafficPair[])
    -> per pair: unordered FirewallCandidate[]
        -> Firewall
        -> resolved source/destination interfaces when available
        -> relevant AccessListLocator[0..N]
```

Base candidate relevance is derived from each Firewall's current local routing state. Active user override rules may then change the result with precedence:

```text
Include > Exclude > Routing
```

Candidate membership means relevance-to-inspect, not proven end-to-end traversal. The candidate set is not a route.

NEP owns the Firewall catalogue/profile, current NEP-relevant routing/interface state, the effective reachability projection, candidate override rules, candidate calculation and relevant ACL/policy locators. Technical Access Evidence owns configured policy contents.

NEP and TAE acquire source data independently and only to the depth required by their own semantics; refreshing NEP routing state must not require fetching complete ACL bodies.

## Current/stronger runtime capability

`tactical-model.md` documents the implemented I19 stronger proven-path model. It remains valid current-runtime/history for sources that can truthfully prove a path, but it is not the MVP target and must not be inferred from candidate evidence.

The current I19/I26 persistence/code therefore differs materially from the accepted target until a separate migration review is completed.
