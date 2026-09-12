# ADR-018 — NEP Firewall Current-State Candidate Model

Status: `accepted target decision; implementation migration pending`.

Date: 2026-09-13.

Supersedes the MVP target portions of `ADR-017-nep-candidate-policy-attachment-contract.md` where this decision is more specific.

## Context

ADR-017 established the important separation between an unordered candidate set and a proven forwarding path. Subsequent Tactical DDD review clarified the actual source semantics and the minimum information required by current consumers.

The MVP does not operate on a known end-to-end forwarding path. It evaluates a batch of technical source/destination address pairs against a catalogue of firewalls. Candidate relevance is derived from each firewall's current local routing knowledge and may then be overridden by user-authored rules.

Inside one candidate firewall, source/destination interface resolution and the relevant ACL/policy locators are deterministic with respect to the currently collected firewall state. The uncertainty is in whether the firewall belongs in the candidate set, not in the meaning of the collected local state.

The review also established that collecting an entire device configuration is unnecessarily expensive. Network Enforcement Placement and Technical Access Evidence therefore acquire their source data independently and only to the depth required by their own semantics.

## Decision

### 1. `Firewall` is the NEP unit of account

NEP owns a catalogue of `Firewall` identities.

`Firewall` means one independently addressed and analysed firewall context with its own routing/interface/policy-binding semantics. NEP does not introduce a separate physical `Device` entity for the MVP.

Minimum profile information is:

```text
Firewall
    firewallId
    name
    managementAddress
    platformType
    credentialRef / connectionProfileRef
    connectionSettings
    acquisitionPolicy
```

Exact lifecycle commands for `Firewall` are deliberately deferred to a separate review.

The profile may carry per-firewall connection settings such as connect/operation timeouts and per-source acquisition intervals. This allows a static-routing firewall to be polled rarely while a firewall with dynamic routing can be refreshed more frequently.

Secret material is not domain state; the firewall profile stores only an opaque reference to connection credentials/profile data.

### 2. Input is a batch of address pairs; no MVP `asOf`

The application input is one or more independent technical pairs:

```text
TrafficPair
    pairId
    sourceAddress
    destinationAddress
```

Batching is first-class at the application/query level for set-based evaluation. Each pair still produces an independent result.

The MVP query evaluates against the current successfully collected NEP state. `asOf` is not part of `TrafficPair` or the target query contract.

### 3. Base candidate relevance comes from local routing

For each firewall and traffic pair, NEP resolves the source and destination addresses against the firewall's effective local routing projection.

Base semantics:

```text
both addresses resolve
AND sourceInterface != destinationInterface
    => RoutingCandidate = true

otherwise
    => RoutingCandidate = false
```

An unresolved source or destination therefore yields `RoutingCandidate = false`; it is not an error and does not block override evaluation.

Candidate membership means only that the firewall is relevant enough to inspect. It does not prove end-to-end traffic traversal and candidate order has no route meaning.

### 4. Candidate override rules are NEP-owned entities

NEP owns user-authored `CandidateOverrideRule` entities targeted at one `Firewall`.

MVP shape:

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

An empty match field means `ANY`.

A rule matches only when every non-empty condition matches. If an interface condition is present but the corresponding interface could not be resolved, that interface condition does not match.

Only Active rules participate.

Conflict precedence is:

```text
Include > Exclude > RoutingCandidate
```

Therefore a matching Include rule always makes the firewall a candidate, including when local routing produced `false` or could not resolve one/both addresses. A matching Exclude rule removes the firewall only when no Include rule matched.

### 5. Current routing state is replaceable current state, not history

NEP keeps only the latest successfully collected state required for candidate analysis. Historical NEP network snapshots are not part of the MVP domain model.

At minimum the routing acquisition slice contains current interfaces and routing facts plus collection metadata such as `collectedAt`.

A refresh builds and validates a complete replacement before making it visible. The current state and all projections derived from it switch atomically as one logical version. The previous version may then be discarded.

### 6. Persist an effective reachability projection for set-based SQL evaluation

Candidate calculation shall not repeatedly walk overlapping routing tables in backend loops.

From the current routing state NEP derives a persisted `EffectiveReachabilitySegment` read model:

```text
EffectiveReachabilitySegment
    firewallId
    routingContext?        # only where required by the supported source
    addressFamily
    addressFrom
    addressTo
    interfaceRef
```

Within one firewall/routing-context/address-family projection, effective segments represent routing precedence after overlaps have been resolved and do not overlap each other.

This projection is replaceable and rebuildable. It is not authoritative routing truth.

