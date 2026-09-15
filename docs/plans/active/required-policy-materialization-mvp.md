# Required Policy Materialization MVP convergence

Status: `active MVP derived-composition convergence`.

Date: 2026-09-15.

## Goal

Define only the minimum Required Policy Materialization semantics required to convert one currently authorized governed interaction into one comparable target-specific required-policy result for APR.

RPM remains a non-peer derived composition, not a Bounded Context. It must compose published upstream projections without taking ownership of authorization, placement, Resource realization or enforcement relevance.

## Accepted inputs

```text
Access Policy current effective Policy Rule
+ ACC immutable Interaction traffic semantics
+ AD applicable ComponentPlacements / ResourceRefs
+ RC effective AddressSpace = HostAddress | Prefix
+ NEP FirewallCandidate / AccessListLocator relevance
-> TargetRequiredPolicy | unresolved
-> APR
```

Relevant accepted constraints:

- Policy Rule identity is the governed interaction subject;
- AP alone decides whether the subject is currently authorized;
- ACC owns traffic semantics;
- AD owns current placement truth;
- RC owns Resource address realization;
- NEP candidate membership means relevance-to-inspect, not proven network path;
- missing/ambiguous required input is unresolved, not empty policy and not realized policy;
- RPM must retain contributing PolicyRule provenance.

## Current task

Specify the smallest happy-path composition for exactly one authorized Policy Rule:

1. resolve source/destination endpoint Components from the governed Interaction;
2. obtain current applicable ComponentPlacements from AD;
3. resolve each placement ResourceRef through RC to one HostAddress or Prefix;
4. combine source/destination AddressSpace with the complete ACC traffic contract into normalized required predicates;
5. submit each technical source/destination pair to NEP for candidate Firewall / AccessListLocator relevance;
6. group the predicates by comparable target/scope into `TargetRequiredPolicy`;
7. preserve provenance/as-of/freshness and return explicit unresolved state when a required input cannot be resolved.

## MVP guardrails

Do not introduce:

- a new RPM bounded context or persistent source of truth;
- endpoint/interface/VIP identities;
- route/path certainty beyond NEP candidate semantics;
- host expansion of Prefix values;
- generalized optimization/deduplication beyond exact equivalent predicates with contributor preservation;
- configured-policy comparison logic owned by APR/PPI;
- rendering/provider syntax;
- persistence/API mechanics unless implementation is explicitly authorized later.

## Exit criteria

- the input/output composition is explicit and deterministic for the first happy path;
- `TargetRequiredPolicy` minimum fields/invariants are explicit;
- unresolved versus empty versus effective required policy are distinguishable;
- source context ownership remains intact;
- no additional S1 product decision is invented;
- APR can consume the result without reconstructing ACC/AD/RC/NEP semantics;
- no implementation authorization is implied.

## Working set

- `docs/decisions/ADR-020-required-policy-materialization-is-derived-composition.md`
- `docs/domain/access-policy/tactical-model.md`
- `docs/domain/application-deployment/boundary.md`
- `docs/domain/resource-catalogue/tactical-model.md`
- `docs/domain/network-enforcement-placement/target-tactical-model.md`
- ACC Interaction/traffic-contract documentation as needed
- APR comparison contract as needed

## Next

Converge the minimum `TargetRequiredPolicy` shape and unresolved semantics for one end-to-end authorized interaction, then revalidate the APR handoff.
