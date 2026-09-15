# Network Enforcement Placement — candidate contract

Status: `current target`.

Canonical Tactical DDD: `target-tactical-model.md`.

## Purpose

For a batch of technical source/destination pairs, identify the unordered set of Firewalls relevant enough to inspect, preserve every firewall-local interface branch that may carry the traffic, and expose the ACL/policy names required downstream.

NEP does not prove an end-to-end forwarding path and does not select an optimal route.

## Input

```text
TrafficPair {
    pairId
    sourceAddress
    destinationAddress
}
```

Queries use current successfully collected state and have no `asOf` input.

## Firewall

`Firewall` is the NEP unit of account:

```text
Firewall {
    firewallId
    name
    managementAddress
    platformType
    state: Active | Inactive
}
```

Active Firewalls participate in acquisition and candidate calculation. Connection/profile references, timeouts and per-Firewall acquisition intervals belong to the Firewall profile.

## Current routing state

NEP retains the latest successful routing/interface state plus collection metadata. Refresh validates the replacement state and derived reachability before switching them atomically.

Effective reachability preserves routing context/VRF and all equal-cost interfaces.

```text
EffectiveReachabilitySegment {
    firewallId
    routingContextRef?
    addressFamily
    addressFrom
    addressTo
    interfaces[1..N]
}
```

Segments do not overlap within one Firewall/context/address family.

## Candidate calculation

For each routing context:

```text
sourceInterfaces = resolve(sourceAddress)
destinationInterfaces = resolve(destinationAddress)
localBranches = sourceInterfaces × destinationInterfaces
```

A branch is routing-relevant when source and destination interfaces differ. Any relevant branch makes the Firewall a routing candidate. ECMP/multipath branches are preserved.

Route lookup miss contributes routing=false and is diagnosed; override evaluation still runs. An Active Firewall with no current routing state is skipped and diagnosed.

## Overrides

```text
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
```

Empty fields mean `ANY`. Only Active rules participate. Precedence is:

```text
Include > Exclude > Routing
```

An Include may override a route lookup miss inside valid current state; it does not manufacture missing current state.

## Result

```text
TrafficPairResult {
    pairId
    candidates[]
}

FirewallCandidate {
    firewallId
    firewallName
    localBranches[]
    accessLists[]
    decisionReason
}

LocalBranch {
    routingContextRef?
    sourceInterfaceRef
    destinationInterfaceRef
}

AccessListLocator {
    accessListName
}
```

Candidate output is unordered and is not a route. ACL/policy applicability is evaluated for every retained branch; the result is the distinct union of applicable names.

## Acquisition boundary

NEP acquires only interfaces, routing and minimal policy-binding/locator metadata required for its semantics. Technical Access Evidence independently owns configured policy-body evidence. Shared low-level transport does not merge semantic ownership.

## Diagnostics

At minimum:

```text
CURRENT_ROUTING_STATE_MISSING
ROUTE_LOOKUP_MISS
```

## Invariants

- `candidate != proven traversal`;
- Firewall is the unit of account;
- current routing state and derived reachability switch atomically;
- routing context and ECMP/multipath branches are preserved;
- candidate order has no route meaning;
- `Include > Exclude > Routing`;
- route lookup miss does not block overrides;
- ACL applicability is evaluated on every retained branch;
- final ACL result is the distinct union across branches;
- NEP does not own ACL/policy bodies.
