# Network Enforcement Placement Core Requirements

Status: `accepted MVP target by ADR-018; implementation migration pending`.

Date: 2026-09-13.

Decision: `../decisions/ADR-018-nep-firewall-current-state-candidate-model.md`.

Canonical model: `../domain/network-enforcement-placement/target-tactical-model.md`.

## Purpose

Specify observable MVP behavior for Network Enforcement Placement (NEP): process a batch of technical source/destination address pairs against the current known firewall state, derive an unordered firewall candidate set from local routing plus explicit overrides, and expose the ACL/policy locators required by downstream configured-evidence consumers.

A candidate is relevance-to-inspect, not proof of end-to-end traversal.

## REQ-NEP-001 — Evaluate a batch of technical address pairs

The application input shall support one or more independent pairs:

```text
TrafficPair
    pairId
    sourceAddress
    destinationAddress
```

Each pair shall produce its own result. Batch evaluation exists for efficient set-based processing and does not merge the semantics of different pairs.

The MVP query shall evaluate current successfully collected NEP state and shall not require an `asOf` input.

## REQ-NEP-002 — Firewall is the NEP unit of account

NEP shall own a catalogue of `Firewall` identities sufficient for acquisition and candidate analysis.

The MVP shall not require a separate physical Device/chassis domain entity.

A Firewall profile shall contain at least the stable firewall identity, human-readable name, management address and source/platform information needed to select the appropriate adapter.

Connection/polling profile data may be stored with the Firewall as value semantics. Secret material shall remain external and be referenced opaquely.

Exact Firewall lifecycle commands are deferred from this requirement set.

## REQ-NEP-003 — Support per-Firewall acquisition settings

A Firewall may require source-specific connection and acquisition settings, including at least:

- connection establishment timeout;
- operation timeout;
- routing refresh interval;
- separately configurable policy-binding/locator refresh interval when that source slice is collected independently.

The design shall permit different Firewalls to use materially different intervals/timeouts.

A missing scheduled interval may represent on-demand acquisition only.

## REQ-NEP-004 — Keep only current NEP network state

NEP shall retain only the latest successfully collected state required for MVP candidate analysis.

Historical routing/configuration snapshots are not NEP domain history in the MVP.

Current-state metadata shall preserve `collectedAt` so the age of the data is observable.

## REQ-NEP-005 — Replace current state atomically

A refresh shall build and validate a complete replacement before making it visible.

Current routing/interface state and the effective reachability projection derived from it shall switch as one logical version. Consumers shall not observe a mixture of old/new routing data from one refresh.

The superseded version may be discarded after successful switching.

## REQ-NEP-006 — Derive a persisted effective reachability index

NEP shall derive a persisted query projection from the current routing state in which supported routing overlaps/precedence have already been resolved:

```text
EffectiveReachabilitySegment
    firewallId
    routingContext?
    addressFamily
    addressFrom
    addressTo
    interfaceRef
```

Within one Firewall/routing-context/address-family projection, effective segments shall not overlap.

The projection shall be rebuildable and shall not become authoritative routing truth.

Unsupported/ambiguous routing semantics shall not be resolved by arbitrary representation order.

## REQ-NEP-007 — Calculate routing candidates from local interface resolution

For each Firewall and Traffic Pair, NEP shall resolve source and destination addresses against the current effective reachability projection.

Base routing semantics are:

```text
both addresses resolve
AND sourceInterface != destinationInterface
    => RoutingCandidate = true

otherwise
    => RoutingCandidate = false
```

An unresolved source or destination is an ordinary routing `NotCandidate` result and shall not be treated as an analysis failure.

## REQ-NEP-008 — Evaluate candidate selection set-wise

The intended target implementation shall support set-based database evaluation over the global effective reachability projection for all requested pairs/firewalls.

The design shall not require a backend/Python loop that independently walks every Firewall routing table for every pair.

This is an implementation-shape requirement for scalability and does not change the domain result.

## REQ-NEP-009 — Support user-authored candidate override rules

NEP shall own `CandidateOverrideRule` entities targeted at a Firewall.

MVP rule shape:

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

An empty match field shall mean `ANY`.

Only Active rules shall participate in calculation.

## REQ-NEP-010 — Match all non-empty override conditions

An override rule shall match only when every non-empty condition matches the evaluated pair/local interface resolution.

If an interface condition is non-empty but the corresponding interface was not resolved, that interface condition shall not match.

An override with no interface conditions may therefore still match when routing could not resolve source and/or destination.

## REQ-NEP-011 — Apply deterministic override precedence

Candidate precedence shall be:

```text
Include > Exclude > RoutingCandidate
```

If at least one matching Include rule exists, the Firewall shall be a candidate regardless of RoutingCandidate or matching Exclude rules.

Otherwise, if at least one matching Exclude rule exists, the Firewall shall not be a candidate.

Otherwise, the final result shall equal RoutingCandidate.

## REQ-NEP-012 — Candidate set is unordered and does not prove traversal

For each pair, NEP shall return zero or more `FirewallCandidate` values.

Candidate semantics:

