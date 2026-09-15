# ADR-020 — Required Policy Materialization is a derived composition

Status: `accepted; affected inputs amended 2026-09-15`.

The core decision remains: Required Policy Materialization (RPM) is a non-peer derived composition, not a Bounded Context. The 2026-09-15 amendment replaces the former ACC-owned deployment and ResourceEndpoint inputs.

## Current inputs

```text
Access Policy effective Policy Rules
+ ACC immutable Interaction traffic semantics
+ AD applicable ComponentPlacements / ResourceRefs
+ RC effective Resource AddressSpace as-of selected time
+ NEP candidate target/policy locators
-> TargetRequiredPolicy | unresolved
-> APR
```

Source contexts retain authority. RPM must not navigate peer-private models or re-decide authorization, placement, Resource realization or enforcement relevance.

## Current Resource realization contract

```text
ResourceRef + logicalTime
-> AddressSpace? = HostAddress | Prefix
```

For current scope one Resource has at most one effective AddressSpace at one logical time. Missing realization is unresolved. A Prefix remains a Prefix and need not be enumerated into hosts.

`ResourceEndpoint`, endpoint cross-products and deployment-specific endpoint selection are superseded target semantics.

## Predicate derivation

For each effective governed Policy Rule, RPM resolves applicable source/destination ComponentPlacements through AD, then each ResourceRef through RC, and combines the resulting source/destination AddressSpace pair with the complete ACC traffic contract.

Normalized predicates preserve contributing PolicyRule provenance. Equivalent predicates may be deduplicated only while retaining all semantic contributors.

## NEP and target projection

Each technical source/destination pair is submitted to NEP. Candidate membership means relevance-to-inspect, not a proven path. Missing/ambiguous target or policy-locator information remains unresolved.

`TargetRequiredPolicy` carries comparison target/scope identity, normalized required predicates, contributing PolicyRule refs, input freshness/provenance and logical/effective time.

Unresolved materialization is not `Realized`, not `Missing`, and not empty required policy.

## Consequences

- no peer BC is introduced for orchestration;
- ACC supplies traffic semantics only;
- AD supplies deployment/placement truth;
- RC supplies Resource-level HostAddress-or-Prefix realization;
- NEP supplies candidate enforcement relevance/locators;
- APR receives comparable target-specific required policy rather than reconstructing upstream semantics;
- future multi-address/interface requirements reopen only the affected AD/RC/RPM contract.
