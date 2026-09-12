# Network Enforcement Placement — MVP Candidate Contract

Status: `accepted MVP target by ADR-018; implementation migration pending`.

Date: 2026-09-13.

Decision: `../../decisions/ADR-018-nep-firewall-current-state-candidate-model.md`.

Canonical Tactical DDD: `target-tactical-model.md`.

## Purpose

For a batch of technical source/destination address pairs, identify the unordered set of known firewalls that are relevant enough to inspect and expose the local interface resolution and ACL/policy locators required by downstream consumers.

The target query evaluates the current successfully collected NEP state. It does not require a proven end-to-end forwarding path and does not take historical `asOf` input in the MVP.

## Traffic Pair

Application input is:

```text
TrafficPair[]

TrafficPair
    pairId
    sourceAddress
    destinationAddress
```

Each pair is evaluated independently even when many pairs are processed in one set-based request.

## Firewall

`Firewall` is the NEP unit of account. It is one independently addressed/analyzed firewall context with its own routing/interface/policy-binding semantics.

NEP does not model a separate physical Device entity in the MVP.

The Firewall profile contains the information required to select a source adapter and acquire NEP state, including management address, platform type, connection/profile reference, connection timeouts and per-firewall acquisition policy.

Exact Firewall lifecycle commands are deferred.

## Base candidate calculation

For each Firewall and Traffic Pair, NEP resolves source and destination addresses against the Firewall's persisted effective reachability projection.

```text
both resolve
AND sourceInterface != destinationInterface
    => RoutingCandidate = true

otherwise
    => RoutingCandidate = false
```

Missing source/destination resolution is therefore a routing `NotCandidate`, not an error. Override evaluation still runs.

A candidate means only that the Firewall is relevant enough to inspect. It does not prove actual end-to-end traversal and candidate ordering has no route meaning.

## Candidate override rules

NEP owns user-authored rules:

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

Empty match fields mean `ANY`.

A rule matches when every non-empty condition matches. A non-empty interface condition does not match when that interface could not be resolved.

Only Active rules participate.

Decision precedence is:

```text
Include > Exclude > RoutingCandidate
```

Therefore a matching Include rule can include a Firewall even when routing produced `false` or could not resolve one/both addresses.

## Current routing state and reachability index

NEP stores only the latest successfully collected state required by the current MVP. Historical NEP routing snapshots are not retained as domain history.

Routing refresh stores current interfaces/routing facts plus `collectedAt`, derives a persisted effective reachability projection, validates the complete replacement, and atomically switches the current state/projection as one logical version.

The effective projection contains non-overlapping segments after supported routing precedence is resolved:

```text
EffectiveReachabilitySegment
    firewallId
    routingContext?
    addressFamily
    addressFrom
    addressTo
    interfaceRef
```

It is a rebuildable query optimization, not authoritative routing truth.

The intended implementation performs set-based SQL lookup across the global reachability table for all input pairs/firewalls instead of looping through firewall routing tables in backend code.

## Access List Locator

For each selected candidate, NEP returns zero or more policy/ACL locators:

```text
AccessListLocator
    accessListName
    accessListRef?
```

The current domain does not require attachment kind, direction, evaluation position or ingress/global/egress classification. Those are source/vendor adapter mechanics unless a future consumer introduces a concrete need for them.

The adapter is responsible for returning the complete locator set relevant to the pair/firewall under its supported platform semantics.

## Target result

```text
TrafficPairResult
    pairId
    candidates[]

FirewallCandidate
    firewallId
    firewallName
    sourceInterfaceRef?
    destinationInterfaceRef?
    accessLists[]
    decisionReason
```

Candidate output is unordered.

Useful explanation reasons include:

```text
IncludedByRouting
ExcludedByRouting
IncludedByOverride
ExcludedByOverride
```

## Independent source acquisition

NEP and Technical Access Evidence acquire source material independently.

NEP reads only what NEP needs:

```text
interfaces
routing
minimal policy-binding/locator metadata
```

TAE independently reads configured policy/ACL bodies when configured evidence is required, ideally only for selected policy locators.

The two acquisitions may use different schedules, source commands, timeouts and capture identities. A shared transport/client implementation does not merge domain ownership.

## Integration with Technical Access Evidence

NEP returns Firewall + `AccessListLocator` information, not policy contents.

Technical Access Evidence owns captured/imported/configured ACL/policy entries and their provenance. A downstream composition/source adapter uses the Firewall/source correlation plus locator to find or acquire corresponding configured evidence.

## Candidate-set invariants

- candidate output is unordered;
- `candidate != proven traversal`;
- candidate set is not a route;
- absence of a candidate does not prove no end-to-end forwarding path;
- candidate relevance is derived from current routing plus explicit overrides;
- `Include > Exclude > Routing`;
- zero relevant access-list locators is a valid result;
- NEP does not copy or interpret ACL/policy bodies;
- `collectedAt` describes age of current state and is not historical query time.

## Relationship to the implemented I19 path model

The existing I19 `ForwardingPath`/`TraversalPoint` model remains optional stronger/current-runtime capability for a source that can truthfully prove an ordered path.

It is not an MVP prerequisite and must never be synthesized from candidate evidence.

## Ownership boundary

NEP owns:

- Firewall identity/profile required for NEP acquisition;
- current routing/interface knowledge required for candidate selection;
- effective reachability projection;
- candidate override rules;
- candidate relevance calculation;
- source/destination interface resolution;
- relevant ACL/policy locator result.

NEP does not own:

- Resource/application-domain endpoint identity;
- a generic physical-device/CMDB catalogue;
- historical NEP routing snapshots;
- configured ACL/policy contents;
- desired Access Rule state;
- desired-vs-configured reconciliation;
- Add/Remove/Replace/No-op decisions;
- vendor rendering or provider/device execution.
