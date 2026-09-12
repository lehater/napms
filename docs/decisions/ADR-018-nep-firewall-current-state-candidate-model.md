# ADR-018 — NEP Firewall Current-State Candidate Model

Status: `accepted target decision; implementation migration pending`.

Date: 2026-09-13.

Supersedes the MVP target portions of `ADR-017-nep-candidate-policy-attachment-contract.md` where this decision is more specific.

## Context

ADR-017 established the important separation between an unordered candidate set and a proven forwarding path. Subsequent Tactical DDD review clarified the actual source semantics and the minimum information required by current consumers.

The MVP evaluates batches of technical source/destination address pairs against a catalogue of firewalls. Candidate relevance is derived from each firewall's current local routing knowledge and may be overridden by user-authored rules.

The system is not trying to select one optimal route. Its purpose is to find every firewall-local path variant that may carry the traffic so that every relevant ACL/policy can be inspected or changed downstream. Therefore equal-cost/multipath routing must be preserved rather than collapsed to one arbitrarily chosen interface.

Collecting an entire firewall configuration is unnecessarily expensive. NEP and Technical Access Evidence therefore acquire source data independently and only to the depth required by their own semantics.

## Decision

### 1. `Firewall` is the NEP unit of account

NEP owns a catalogue of `Firewall` identities. `Firewall` means one independently addressed and analysed firewall context with its own routing/interface/policy-binding semantics. No separate physical `Device` entity is required for MVP.

Minimum profile:

```text
Firewall
    firewallId
    name
    managementAddress
    platformType
    state: Active | Inactive
    credentialRef / connectionProfileRef
    connectionSettings
    acquisitionPolicy
```

`Active` firewalls participate in polling and candidate calculation. `Inactive` firewalls remain configured but are ignored by both. The state is directly administered through the Web UI; no separate domain lifecycle/command model is required for MVP.

The profile may carry per-firewall connection settings such as connect/operation timeouts and independent acquisition intervals. Secret material is not domain state; only an opaque credential/profile reference is retained.

### 2. Input is a batch of address pairs; no MVP `asOf`

```text
TrafficPair
    pairId
    sourceAddress
    destinationAddress
```

The application accepts `TrafficPair[1..N]`. Each pair produces its own result. The MVP query evaluates the current successfully collected NEP state and does not take `asOf`.

### 3. Current routing state is replaceable current state, not history

NEP keeps only the latest successfully collected routing/interface state needed for candidate analysis. Historical NEP network snapshots are not part of the MVP domain model.

A refresh builds and validates a complete replacement before publishing it. Current routing/interface state and every reachability projection derived from it switch atomically as one logical version. The previous version may then be discarded.

`collectedAt` is retained as current-state freshness metadata.

### 4. Persist an effective reachability projection for set-based SQL evaluation

Raw routes may overlap and may produce more than one equally valid interface. NEP derives a persisted read model that resolves prefix precedence but preserves multipath results.

Conceptual shape:

```text
EffectiveReachabilitySegment
    firewallId
    routingContextRef?       # e.g. VRF when present
    addressFamily
    addressFrom
    addressTo
    interfaces[1..N]
```

A relational implementation may normalize `interfaces[1..N]` into child rows rather than an array.

Within one firewall + routing context + address family, address segments do not overlap. One effective segment may reference multiple interfaces when ECMP/multipath makes them equally valid.

The projection is replaceable and rebuildable; it is not authoritative routing truth. Candidate calculation should use set-based PostgreSQL operations over this projection rather than per-firewall backend loops.

### 5. Routing contexts such as VRF are preserved, not guessed away

When a firewall exposes multiple routing contexts/VRFs, route facts and effective reachability retain the routing-context reference.

The current `TrafficPair` contract does not carry a routing-context selector. Therefore, unless a future caller supplies stronger context, NEP evaluates all applicable routing contexts and keeps all resulting local path variants. This may conservatively over-include candidates, which is acceptable for the placement use case.

### 6. Base candidate relevance preserves every local path variant

For each firewall/pair/routing-context, NEP resolves source and destination addresses to sets of effective interfaces.

Conceptually:

```text
sourceInterfaces = resolve(sourceAddress)
destinationInterfaces = resolve(destinationAddress)

localBranches = sourceInterfaces × destinationInterfaces
```

A local branch is routing-relevant when its source and destination interfaces differ:

```text
sourceInterface != destinationInterface
    => branch is routing-relevant
```

The firewall is a routing candidate when at least one routing-relevant branch exists.

NEP must not arbitrarily choose one ECMP/multipath interface. Every relevant branch is retained for ACL/policy-locator resolution, and the final ACL names are the distinct union across all relevant branches.

If source and/or destination does not resolve in an otherwise valid current routing state, routing contributes `false`; override evaluation still runs. This lookup miss is logged/diagnosed but is not a separate business entity or public lifecycle state.

