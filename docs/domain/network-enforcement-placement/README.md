# Network Enforcement Placement domain

Current NEP authority:

- `target-tactical-model.md` — canonical Tactical DDD model;
- `network-context.md` — query/output semantics;
- `../../requirements/network-enforcement-placement-core.md` — observable behavior;
- `../../decisions/ADR-018-nep-firewall-current-state-candidate-model.md` — still-binding placement decision.

Core contract:

```text
AnalyzeTrafficPairs(TrafficPair[])
    -> per pair: unordered FirewallCandidate[]
        -> Firewall
        -> relevant firewall-local interface branches
        -> AccessListLocator(accessListName)[]
```

Candidate membership means relevance-to-inspect/affect, not a proven route. ECMP/multipath branches are preserved. Active override precedence is `Include > Exclude > Routing`.

NEP owns candidate target and ACL/policy-locator relevance, not ACL bodies or configured policy semantics.
