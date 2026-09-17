# ADR-020 — Required Policy Materialization is a derived composition

Status: `accepted current target decision; inputs revalidated 2026-09-16`.

The core decision remains: Required Policy Materialization (RPM) is a non-peer derived composition, not a Bounded Context. It composes published upstream semantics and never becomes an independent source of policy, deployment, Resource realization or enforcement-relevance truth.

## Current inputs

```text
Access Policy current effective Policy Rules
+ ACC exact immutable InteractionContractRevision semantics
+ Application Deployment concrete ComponentDeployment -> ResourceRef truth
+ RC effective Resource AddressSpace
+ NEP candidate target/policy locators
-> TargetRequiredPolicy[] | unresolved
-> APR
```

Source contexts retain authority. RPM must not navigate peer-private models or re-decide authorization, deployment identity, Resource realization or enforcement relevance.

## Current Resource realization contract

```text
ResourceRef + logicalTime
-> AddressSpace? = HostAddress | Prefix
```

For current scope one Resource has at most one effective AddressSpace at one logical time. Missing realization is unresolved. A Prefix remains a Prefix and is not expanded into individual hosts.

`ResourceEndpoint`, endpoint cross-products and deployment-specific endpoint selection are not current target semantics.

## MVP materialization pipeline

For one currently effective Policy Rule:

```text
EffectivePolicyRule
    policyRuleRef
    sourceComponentDeploymentRef
    destinationComponentDeploymentRef
    revisionRef

revisionRef
    -> ACC InteractionContractRevision
       -> owning Interaction
       -> sourceComponentRef
       -> destinationComponentRef
       -> trafficAlternatives[1..N]

sourceComponentDeploymentRef
    -> AD ComponentDeployment
       -> source ComponentRef
       -> source ResourceRef

destinationComponentDeploymentRef
    -> AD ComponentDeployment
       -> destination ComponentRef
       -> destination ResourceRef

ResourceRef
    -> RC CurrentResourceRealization
    -> AddressSpace
```

RPM must verify the concrete deployment Components match the exact revision's Interaction endpoints. A mismatch is unresolved/corrupt input and must not be silently normalized.

There is no whole-Application deployment placement-set expansion in the target model. One Policy Rule already identifies one concrete source and one concrete destination Component Deployment.

If the same Component is deployed on several Resources, those are several ComponentDeployment identities. They participate in required policy only through their own effective Policy Rules.

For the first target-specific NEP path, each supported technical pair resolves to:

```text
HostAddress -> HostAddress
```

If either side resolves to `Prefix`, RPM returns unresolved for that target-specific materialization rather than expanding the Prefix into hosts or inventing Prefix-routing semantics.

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

A candidate is relevance-to-inspect/affect, not proof of end-to-end traversal. Multiple candidates/locators are preserved; RPM never chooses an arbitrary route/winner.

## Normalized required predicate

For each effective Rule and each traffic alternative in its exact revision, RPM derives one vendor-neutral required permit predicate:

```text
NormalizedRequiredPredicate {
    sourceAddressSpace
    destinationAddressSpace
    trafficAlternative
}
```

RPM preserves the complete atomic InteractionContractRevision meaning. It cannot materialize only a preferred subset of traffic alternatives.

Equivalent predicates may be deduplicated only when all contributing `PolicyRuleRef` provenance is retained.

## Comparison target and TargetRequiredPolicy

The minimum comparable target scope remains:

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

A FirewallCandidate with several access-list names yields several comparison scopes. Several candidates likewise yield several `TargetRequiredPolicy` values. Candidate ordering has no route meaning.

RPM does not decide provider-native rule changes. APR compares each target-specific required permit space with the corresponding configured effective policy snapshot.

## Unresolved semantics

`unresolved` is first-class and is not equivalent to empty required policy.

Materialization is unresolved when any required input prevents complete target-specific projection, including at least:

- Access Policy cannot establish the Rule as currently effective;
- the exact InteractionContractRevision cannot be resolved;
- a source/destination ComponentDeployment cannot be resolved;
- a ComponentDeployment Component does not match the corresponding Interaction endpoint Component;
- a ComponentDeployment Resource cannot be resolved;
- a Resource has no effective RC AddressSpace;
- RC returns `Prefix` while the target-specific NEP edge remains HostAddress-only;
- NEP returns no candidate target for a required technical pair;
- a returned candidate has no access-list locator;
- required upstream completeness/provenance needed to claim the result is unknown.

RPM may retain diagnostics/partial derivation internally for explanation, but it must not publish partial policy to APR as though complete.

An empty required-policy meaning may only come from an explicitly empty effective policy input for an explicitly known comparison scope. Missing evidence or failed materialization never becomes `requiredPermitSpace = []`.

## Freshness and provenance

`TargetRequiredPolicy` carries enough source references to explain derivation without copying ownership:

- contributing Access Policy `PolicyRuleRef` values/current authorization provenance;
- exact ACC `InteractionContractRevisionRef`;
- source/destination AD `ComponentDeploymentRef` and Resource correlation;
- RC Resource realization provenance/freshness;
- NEP candidate/locator freshness;
- materialization logical time.

Exact serialization is Architecture/implementation work.

## NEP and target projection

NEP owns only candidate Firewall and relevant ACL/policy-name discovery. It does not decide what Rule must be authorized or what provider-native change must be made.

RPM uses every returned `firewallId + accessListName` as a comparison scope. APR decides required-versus-configured difference from source-neutral effective policy semantics.

## Consequences

- no peer BC is introduced for orchestration;
- Access Policy supplies current effective concrete Rule truth only;
- ACC supplies exact immutable traffic semantics and endpoint Component meaning;
- Application Deployment supplies concrete ComponentDeployment -> ResourceRef truth;
- RC supplies Resource-level HostAddress-or-Prefix realization;
- RPM no longer performs source-placement × destination-placement Cartesian expansion;
- independent replicas require independent effective Policy Rules;
- NEP supplies every candidate enforcement location/policy locator without claiming a proven path;
- RPM produces complete target-specific normalized required permit space or explicit unresolved state;
- APR receives comparable `TargetRequiredPolicy` values rather than reconstructing upstream semantics;
- future multi-address/interface or Prefix-aware NEP requirements reopen only their affected contracts.
