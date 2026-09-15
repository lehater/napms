# Network Enforcement Placement domain

Current authority:

- `target-tactical-model.md` — Tactical DDD model;
- `network-context.md` — concise query/output contract;
- `../../requirements/network-enforcement-placement-core.md` — observable behavior.

Core contract:

```text
AnalyzeTrafficPairs(TrafficPair[])
    -> per pair: unordered FirewallCandidate[]
        -> relevant firewall-local interface branches
        -> distinct AccessListLocator(accessListName)[]
```

Candidate membership means relevance-to-inspect/affect, not proven traversal. ECMP/multipath branches are preserved. Active override precedence is `Include > Exclude > Routing`.

NEP owns candidate target and ACL/policy-locator relevance, not ACL bodies or configured policy semantics.