- candidate means relevant enough to inspect;
- candidate order has no route meaning;
- candidate membership does not prove end-to-end traversal;
- a missing candidate does not by itself prove there is no end-to-end path;
- the candidate set shall never be promoted to a proven route merely by representation order.

## REQ-NEP-013 — Expose local interface resolution

A candidate result shall expose the source and destination interface references resolved from the current Firewall state when available:

```text
sourceInterfaceRef?
destinationInterfaceRef?
```

They are local Firewall interpretation used for candidate/policy-locator resolution, not an assertion of global traversal order.

An Include override may create a candidate even when one or both interfaces are unresolved.

## REQ-NEP-014 — Expose relevant ACL/policy locators only

For each candidate, NEP shall expose zero or more locators for ACL/policy objects that the supported Firewall adapter determines are relevant for the pair:

```text
AccessListLocator
    accessListName
    accessListRef?
```

At least one usable source-supported locator shall be present for each returned list.

A candidate with zero relevant locators is valid and shall not be silently dropped.

## REQ-NEP-015 — Keep vendor attachment topology outside the core unless required

The MVP domain shall not require `attachmentKind`, `direction`, `evaluationPosition`, ingress/global/egress classification or a universal interface-binding topology.

Vendor/source-specific logic may use those facts internally to determine the correct locator set, but the domain output shall expose only the locators required by current consumers.

A future consumer requirement may extend this contract explicitly.

## REQ-NEP-016 — NEP owns policy location/selection, not policy contents

NEP shall not copy, parse or own configured ACL/policy entries.

Technical Access Evidence remains the owner of captured/imported/configured policy bodies, normalized predicates/actions and their provenance.

Downstream composition/source acquisition may correlate configured evidence using Firewall/source identity plus `AccessListLocator`.

## REQ-NEP-017 — Acquire NEP and TAE source data independently

Refreshing NEP routing state shall not require collecting complete ACL/policy bodies.

NEP acquisition shall read only the source slices it needs, such as:

- interfaces;
- routing;
- minimal policy-binding/locator metadata required to resolve relevant ACL/policy names.

TAE shall acquire configured ACL/policy bodies independently when those contents are needed, ideally only for the selected policy locators where the vendor/source permits targeted reads.

The two acquisitions may differ in schedule, trigger, timeout, source command/API and capture identity.

## REQ-NEP-018 — Preserve current-state collection metadata

Current NEP state shall preserve at least `collectedAt` for freshness/explainability.

`collectedAt` shall not be presented as historical query time or as an automatic proof that state is fresh enough for every consumer.

Any stricter freshness contract belongs to a concrete consumer/source requirement.

## REQ-NEP-019 — Keep Resource Catalogue identity independent

A Firewall shall not automatically become a Resource Catalogue `Resource` merely because it is infrastructure.

NEP Firewall identity and Resource Catalogue Resource identity remain independent unless a future explicit cross-context correspondence use case requires a relation.

NEP shall not become a generic infrastructure/CMDB catalogue.

## REQ-NEP-020 — Keep stronger proven-path capability optional

The existing I19 `ForwardingPath` / ordered `TraversalPoint` capability may remain available during migration or for future sources that can truthfully prove it.

MVP candidate consumers shall not require it and NEP shall never infer a proven path from candidate membership.

## REQ-NEP-021 — Do not perform reconciliation or configuration generation

NEP shall not:

- decide whether configured policy satisfies desired policy;
- produce Add/Remove/Replace/No-op;
- render vendor configuration;
- execute provider/device changes.

Those are downstream concerns.

## Acceptance examples

1. One request containing 10 source/destination pairs is evaluated set-wise and returns an independent unordered candidate list for every pair.
2. Firewall A resolves source to interface `inside` and destination to `outside`; absent overrides it is a candidate.
3. Firewall B resolves both addresses to the same interface; absent overrides it is not a candidate.
4. Firewall C cannot resolve the destination, so routing says NotCandidate; a matching Include rule with wildcard interfaces still makes it a candidate.
5. A matching Include and Exclude rule both apply; Include wins.
6. A rule with `sourceInterfaceRef=inside` does not match when source interface resolution is absent.
7. An override rule with all optional match fields empty applies to every pair for its Firewall while Active.
8. Routing prefixes overlap in the source routing state; the effective reachability projection contains non-overlapping winning address segments.
9. A routing refresh atomically replaces the old current routing state and its reachability projection; no historical NEP snapshot is retained after successful replacement.
10. One Firewall configured with static routing is refreshed infrequently while another with dynamic routing has a short routing interval.
11. A Firewall with high-latency connectivity uses a larger connection timeout than other Firewalls.
12. Candidate analysis returns `ACL-IN`, `GLOBAL-POLICY` and `ACL-OUT` as three opaque access-list locators without exposing why/how each is attached.
13. TAE subsequently fetches/records the bodies of only the selected ACLs; NEP routing refresh did not fetch those bodies.
14. A candidate with no applicable ACL/policy locator remains a candidate with an empty locator list.
15. Candidate result ordering is never interpreted as a forwarding route.
