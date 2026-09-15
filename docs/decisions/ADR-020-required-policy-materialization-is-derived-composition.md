# ADR-020 — Required Policy Materialization is a derived composition

Status: `accepted; affected inputs amended 2026-09-15; MVP materialization shape aligned 2026-09-15`.

The core decision remains: Required Policy Materialization (RPM) is a non-peer derived composition, not a Bounded Context. It composes published upstream semantics and never becomes an independent source of authorization, placement, Resource realization or enforcement relevance truth.

## Current inputs

```text
Access Policy effective Policy Rules
+ ACC immutable Interaction traffic semantics
+ AD applicable ComponentPlacements / ResourceRefs
+ RC effective Resource AddressSpace as-of selected time
+ NEP candidate target/policy locators
-> TargetRequiredPolicy[] | unresolved
-> APR
```

Source contexts retain authority. RPM must not navigate peer-private models or re-decide authorization, placement, Resource realization or enforcement relevance.

## Current Resource realization contract

```text
ResourceRef + logicalTime
-> AddressSpace? = HostAddress | Prefix
```

For current scope one Resource has at most one effective AddressSpace at one logical time. Missing realization is unresolved. A Prefix remains a Prefix and is not expanded into individual hosts.

`ResourceEndpoint`, endpoint cross-products and deployment-specific endpoint selection are superseded target semantics.

## MVP materialization pipeline

For one currently authorized Policy Rule:

```text
GovernedInteractionSubject
    -> ACC InteractionContractRevision
       sourceComponentRef
       destinationComponentRef
       trafficAlternatives[1..N]

source ApplicationDeployment + source Component
    -> AD applicable ComponentPlacement[]

destination ApplicationDeployment + destination Component
    -> AD applicable ComponentPlacement[]

ComponentPlacement.ResourceRef
    -> RC CurrentResourceRealization
    -> AddressSpace
```

RPM forms the full source-placement × destination-placement technical pair set. Every applicable placement is part of completeness; RPM must not silently ignore one unresolved placement or Resource realization and still claim a complete materialization.

For the first end-to-end MVP happy path, the NEP query edge is supported only when each technical pair resolves to:

```text
HostAddress -> HostAddress
```

If either side resolves to `Prefix`, RPM returns unresolved for that materialization rather than expanding the Prefix into hosts or inventing Prefix-routing/override semantics that NEP has not accepted yet. Future Prefix-aware NEP query semantics reopen only the NEP/RPM edge; RC AddressSpace semantics do not change.

Each supported HostAddress pair is submitted to NEP:

```text
TrafficPair
    sourceAddress
    destinationAddress

-> FirewallCandidate[]
   firewallId
   accessListNames[]
   freshness metadata
```

A candidate is relevance-to-inspect/affect, not proof of end-to-end traversal. Multiple candidates are therefore valid and are all preserved; RPM never chooses an arbitrary winning Firewall or route.

## Normalized required predicate

For each supported technical source/destination pair and each traffic alternative in the immutable ACC contract, RPM derives one vendor-neutral required permit predicate:

```text
NormalizedRequiredPredicate {
    sourceAddressSpace       // HostAddress in first MVP vertical path
    destinationAddressSpace  // HostAddress in first MVP vertical path
    trafficAlternative       // complete ACC vendor-neutral protocol/port/service semantics
}
```

RPM must preserve the entire atomic InteractionContractRevision traffic meaning. It cannot authorize/materialize only a preferred subset of its traffic alternatives.

Equivalent predicates may be deduplicated only when all contributing PolicyRule references/provenance are retained.

## Comparison target and TargetRequiredPolicy

The minimum comparable target scope is the NEP result pair:

```text
ComparisonScope {
    firewallId
    accessListName
}
```

For every relevant `firewallId + accessListName`, RPM groups all required predicates that may be affected by that policy scope:

```text
TargetRequiredPolicy {
    comparisonScope {
        firewallId
        accessListName
    }
    requiredPermitSpace: NormalizedRequiredPredicate[1..N]
    contributingPolicyRuleRefs[1..N]
    logicalTime
    inputProvenance
    inputFreshness
}
```

A FirewallCandidate with several distinct access-list names yields several comparison scopes. Several FirewallCandidates likewise yield several `TargetRequiredPolicy` values. Candidate ordering has no semantic meaning.

RPM does not decide the provider-native rule change. APR compares each target-specific required permit space with the corresponding configured effective policy snapshot.

## Unresolved semantics

`unresolved` is a first-class outcome and is not equivalent to an empty required policy.

For the first happy path, materialization is unresolved when any required input prevents a complete target-specific projection, including at least:

- AP does not expose the subject as currently authorized;
- the governed InteractionContractRevision or its complete traffic contract cannot be resolved;
- required source/destination ComponentPlacements are unresolved/incomplete;
- a placement Resource has no effective RC AddressSpace;
- RC returns `Prefix` on either side while Prefix-aware NEP query semantics remain unsupported by the MVP vertical path;
- NEP returns no candidate target for a required technical pair;
- a returned candidate has no `accessListName`, so no comparable policy scope can be formed;
- required upstream completeness/provenance needed to claim the result is unknown.

RPM may retain diagnostics/partial derivation internally for explanation, but it must not publish a partial result to APR as though it were a complete `TargetRequiredPolicy`.

An empty required-policy meaning may only come from an explicitly empty authorized input set for an explicitly known comparison scope. Missing evidence, missing target, missing locator or failed materialization must never be encoded as `requiredPermitSpace = []`.

## Freshness and provenance

`TargetRequiredPolicy` carries enough source references to explain its derivation without copying source ownership:

- contributing AP PolicyRule references / authorization provenance;
- immutable ACC InteractionContractRevision reference;
- AD placement resolution/as-of evidence;
- RC Resource realization provenance/freshness;
- NEP candidate/locator freshness such as `snapshotCollectedAt`;
- materialization logical time.

Exact serialization is downstream Architecture/implementation work.

## NEP and target projection

NEP owns only candidate Firewall and relevant ACL/policy-name discovery. It does not decide what rule must be added or removed.

RPM uses every returned `firewallId + accessListName` as a comparison scope for the required permit semantics associated with the queried TrafficPair. APR then decides required-versus-configured difference from source-neutral effective policy semantics.

If NEP knows a candidate Firewall but cannot determine any policy locator, RPM cannot form a comparable target and remains unresolved for the affected materialization.

## Consequences

- no peer BC is introduced for orchestration;
- ACC supplies traffic semantics only;
- AD supplies deployment/placement truth;
- RC supplies Resource-level HostAddress-or-Prefix realization;
- the first MVP end-to-end NEP edge accepts only HostAddress pairs; Prefix stays first-class upstream and fails closed at materialization until Prefix-aware NEP semantics are explicitly designed;
- NEP supplies every candidate enforcement location and policy locator without claiming a proven path;
- RPM produces complete target-specific normalized required permit space or explicit unresolved state;
- APR receives comparable `TargetRequiredPolicy` values rather than reconstructing upstream semantics;
- future multi-address/interface or Prefix-aware NEP requirements reopen only their affected AD/RC/NEP/RPM contracts.
