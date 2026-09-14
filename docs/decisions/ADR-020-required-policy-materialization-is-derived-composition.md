# ADR-020 — Required Policy Materialization is a derived composition

Status: `accepted`.

Date: 2026-09-14.

## Context

G1 requires current semantic authorization to be translated into normalized technical access and then scoped to candidate enforcement targets before APR compares required and configured effective policy.

The chain consumes authoritative facts owned elsewhere:

```text
Access Policy effective Policy Rules
    + ACC deployed Interaction / traffic contract
    + Resource Catalogue current endpoint/address realization
    + NEP candidate enforcement locations / policy locators
        -> target-specific required effective policy
        -> APR
```

No evidence establishes an independent business identity, approval lifecycle or source truth for the intermediate materialization itself.

## Decision

### 1. Do not introduce a Required Policy Materialization Bounded Context

Required Policy Materialization is a non-peer application/domain composition over published contracts of existing Bounded Contexts.

It owns no upstream fact. Its outputs are derived and rebuildable from an explicit input snapshot/provenance set.

### 2. Inputs remain owned by their source contexts

- Access Policy publishes current effective semantic Policy Rules.
- ACC publishes the exact deployed Interaction subject and immutable protocol/port contract.
- Resource Catalogue publishes current ResourceEndpoint/address realization for each Resource.
- NEP publishes candidate Firewall/policy-locator results for technical source/destination pairs.

The composition must not navigate peer-private persistence models or re-derive their authoritative decisions.

### 3. MVP Resource realization contract

For materialization, each ComponentDeployment resolves to exactly one Resource.

A Resource may expose zero or more current ResourceEndpoints. `ResourceEndpoint` is a stable logical L3 presence of the Resource; changing its address does not create a new Endpoint.

For MVP each Endpoint has at most one current address realization. The address is the corporate-visible host/prefix used for access management; NAT discovery/calculation remains outside Resource Catalogue.

An Endpoint with no current address is valid catalogue truth but makes affected authorization technically unresolved rather than equivalent to an empty required policy.

### 4. Predicate derivation

For each effective Policy Rule, materialization forms the cross-product of current source Endpoint addresses and current destination Endpoint addresses and combines each pair with the complete immutable Interaction traffic contract.

The resulting normalized required-access predicate carries conceptually:

```text
source address/prefix
+ destination address/prefix
+ protocol
+ relevant port constraints
+ contributing PolicyRule provenance
```

Several Policy Rules may support the same normalized predicate. Deduplication must preserve the set of contributing semantic Rule references/provenance.

### 5. Target projection

Each technical source/destination pair is submitted to NEP. Every returned `firewallId + accessListName` candidate locator becomes an independent target correlation for required-policy projection.

A candidate Firewall with no policy locator is not silently discarded. It produces an unresolved target-policy condition because APR cannot compare a concrete target policy without a comparable locator/scope.

The composition must not reinterpret NEP routing/override evidence or infer an end-to-end path.

### 6. TargetRequiredPolicy is derived

The public downstream result is a derived target-specific required policy, conceptually:

```text
TargetRequiredPolicy
    targetRef / firewallId
    policyLocator
    required effective normalized predicates
    contributing PolicyRule refs
    input freshness / provenance refs
    logical/effective time
```

It is grouped from all effective semantic authorizations that require access on the same comparable target/policy locator.

Revoking one Policy Rule recomputes the aggregate projection; a technical predicate remains required when another effective Rule still contributes it.

### 7. Unresolved materialization is first-class

A semantically valid Policy Rule is reported as unresolved when required technical projection cannot be completed, including at least:

- Deployment has no valid Resource realization;
- Resource has no current Endpoint/address realization needed for the subject;
- NEP cannot determine a comparable policy locator for a candidate target;
- required upstream facts are unavailable/ambiguous for the selected logical time.

Unresolved materialization is not `Realized`, not `Missing`, and not an empty required policy. APR receives only comparable `TargetRequiredPolicy` inputs; unresolved cases remain visible to the upstream composition/reconciliation surface.

## Consequences

- no new peer BC is introduced merely for orchestration;
- source contexts remain authoritative for their own facts;
- APR receives target-specific required effective policy and does not reconstruct authorization/catalogue/placement semantics;
- provenance survives many-to-one predicate deduplication;
- revocation is aggregate recomputation, not deletion of a historical firewall line;
- Resource Catalogue endpoint/address semantics require revalidation to the stable Endpoint + separate corporate-visible address realization model;
- provider-specific configured-policy normalization/rendering remains a separate unresolved boundary.
