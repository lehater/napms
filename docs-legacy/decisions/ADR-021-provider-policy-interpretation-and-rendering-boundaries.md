# ADR-021 — Provider policy interpretation and rendering are boundary adapters around source-neutral policy semantics

Status: `accepted S2 decision`.

Date: 2026-09-14.

## Context

The revalidated realization chain requires two opposite transformations around Access Policy Realization (APR):

```text
provider/device configuration
    -> configured effective policy
    -> APR comparison/change design/verification
    -> verified change intent
    -> provider/device representation
    -> Network Environment Operations
```

The current repository contains historical implementation where APR also owns provider rendering. Technical Access Evidence (TAE) also stores source-neutral technical predicates, which creates a risk of assigning configured-policy interpretation to TAE merely because normalized evidence can be persisted there.

Neither existing implementation structure nor similarity of value types establishes semantic ownership.

The target must preserve these accepted guarantees:

- APR compares source-neutral effective policy semantics, not raw provider rows;
- ordered rules, deny/default behavior, objects/groups, aliases and other provider semantics must be interpreted before APR treats configured input as comparable effective policy;
- provider/device mutation remains Network Environment Operations (NEO);
- TAE records source-qualified evidence and does not choose current/fresh/complete configured policy for consumers;
- rendering must preserve verified semantics and must not quietly broaden or narrow access.

## Decision

### 1. Provider-specific policy interpretation is an integration/adapter responsibility, not a new Bounded Context

A provider policy interpreter consumes provider-native configuration/evidence plus the provider semantics needed to evaluate it and publishes a source-neutral configured effective-policy projection.

Conceptually:

```text
ProviderPolicyState
    + ProviderSemantics
    + explicit target/policy scope
        -> ConfiguredEffectivePolicySnapshot
```

The interpreter owns representation translation, including provider-specific ordering, deny/default semantics, objects/groups, service aliases and other constructs required to determine effective behavior exactly for the supported slice.

It does not own authorization, required access, target-placement relevance, APR delta, source evidence history or device mutation lifecycle.

Provider interpretation has no independent business identity/lifecycle/invariant that justifies a peer Bounded Context. It is an integration capability implementing a published source-neutral contract.

### 2. ConfiguredEffectivePolicySnapshot is a consumer-facing semantic projection

The projection must identify the comparable unit and carry enough provenance/completeness information for APR to decide whether a complete realization conclusion is valid.

Conceptually:

```text
ConfiguredEffectivePolicySnapshot
    targetRef
    policyLocator / comparisonScope
    effectivePermitSpace
    sourceCapture/evidence references
    evidence/effective time where known
    completeness: Complete | Incomplete | Unknown
    interpreter identity/version
    unsupportedSemantics[]
```

Exact transport/storage shape is S3/S4 work. The semantic guarantees are S2.

Rules:

- `Complete` may be asserted only by an explicit source/interpreter contract for the comparison scope;
- `Incomplete | Unknown` cannot be interpreted as an empty effective policy;
- unsupported provider semantics fail closed for complete APR comparison;
- normalization must neither broaden nor narrow represented effective access;
- raw provider rule identity/order may be preserved as provenance but is not policy-semantic identity.

For the current target, comparable effective policy is expressed as normalized effective permit space. Provider deny/order/default mechanics are inputs to computing that space, not desired-policy actions inside APR.

### 3. TAE is evidence storage, not configured-policy publication ownership

TAE may receive and persist source-neutral provider-derived evidence when useful. It continues to own immutable source-qualified capture facts only.

TAE does not decide which capture is current for APR, whether a capture is complete for a comparison target, or which target/policy correlation APR should compare.

A provider interpreter may use raw/provider source material directly, TAE evidence through an explicit source contract, or both. The resulting `ConfiguredEffectivePolicySnapshot` is a consumer/integration projection, not a new authoritative TAE aggregate.

### 4. APR core owns source-neutral policy semantics, reconciliation, change design and semantic verification

APR receives comparable source-neutral inputs:

```text
TargetRequiredPolicy
ConfiguredEffectivePolicySnapshot
```

and owns exact effective-policy algebra, `common / missing / excess`, realization assessment, vendor-neutral change design and semantic verification of the proposed resulting effective policy.

APR does not parse provider-native syntax and does not make provider-specific rule-order/object/default semantics part of its core model.

### 5. Provider-specific rendering is an output adapter responsibility, not APR domain ownership

After APR has produced semantically verified vendor-neutral change intent, a provider renderer translates that intent into a target representation accepted by NEO.

Conceptually:

```text
VerifiedChangeIntent
    + Target/ProviderCapabilities
    + base target revision/correlation
        -> TargetPolicyArtifact
```

The renderer owns provider representation translation and capability checks. It does not own the meaning of the desired semantic result and may not reinterpret APR's verified intent.

### 6. Semantic equivalence is an APR-facing contract; provider rendering mechanism remains outside APR core

A successful renderer must establish that the produced target representation corresponds to the verified semantic intent for the supported provider semantics.

This may be proven by deterministic construction, interpretation/round-trip verification, provider simulation, or another architecture mechanism selected later. S2 requires the semantic-equivalence guarantee, not one mechanism.

If equivalence cannot be established, rendering fails closed and NEO receives no executable artifact.

### 7. NEO owns execution, not reinterpretation

NEO consumes `TargetPolicyArtifact` plus mutation authority/precondition inputs. It owns operation identity, concurrency/pre-check, apply outcome and post-operation evidence.

NEO does not rewrite provider policy intent for convenience and does not turn a renderer failure/unsupported result into an executable operation.

Post-operation convergence remains a comparison of subsequently observed normalized configured effective policy against required policy; apply success alone is insufficient.

## Consequences

- no new provider-normalization or rendering Bounded Context is introduced;
- APR remains provider-neutral at its core semantic boundary;
- TAE does not acquire hidden current-policy/reconciliation semantics;
- NEO remains a safe execution boundary rather than a configuration translator;
- provider-specific interpretation and rendering may share implementation libraries/adapters where useful without becoming a shared domain owner;
- unsupported provider semantics fail closed rather than being approximated into false policy certainty;
- current APR renderer code is migration evidence and must be reclassified during Architecture/Implementation migration rather than treated as target ownership;
- provider-specific interpretation/rendering architecture, capability negotiation, caching and transport remain downstream design work.
