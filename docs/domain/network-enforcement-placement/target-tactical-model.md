# Network Enforcement Placement — Tactical DDD model

Status: `current target`.

## Purpose

Own current Firewall/routing state and derive conservative enforcement candidates for technical TrafficPairs. Candidate means relevant to inspect/affect, not proven end-to-end traversal.

## Owned state

```text
Firewall {
    firewallId
    name
    managementAddress
    platformType
    state: Active | Inactive
    credentialRef
    connectionSettings
    acquisitionPolicy
}

CandidateOverrideRule {
    ruleId
    firewallId
    state: Active | Inactive
    effect: Include | Exclude
    sourceAddressRange?
    destinationAddressRange?
    sourceInterfaceRef?
    destinationInterfaceRef?
}

CurrentRoutingState {
    firewallId
    collectedAt
    stateVersion
    interfaces[]
    routingEntries[]
}
```

NEP also owns a rebuildable effective-reachability projection and enough current policy-binding metadata to resolve relevant ACL/policy names.

## Derived values

```text
TrafficPair {
    pairId
    sourceAddress
    destinationAddress
}

LocalBranch {
    routingContextRef?
    sourceInterfaceRef
    destinationInterfaceRef
}

FirewallCandidate {
    firewallId
    firewallName
    localBranches[]
    accessLists[]
    decisionReason
}

AccessListLocator {
    accessListName
}
```

## Reachability

Effective reachability normalizes route precedence while preserving routing-context identity and every equal-cost interface. Address segments do not overlap within one Firewall/context/address family. The projection is replaceable and switches atomically with current routing state.

For each TrafficPair and routing context:

```text
sourceInterfaces = resolve(sourceAddress)
destinationInterfaces = resolve(destinationAddress)
localBranches = sourceInterfaces × destinationInterfaces
```

A branch is routing-relevant when source and destination interfaces differ. Any such branch makes the Firewall routing-relevant. NEP never picks an arbitrary ECMP winner.

## Overrides

Only Active override rules participate. Empty selector fields mean `ANY`.

```text
Include > Exclude > Routing
```

A matching Include may override a route lookup miss in valid current state. Missing current routing state cannot be overridden into invented state.

## ACL/policy locator semantics

For a candidate Firewall, policy applicability is evaluated on every retained LocalBranch.

```text
result = DISTINCT UNION(applicable accessListName for each retained branch)
```

`AccessListLocator` contains `accessListName`. ACL/policy bodies belong to Technical Access Evidence, not NEP.

## Diagnostics

```text
CURRENT_ROUTING_STATE_MISSING
ROUTE_LOOKUP_MISS
```

Operational misses are observable but do not create a separate domain lifecycle.

## Invariants

1. Firewall is the NEP unit of account.
2. Firewall state is `Active | Inactive`.
3. Query input is current-state `TrafficPair[]` with no `asOf`.
4. Candidate means relevance-to-inspect, not proven traversal.
5. Candidate output is unordered.
6. Current routing state and derived reachability switch atomically.
7. Routing-context/VRF identity is preserved when present.
8. ECMP/multipath branches are preserved.
9. Route lookup miss contributes routing=false and is diagnosed.
10. Missing current routing state skips the Firewall and is diagnosed.
11. Override precedence is `Include > Exclude > Routing`.
12. ACL/policy applicability is evaluated for every retained branch.
13. Access-list output is the distinct union of names across branches.
14. NEP and Technical Access Evidence have separate semantic ownership even if low-level provider access is shared.
