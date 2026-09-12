# Network Enforcement Placement Core Requirements

Status: `accepted MVP target by ADR-018; implementation migration pending`.

Date: 2026-09-13.

Decision: `../decisions/ADR-018-nep-firewall-current-state-candidate-model.md`.

Canonical model: `../domain/network-enforcement-placement/target-tactical-model.md`.

## Purpose

For each technical source/destination pair, identify the unordered set of known Firewalls that may be relevant, preserve every firewall-local routing branch that may carry the traffic, and expose the distinct ACL/policy names that must be inspected downstream.

A candidate is relevance-to-inspect, not proof of end-to-end traversal.

## REQ-NEP-001 — Batch technical address pairs

The application shall accept `TrafficPair[1..N]`:

```text
TrafficPair
    pairId
    sourceAddress
    destinationAddress
```

Each pair produces its own result. MVP evaluation uses current NEP state and does not require `asOf`.

## REQ-NEP-002 — Firewall is the unit of account

NEP shall own a catalogue of:

```text
Firewall
    firewallId
    name
    managementAddress
    platformType
    state: Active | Inactive
```

No separate physical Device/chassis entity is required for MVP.

`Active` Firewalls participate in polling and candidate calculation. `Inactive` Firewalls remain configured but are ignored. Administrators may change this state directly through the Web UI; no separate domain lifecycle command model is required.

## REQ-NEP-003 — Per-Firewall connection and acquisition settings

The Firewall profile shall support the minimal independently configurable settings needed by current acquisition use cases:

```text
ConnectionSettings
    connectTimeout
    operationTimeout

AcquisitionPolicy
    routingPollInterval?
    policyBindingPollInterval?
```

Different Firewalls may use materially different values. Secret material shall remain external and be referenced opaquely.

Retry/backoff/error-policy design is not required by this MVP model.

## REQ-NEP-004 — Keep only current routing/interface state

NEP shall retain only the latest successfully collected state required for candidate analysis. Historical NEP routing/configuration snapshots are not MVP domain history.

Current state shall retain `collectedAt`.

## REQ-NEP-005 — Replace routing state atomically

A routing refresh shall build and validate a complete replacement before publishing it. Current routing/interface facts and all effective reachability projections derived from them shall switch as one logical version.

The superseded version may be discarded after successful switching.

## REQ-NEP-006 — Persist routing-context-aware effective reachability

NEP shall derive a persisted query projection from current routing facts after normal prefix precedence is resolved.

Conceptual shape:

```text
EffectiveReachabilitySegment
    firewallId
    routingContextRef?
    addressFamily
    addressFrom
    addressTo
    interfaces[1..N]
```

Within one Firewall + routing context + address family, effective address segments shall not overlap.

A segment may resolve to more than one interface for ECMP/multipath. Implementations may normalize the interface set into child rows.

The projection is rebuildable and is not authoritative routing truth.

## REQ-NEP-007 — Preserve VRF/routing context

When source routing data contains routing contexts such as VRFs, NEP shall preserve the context reference in current routing facts and effective reachability.

The current `TrafficPair` contract has no routing-context selector. Therefore NEP shall evaluate all applicable routing contexts unless a future stronger input contract supplies one.

## REQ-NEP-008 — Preserve all multipath local branches

For each Firewall, Traffic Pair and routing context, resolve source and destination to sets of effective interfaces and evaluate the local combinations:

```text
localBranches = sourceInterfaces × destinationInterfaces
```

A branch is routing-relevant when:

```text
sourceInterface != destinationInterface
```

The Firewall is a routing candidate when at least one routing-relevant branch exists.

NEP shall not arbitrarily select one ECMP/equal-cost interface. Every routing-relevant branch shall remain available for ACL/policy-locator resolution.

## REQ-NEP-009 — Route lookup miss does not block overrides

If source and/or destination does not resolve in an otherwise available current routing state, routing contributes `false` for that Firewall/pair and the condition shall be diagnosed/logged.

Override evaluation shall still run.

No separate public/domain `NetworkResolution` lifecycle object is required.

## REQ-NEP-010 — Missing current routing state is diagnosed and skipped

If an Active Firewall has no current routing state, MVP candidate calculation shall not add it to the candidate set merely because the state is unknown.

The condition shall be diagnosed/logged, e.g. `CURRENT_ROUTING_STATE_MISSING`.

## REQ-NEP-011 — Candidate overrides

NEP shall own:

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

Address conditions match the queried pair directly. Interface conditions shall match only when there exists a resolved local branch in one routing context satisfying all specified interface conditions.

## REQ-NEP-012 — Override precedence

Candidate precedence shall be:

