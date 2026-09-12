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
        -> every relevant firewall-local interface branch
        -> distinct AccessListLocator(accessListName)[] across those branches
```

Base candidate relevance is derived from each Firewall's current local routing state. ECMP/multipath is preserved as multiple local branches; NEP does not choose one arbitrary route. Routing contexts such as VRFs are retained when present.

Active user override rules may change the result with precedence:

```text
Include > Exclude > Routing
```

Candidate membership means relevance-to-inspect, not proven end-to-end traversal. The candidate set is not a route.

`Firewall` is the NEP unit of account. Its MVP state is simply `Active | Inactive`, administered through the Web UI. No separate physical Device or Firewall lifecycle-command model is required.

NEP keeps only current routing/interface state, derives a persisted reachability projection for set-based batch evaluation, and logs route lookup/current-state misses rather than creating extra domain lifecycle concepts.

NEP owns relevant ACL/policy-name selection but not ACL bodies. Technical Access Evidence owns configured policy contents. NEP and TAE acquire source data independently and only to the depth required by their own semantics; refreshing NEP routing state must not require fetching complete ACL bodies.

## Current/stronger runtime capability

`tactical-model.md` documents the implemented I19 stronger proven-path model. It remains valid current-runtime/history for sources that can truthfully prove a path, but it is not the MVP target and must not be inferred from candidate evidence.

The current I19/I26 persistence/code therefore differs materially from the accepted target until a separate migration review is completed.