A batch query joins all input traffic pairs against the shared reachability table to resolve source/destination interfaces for all firewalls set-wise and produce the base candidate set without a per-firewall Python/backend loop.

The routing normalization must not silently choose a winner when the source semantics cannot truthfully resolve competing routes. Exact handling of unsupported multipath/routing dimensions remains an adapter/normalization concern to be specified when required.

### 7. NEP needs only ACL/policy locators, not attachment topology

For a selected firewall candidate, current consumers need the list of ACL/policy objects to inspect downstream.

The domain result is therefore reduced to source-supported locators:

```text
AccessListLocator
    accessListName
    accessListRef?
```

The NEP domain does not require `attachmentKind`, `direction`, `evaluationPosition`, ingress/global/egress classification or interface attachment topology for the current MVP use cases.

Vendor-specific knowledge about how a policy is attached and how the relevant policy list is determined belongs behind the firewall source adapter. The adapter returns the complete locator set required for the pair/firewall according to the supported platform semantics.

A firewall candidate may legitimately return zero relevant access-list locators.

### 8. NEP and TAE acquire source data independently

NEP must not require collection of a full firewall configuration merely because configured ACL/policy contents may exist on the same source.

NEP acquisition reads only data required by NEP, such as:

```text
interfaces
routing
minimal policy-binding/locator metadata required to resolve relevant ACL/policy names
```

Technical Access Evidence independently acquires configured ACL/policy bodies when those contents are required. Ideally it can request only selected policies identified by NEP locators; a vendor adapter may internally use a broader source operation only when the platform forces it.

A shared source transport/client may be reused by adapters, but shared transport mechanics do not create shared domain ownership.

There is no requirement that NEP routing acquisition and TAE policy-body acquisition happen in the same poll, at the same time, or share one capture identifier.

### 9. Current-state acquisition can have per-firewall policy

The `Firewall` profile may configure acquisition characteristics per source slice, including at least routing refresh frequency and, when separately collected, policy-binding metadata refresh frequency.

A missing/disabled scheduled interval may mean on-demand acquisition only. Exact scheduling commands and failure/retry policy are application/infrastructure concerns and are deferred from this ADR.

`collectedAt` is preserved on current state so consumers can assess the age of the data. It is collection metadata, not historical query time and not a replacement for a future explicit freshness contract.

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
    sourceInterfaceRef?
    destinationInterfaceRef?
    accessLists[]
    decisionReason

AccessListLocator
    accessListName
    accessListRef?
```

Candidate decision reasons may distinguish routing-derived inclusion/exclusion from override-derived inclusion/exclusion for explainability.

## Ownership boundary

NEP owns:

- Firewall identity and the firewall acquisition profile required by NEP;
- current NEP-relevant routing/interface state;
- the effective reachability projection;
- candidate override rules and their precedence;
- candidate relevance calculation;
- source/destination interface resolution used by that calculation;
- the relevant ACL/policy locator set for a candidate firewall.

NEP does not own:

- Resource Catalogue Resource identity;
- a generic infrastructure/CMDB catalogue;
- physical device/chassis identity as a separate MVP concept;
- configured ACL/policy bodies or entries;
- authorization/desired Access Rule semantics;
- desired-vs-configured reconciliation;
- vendor rendering or provider execution;
- historical NEP network-state snapshots.

Technical Access Evidence remains the owner of configured policy contents/evidence. NEP publishes only the firewall + policy locator information needed to find or acquire that evidence.

## Consequences

- the target model matches the actual uncertainty boundary: firewall candidate selection is heuristic/overrideable, while local current-state interpretation is deterministic for supported adapter semantics;
- the physical-device/provider-realization abstraction is removed from the MVP target because it adds no current business value;
- `asOf` and historical network snapshots are removed from the MVP candidate contract;
- SQL set-based candidate evaluation becomes the intended implementation shape through the persisted effective reachability projection;
- ACL attachment topology is kept out of the core domain until a consumer needs it;
- expensive policy bodies are not collected as a side effect of refreshing routing state;
- polling cost and connection behaviour can be tuned per firewall.

## Deferred questions

The following are intentionally not fixed by this ADR:

- exact Firewall lifecycle and command set;
- exact Firewall mutation/concurrency semantics;
- concrete secret/profile storage mechanism;
- exact retry/backoff scheduling policy;
- source-specific multipath/ECMP/PBR/VRF semantics beyond what a supported adapter can normalize truthfully;
- implementation migration from the current I19/I26 persistence/code model.
