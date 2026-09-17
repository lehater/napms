# Network Enforcement Placement Core Requirements

Status: `revalidated MVP requirements; G1 accepted for current NEP slice; domain design pending`.

Date: 2026-09-13.

## Purpose

For each technical source/destination pair, identify every known Firewall that is a relevant candidate enforcement location and the distinct ACL/policy names on that Firewall where the pair may be affected.

A candidate is relevance-to-inspect/affect, not proof of end-to-end traversal. NEP answers where traffic may be affected; it does not decide what ACL change is required.

## REQ-NEP-001 — Batch technical address pairs

The application shall accept `TrafficPair[1..N]`:

```text
TrafficPair
    pairId
    sourceAddress
    destinationAddress
```

Each pair produces its own result.

## REQ-NEP-002 — Candidate result contract

For each pair NEP shall return zero or more candidate enforcement locations:

```text
TrafficPairResult
    pairId
    enforcementLocations[0..N]

EnforcementLocation
    firewallId
    accessListNames[0..N]
    metadata
        snapshotCollectedAt?
        decisionSource: Routing | IncludeOverride
```

A candidate Firewall shall remain in the result even when no relevant ACL/policy name can be determined. `accessListNames = []` is therefore a valid result.

Candidate ordering has no route meaning and shall never be promoted to a proven forwarding path.

## REQ-NEP-003 — Firewall catalogue and state

NEP shall maintain the Firewall information needed to identify and acquire from each enforcement device, including a stable `firewallId`, name, management endpoint/platform information and administrative state `Active | Inactive`.

Active Firewalls participate in acquisition and candidate calculation. Inactive Firewalls remain registered but are ignored by both routing and override candidate calculation.

Administrators may change this state directly; no additional domain lifecycle is required by this MVP.

## REQ-NEP-004 — Per-Firewall acquisition configurability

The acquisition behavior needed by NEP shall be independently configurable per Firewall, including polling interval, stale-data threshold and connection/operation timeouts.

This requirement constrains externally configurable behavior but does not prescribe commands, sessions, polling implementation or adapter strategy. Secret material remains external and is referenced opaquely when required.

## REQ-NEP-005 — Latest successful state

NEP shall calculate from the latest successfully acquired network state available for a Firewall. A failed later acquisition shall not invalidate or remove the last successful state.

The MVP does not require historical network-state snapshots as domain history.

## REQ-NEP-006 — Consistent freshness provenance for decision data

NEP shall have the routing/interface facts and ACL/policy binding/name facts necessary to determine candidates and relevant policy names.

When network state contributes to an EnforcementLocation result, the result shall expose one unambiguous `snapshotCollectedAt` freshness value for the network facts used by that result. The system shall not present one freshness date while silently combining decision-critical network facts whose freshness is incompatible with that date.

Configured ACL/policy bodies are not required to perform the current NEP decision.

Requirements do not prescribe how this consistency is achieved. Whether routing/interface facts and ACL binding/name facts are read in one poll, one logical refresh, one session, several commands/APIs or another source-specific mechanism belongs to later design/architecture.

## REQ-NEP-007 — Stale state remains usable

Snapshot age shall not change candidate calculation or ACL/policy selection in MVP.

If the latest successful state exceeds the configured stale threshold, NEP shall diagnose/log `CURRENT_STATE_STALE` and continue calculating normally from that state.

The result metadata shall expose the `snapshotCollectedAt` used for the result so downstream consumers can apply their own freshness policy.

## REQ-NEP-008 — Missing state

When no successful network-state snapshot exists, routing evidence is unavailable and NEP shall diagnose/log `CURRENT_STATE_MISSING`.

Missing state on one Firewall shall not fail calculation for other Firewalls or other Traffic Pairs.

A matching Include override that does not require routing/interface evidence may still make the Firewall a candidate.

## REQ-NEP-009 — Routing evidence

For a Firewall, source and destination shall be resolved using the available routing state. Routing evidence exists when at least one applicable local resolution has different source and destination interfaces.

If source and/or destination cannot be resolved from otherwise available state, routing contributes false and NEP shall diagnose/log `ROUTE_LOOKUP_MISS`. Override evaluation shall still run.

## REQ-NEP-010 — Preserve routing alternatives for decision correctness

When routing contains multiple applicable alternatives, including ECMP/multipath, NEP shall consider every relevant alternative rather than arbitrarily selecting one.

When routing contexts such as VRFs are present, they shall be respected during calculation. Because the current TrafficPair does not select a routing context, every applicable context shall be considered.

These local branches/routing contexts are calculation evidence. They are not required as part of the public result for the current use case.

## REQ-NEP-011 — Candidate overrides

NEP shall support administratively defined candidate override rules:

```text
CandidateOverrideRule
    ruleId
    firewallId
    state: Active | Inactive
    effect: Include | Exclude

    sourceAddressRanges[0..N]
    destinationAddressRanges[0..N]
    sourceInterface?
    destinationInterface?
```

Only Active rules participate. An empty address-range collection means `ANY`; an omitted interface condition means `ANY`.

Within one rule, source ranges are alternatives and destination ranges are alternatives. The rule therefore matches the full mesh of matching source and destination ranges: `ANY(sourceAddressRanges) AND ANY(destinationAddressRanges)`.