If an Active firewall has no current routing state at all, MVP candidate calculation skips that firewall and records a diagnostic. It is not added as a candidate merely because its routing state is unknown.

### 7. Candidate override rules are NEP-owned entities

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

An empty match field means `ANY`. Only Active rules participate.

Address conditions are evaluated directly against the queried pair. Interface conditions match when there exists a resolved local branch in one routing context satisfying all specified interface conditions. If a specified interface cannot be resolved, that condition does not match.

Conflict precedence is:

```text
Include > Exclude > RoutingCandidate
```

A matching Include therefore overrides routing `false`, including a route-lookup miss inside an otherwise valid current state. A missing current routing state is different: that firewall is skipped and diagnosed for MVP.

### 8. NEP needs ACL/policy names, not attachment topology

For a selected firewall candidate, the current use case needs the names of every ACL/policy object that may apply on any relevant local branch.

MVP locator:

```text
AccessListLocator
    accessListName
```

No stable `accessListRef` is required until a concrete source or consumer demonstrates that the name is insufficient.

The core domain does not require `attachmentKind`, `direction`, `evaluationPosition`, ingress/global/egress classification or universal interface attachment topology. Those remain vendor-adapter knowledge.

The adapter evaluates every relevant local branch and returns the distinct union of applicable access-list names. NEP must not assume that parallel paths use the same ACL even when that is common operationally.

### 9. NEP and TAE acquire source data independently

NEP reads only what it needs:

```text
interfaces
routing
minimal policy-binding/locator metadata
```

TAE independently acquires configured ACL/policy bodies when those contents are needed, ideally only for selected access-list names where the source permits targeted reads.

The acquisitions may differ in time, frequency, trigger, timeout, source command/API and capture identity. Shared transport/client code is allowed but does not merge bounded-context ownership.

### 10. Acquisition settings are per Firewall and intentionally minimal

Minimum profile settings currently required are:

```text
ConnectionSettings
    connectTimeout
    operationTimeout

AcquisitionPolicy
    routingPollInterval?
    policyBindingPollInterval?
```

This allows static-routing firewalls to be refreshed rarely and dynamic-routing/high-volatility firewalls more frequently, while high-latency links can use larger timeouts.

Retry/backoff/error-policy design is deferred to implementation when needed.

## Target query shape

```text
AnalyzeTrafficPairs(TrafficPair[])
    -> TrafficPairResult[]

TrafficPairResult
    pairId
    candidates[]              # unordered

FirewallCandidate
    firewallId
    firewallName
    localBranches[]           # all relevant local interface variants
    accessLists[]             # distinct union across branches
    decisionReason

LocalBranch
    routingContextRef?
    sourceInterfaceRef
    destinationInterfaceRef

AccessListLocator
    accessListName
```

Candidate membership means relevance-to-inspect, not proof of end-to-end traversal. Candidate order has no route meaning.

## Diagnostics

The MVP does not introduce a new domain state machine for missing network knowledge. Operationally important misses are logged/diagnosed, at minimum:

```text
CURRENT_ROUTING_STATE_MISSING
ROUTE_LOOKUP_MISS
```

A route lookup miss in a valid current state still allows override evaluation. A missing current routing state causes the firewall to be skipped for MVP candidate calculation.

## Ownership boundary

NEP owns:

- Firewall identity/profile and Active/Inactive state;
- current NEP-relevant routing/interface state;
- routing-context-aware effective reachability projection;
- multipath-preserving local branch derivation;
- candidate override rules and precedence;
- candidate relevance calculation;
- relevant access-list-name selection for every retained local branch.

NEP does not own:

- Resource Catalogue Resource identity;
- generic infrastructure/CMDB identity;
- physical chassis identity as a separate MVP concept;
- configured ACL/policy bodies or entries;
- desired Access Rule semantics;
- reconciliation;
- vendor rendering/execution;
- historical NEP routing snapshots.

Technical Access Evidence remains the owner of configured policy contents/evidence.

## Consequences

- the target model remains conservative toward inclusion;
- ECMP/multipath is not treated as an error and no single winner is invented;
- VRF/routing-context identity can be carried without making route selection a NEP responsibility;
- ACL resolution covers every retained local branch and deduplicates names only after branch evaluation;
- missing current state is observable through diagnostics rather than silently interpreted as `NotCandidate`;
- expensive ACL bodies are never required merely to refresh NEP routing state;
- the model stays minimal: no physical Device entity, no historical snapshots, no ACL attachment taxonomy, no premature stable ACL reference, and no separate Firewall lifecycle command model.

## Deferred implementation details

The following do not block the target domain model:

- concrete secret/profile storage mechanism;
- retry/backoff and scheduler failure policy;
- vendor-specific PBR or other routing semantics not yet required by supported adapters;
- implementation migration from current I19/I26 persistence/code.