```text
Include > Exclude > Routing
```

A matching Include wins over matching Exclude and routing result. Otherwise matching Exclude wins. Otherwise the routing result is used.

A matching Include may override a route lookup miss inside a valid current state. It does not manufacture current routing state when none exists.

## REQ-NEP-013 — Candidate output is unordered and not a route

Candidate membership means relevant enough to inspect. Candidate ordering has no route meaning and shall never be promoted to a proven forwarding path.

## REQ-NEP-014 — Expose local branches needed for policy selection

For a routing-derived candidate, NEP shall preserve every routing-relevant local branch used for policy selection:

```text
LocalBranch
    routingContextRef?
    sourceInterfaceRef
    destinationInterfaceRef
```

These are firewall-local resolution facts, not proof of global traversal.

An Include override may create a candidate without resolved local branches when its matching conditions do not require them.

## REQ-NEP-015 — Return every distinct relevant ACL/policy name

For each candidate, the supported Firewall adapter shall evaluate every relevant local branch and return the distinct union of ACL/policy names required by those branches:

```text
AccessListLocator
    accessListName
```

NEP shall not assume that equal-cost/parallel branches use the same ACL even when that is common in practice.

A stable `accessListRef` is not part of the MVP contract until a concrete source/consumer requires it.

## REQ-NEP-016 — Keep attachment topology outside the core

MVP does not require `attachmentKind`, `direction`, `evaluationPosition`, ingress/global/egress classification or a universal interface-binding topology.

Vendor adapters may use such details internally to determine the correct access-list-name set.

## REQ-NEP-017 — NEP owns policy selection, not policy contents

NEP shall not copy, parse or own configured ACL/policy bodies or entries.

Technical Access Evidence remains the owner of configured policy contents/evidence. Downstream composition may use `firewallId + accessListName` plus source-specific adapter correlation to locate/acquire those contents.

## REQ-NEP-018 — Acquire NEP and TAE source data independently

Refreshing NEP routing state shall not require collecting complete ACL/policy bodies.

NEP acquisition reads only the slices it needs, including interfaces, routing, and minimal policy-binding/locator metadata. TAE acquires ACL/policy bodies independently and should use targeted reads when supported by the source.

The two acquisitions may differ in schedule, trigger, timeout, source command/API and capture identity.

## REQ-NEP-019 — Set-based candidate evaluation

The target implementation shall support set-based database evaluation over the shared effective reachability projection for all requested pairs/firewalls.

It shall not require a backend loop that independently walks every Firewall routing table for every pair.

## REQ-NEP-020 — Current-state diagnostics

At minimum the implementation shall make these operational conditions observable in logs/diagnostics:

```text
CURRENT_ROUTING_STATE_MISSING
ROUTE_LOOKUP_MISS
```

Diagnostics do not introduce a new domain state machine in MVP.

## REQ-NEP-021 — Context boundaries

A Firewall is not automatically a Resource Catalogue `Resource`. NEP is not a generic CMDB.

The existing stronger I19 `ForwardingPath` capability may remain during migration or for future proven-path sources, but MVP consumers shall not require it.

NEP shall not perform desired-vs-configured reconciliation, configuration generation or execution.

## Acceptance examples

1. Ten pairs are evaluated set-wise and each receives its own unordered candidate list.
2. A Firewall resolves source to `inside` and destination to `outside`; it is a routing candidate.
3. Both addresses resolve only to the same interface; absent overrides, it is not a routing candidate.
4. Destination route lookup misses, so routing contributes false; a wildcard-interface Include override still includes the Firewall.
5. An Active Firewall has never been successfully polled; it is skipped and `CURRENT_ROUTING_STATE_MISSING` is logged.
6. Include and Exclude both match; Include wins.
7. An all-wildcard Active Include rule applies to every pair for its Firewall when current routing state exists.
8. A route segment has ECMP interfaces `wan1` and `wan2`; both branches are preserved rather than choosing one.
9. Branch `inside -> wan1` uses `ACL-A`, while `inside -> wan2` uses `ACL-B`; result contains both ACL names.
10. Both ECMP branches use `ACL-A`; result contains `ACL-A` once after deduplication.
11. Two VRFs resolve the same destination differently; both routing-context branches are evaluated because the input pair does not select a VRF.
12. Routing refresh atomically replaces old state and its reachability projection; no historical NEP snapshot remains.
13. A static-routing Firewall is refreshed infrequently while a dynamic-routing Firewall uses a short routing interval.
14. A high-latency Firewall uses larger connection/operation timeouts.
15. NEP routing refresh does not fetch ACL bodies; TAE obtains selected ACL contents separately.
