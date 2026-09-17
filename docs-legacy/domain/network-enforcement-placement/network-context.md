# Network Enforcement Placement — MVP Candidate Contract

Status: `accepted MVP target by ADR-018; implementation migration pending`.

Date: 2026-09-13.

Decision: `../../decisions/ADR-018-nep-firewall-current-state-candidate-model.md`.

Canonical Tactical DDD: `target-tactical-model.md`.

## Purpose

For a batch of technical source/destination pairs, identify the unordered set of known Firewalls that are relevant enough to inspect, preserve every firewall-local interface branch that may carry the traffic, and expose the ACL/policy names required by downstream consumers.

NEP does not prove an end-to-end forwarding path and does not select one optimal route.

## Input

```text
TrafficPair[]

TrafficPair
    pairId
    sourceAddress
    destinationAddress
```

Each pair is evaluated independently. MVP uses current successfully collected state and has no `asOf` input.

## Firewall

`Firewall` is the NEP unit of account. No separate physical Device entity is required for MVP.

```text
Firewall
    firewallId
    name
    managementAddress
    platformType
    state: Active | Inactive
```

`Active` participates in polling/candidate calculation. `Inactive` is retained but ignored. The administrator changes this state directly through the Web UI.

The Firewall profile also contains connection/profile reference, connection timeouts and per-firewall acquisition intervals.

## Current routing state

NEP stores only the latest successful routing/interface state plus `collectedAt`. Historical NEP routing snapshots are not retained as domain history.

Refresh builds and validates the new state and its reachability projection, then switches them atomically.

## Effective reachability

Routing precedence is normalized into a persisted query projection. Routing contexts such as VRFs are preserved when present.

Conceptually:

```text
EffectiveReachabilitySegment
    firewallId
    routingContextRef?
    addressFamily
    addressFrom
    addressTo
    interfaces[1..N]
```

Address segments do not overlap within one Firewall/context/address-family scope. A segment may reference multiple interfaces for ECMP/multipath.

NEP never chooses one arbitrary ECMP winner.

## Candidate calculation

For every routing context:

```text
sourceInterfaces = resolve(sourceAddress)
destinationInterfaces = resolve(destinationAddress)
localBranches = sourceInterfaces × destinationInterfaces
```

A branch is routing-relevant when source and destination interfaces differ. A Firewall is a routing candidate if at least one routing-relevant branch exists.

All routing-relevant branches are retained for ACL/policy selection.

If route lookup for source or destination misses in an otherwise valid current state, routing contributes false and the miss is logged. Override evaluation still runs.

If an Active Firewall has no current routing state, it is skipped for MVP candidate calculation and the condition is logged/diagnosed.

## Candidate override rules

```text
CandidateOverrideRule
    ruleId
    firewallId
    state: Active | Inactive
    effect: Include | Exclude

    sourceAddressRange?
    destinationAddressRange?
    sourceInterfaceRef?
    destinationInterfaceRef?
```

Empty fields mean `ANY`. Only Active rules participate.

Interface conditions match only if one resolved local branch in one routing context satisfies all specified interface conditions.

Decision precedence:

```text
Include > Exclude > Routing
```

A matching Include may override a route lookup miss in valid current state. It does not manufacture current state when the Firewall has never been successfully collected.

## Access-list result

For each candidate, the platform adapter evaluates every retained local branch and returns the distinct union of applicable ACL/policy names:

```text
AccessListLocator
    accessListName
```

NEP does not assume parallel branches use the same ACL, even when that is common operationally.

MVP does not require stable `accessListRef`, attachment kind, direction, evaluation position, or ingress/global/egress classification. Those details remain adapter knowledge until a concrete consumer needs them.

## Target result

```text
TrafficPairResult
    pairId
    candidates[]

FirewallCandidate
    firewallId
    firewallName
    localBranches[]
    accessLists[]
    decisionReason

LocalBranch
    routingContextRef?
    sourceInterfaceRef
    destinationInterfaceRef

AccessListLocator
    accessListName
```

Candidate output is unordered and is not a route.

## Independent acquisition

NEP and Technical Access Evidence acquire source data independently.

NEP reads only:

```text
interfaces
routing
minimal policy-binding/locator metadata
```

TAE independently reads ACL/policy bodies when configured evidence is required, ideally only for the selected access-list names where the platform permits targeted reads.

The acquisitions may have different schedules, commands/APIs, timeouts and capture identities.

## Per-Firewall acquisition profile

Minimum current settings:

```text
ConnectionSettings
    connectTimeout
    operationTimeout

AcquisitionPolicy
    routingPollInterval?
    policyBindingPollInterval?
```

This permits static-routing Firewalls to be refreshed rarely and dynamic-routing Firewalls more frequently, while high-latency links may use larger timeouts.

Retry/backoff/error-policy details are deferred.

## Diagnostics

At minimum these conditions are made observable in logs/diagnostics:

```text
CURRENT_ROUTING_STATE_MISSING
ROUTE_LOOKUP_MISS
```

No separate NetworkResolution domain lifecycle/state machine is introduced.

## Invariants

- `candidate != proven traversal`;
- candidate set is unordered and is not a route;
- `Firewall` is the unit of account;
- no separate physical Device is required by MVP;
- current state only; no historical NEP routing snapshots;
- routing state + derived reachability switch atomically;
- VRF/routing context is preserved when present;
- ECMP/multipath interfaces and branches are preserved, not collapsed;
- any routing-relevant branch may make the Firewall a routing candidate;
- `Include > Exclude > Routing`;
- route lookup miss does not block overrides;
- missing current routing state is diagnosed and skipped;
- ACL applicability is evaluated on every retained branch;
- final ACL result is the distinct union of names across branches;
- NEP does not own ACL/policy bodies;
- NEP and TAE acquisition are independent.

## Relationship to I19

The existing I19 `ForwardingPath`/`TraversalPoint` model remains an optional stronger/current-runtime capability for sources that can truthfully prove an ordered path. It is not an MVP prerequisite and must not be synthesized from candidate evidence.