Address conditions are evaluated directly against the queried pair. A specified interface condition matches only when routing/interface evidence resolves a corresponding local alternative satisfying that condition. If both interface conditions are specified, one local alternative must satisfy both.

An override with no interface conditions does not require routing/interface resolution merely because those fields are `ANY`.

## REQ-NEP-012 — Override precedence

Candidate precedence shall be:

```text
Include > Exclude > Routing
```

Precedence is applied after determining which override rules actually match.

A matching Include makes the Firewall a candidate regardless of whether routing evidence exists. In particular, an Include rule whose conditions do not require interface evidence may create a candidate even when no network-state snapshot exists.

Otherwise a matching Exclude suppresses the candidate regardless of routing evidence. Otherwise routing evidence determines candidate membership.

## REQ-NEP-013 — Candidate metadata

Every returned EnforcementLocation shall carry metadata describing the result rather than mixing provenance into the core candidate identity.

`decisionSource` shall be `Routing` when routing determined candidate membership and `IncludeOverride` when a matching Include override determined it.

`snapshotCollectedAt` shall contain the freshness date of the network state used for the result. It is `null` when no applicable network snapshot exists, for example when a routing-independent Include override creates a candidate before any successful acquisition.

The age/date of the override rule itself shall not be substituted for network-data freshness.

## REQ-NEP-014 — Return every distinct relevant ACL/policy name

For every candidate Firewall, NEP shall determine all ACL/policy names relevant to the Traffic Pair from every applicable local routing alternative and return their distinct union.

NEP shall not assume parallel/equal-cost alternatives use the same policy.

No ACL/policy name is also a valid result; candidate membership and presence of an ACL are independent facts.

## REQ-NEP-015 — Local traversal details are not required output

Interfaces, local branches, routing contexts, attachment kinds, direction/evaluation position and vendor-specific binding topology may be used internally to determine the correct candidate and ACL/policy-name set.

They are not required as public output by the current MVP use case. A future independently justified use case may expose additional evidence without changing the current meaning of candidate membership.

## REQ-NEP-016 — NEP owns location selection, not policy contents or change intent

NEP shall not require ownership or parsing of configured ACL/policy bodies in order to answer the current use case.

Its responsibility ends with identifying candidate Firewalls and relevant ACL/policy names. It does not decide what rule must be added/removed/changed, perform desired-vs-configured reconciliation, generate configuration or execute changes.

Downstream contexts may use `firewallId + accessListName` and their own evidence to inspect policy contents and decide further action.

## REQ-NEP-017 — Partial availability

A data acquisition failure, missing state or stale state for one Firewall shall not prevent NEP from returning independently determinable results for other Firewalls or Traffic Pairs.

Operational acquisition failures and state diagnostics belong to NEP observability and do not need to be copied into every EnforcementLocation metadata object merely to report a successful candidate result.

## Acceptance examples

1. Ten Traffic Pairs are evaluated and each receives its own unordered candidate list.
2. A Firewall resolves source to `inside` and destination to `outside`; it is a routing candidate.
3. Both addresses resolve only to the same interface; absent overrides, the Firewall is not a routing candidate.
4. Destination lookup misses; routing contributes false, but a matching Include rule without interface constraints still includes the Firewall.
5. A Firewall has never been successfully acquired; routing cannot include it and `CURRENT_STATE_MISSING` is diagnosed, but a routing-independent Include may still return it with `accessListNames=[]` and `snapshotCollectedAt=null`.
6. Include and Exclude both match; Include wins.
7. A rule with source ranges `{S1,S2}` and destination ranges `{D1,D2,D3}` matches all six source/destination range combinations.
8. An Include constrained to `sourceInterface=inside` does not match when interface evidence is unavailable; an otherwise identical Include with no interface constraint may match.
9. ECMP alternatives `inside -> wan1` and `inside -> wan2` are both considered. If they use `ACL-A` and `ACL-B`, both names are returned; if both use `ACL-A`, it is returned once.
10. A candidate Firewall with no relevant ACL/policy binding is still returned with `accessListNames=[]`.
11. Two VRFs resolve the same destination differently; both are considered because TrafficPair does not select a VRF.
12. A week-old latest successful snapshot is still used normally; `CURRENT_STATE_STALE` is diagnosed and its freshness date is returned in metadata.
13. A new acquisition fails but an older successful snapshot exists; NEP continues calculating from the older snapshot.
14. One Firewall has no usable routing state; calculation for other Firewalls and other pairs still completes.
15. Different Firewalls may have different polling, staleness and timeout settings without Requirements prescribing how acquisition is implemented.
16. NEP can answer its candidate/policy-name use case without acquiring ACL/policy bodies.
17. Network facts used in one result do not claim a single `snapshotCollectedAt` unless that date truthfully represents their freshness; the mechanism that guarantees this consistency is left to later design.

## G1 result

For the current NEP slice, the observable requirements above are coherent enough for Domain Design without selecting acquisition coordination, persistence, adapter/session, database, API implementation or internal local-branch representation mechanisms.

`G1 PASS` — proceed to S2 Domain Design when work resumes.
