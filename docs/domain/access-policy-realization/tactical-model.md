# Access Policy Realization — MVP Tactical DDD model

Status: `S2 MVP Tactical model accepted for convergence 2026-09-15`.

## Purpose

Own the source-neutral semantic decision:

> for one explicit policy comparison scope, how does complete configured effective permit space compare with complete required effective permit space, and which additive vendor-neutral change may safely be handed downstream?

APR does not own provider syntax, enforcement-target discovery, authorization, execution or persistence merely because a calculation may be expensive.

## Tactical shape

The first MVP APR model does **not** require a durable aggregate or editable remediation-plan lifecycle.

Its domain concepts are immutable semantic values and domain operations:

```text
ComparisonScope
EffectivePermitSpace
RealizationAssessment
SemanticDelta
VerifiedChangeIntent
```

The Bounded Context is justified by ownership of comparison/change-verification semantics, not by a requirement to persist an aggregate.

## Value — ComparisonScope

```text
ComparisonScope {
    firewallRef
    accessListName
}
```

`ComparisonScope` is a value identifying the exact technical policy scope being compared. It has no lifecycle independent of its fields.

Two APR inputs are comparable only when their ComparisonScope values are equal.

APR does not infer one scope from another and does not merge distinct ACL/policy locators into one synthetic scope.

## Value — PermitRegion

For the first HostAddress-based MVP path, the minimum source-neutral effective-permit atom is:

```text
PermitRegion {
    sourceHostAddress
    destinationHostAddress
    protocolSelector
    sourcePortConstraint
    destinationPortConstraint
}
```

The exact protocol/port vocabulary is the normalized ACC traffic vocabulary supported by the first vertical path. Provider-native rule/object identities are not part of this value.

A `PermitRegion` denotes effective access semantics, not one native firewall rule.

Future Prefix-aware or richer service/address algebra may extend the value vocabulary without changing ComparisonScope or APR ownership.

## Value — EffectivePermitSpace

```text
EffectivePermitSpace = finite semantic union of PermitRegion
```

The space is compared by semantic set meaning, not by rule count, ordering or provider decomposition.

Equivalent decompositions are the same EffectivePermitSpace.

Canonicalization/deduplication is allowed only when semantic coverage and provenance attribution are preserved.

For the MVP domain, the required operations are:

```text
intersection(left, right)
difference(left, right)
union(left, right)
isEmpty(space)
```

How these operations are executed at scale is Architecture, not Tactical DDD.

## Input classification

APR consumes two published semantic inputs for one attempted comparison:

```text
RequiredPolicyInput {
    comparisonScope
    requiredPermitSpace
    requiredProvenance
    freshness
    completeness = Complete
}

ConfiguredPolicyInput {
    comparisonScope
    configuredPermitSpace
    configuredProvenance
    baseConfiguredCorrelation
    freshness
    completeness: Complete | Incomplete | Unknown
    unsupportedSemantics
}
```

An upstream unresolved required materialization is not a complete RequiredPolicyInput with an empty permit space.

Likewise, missing/failed provider evidence is not a complete empty ConfiguredPolicyInput.

APR therefore distinguishes explicit complete emptiness from unresolved/unknown evidence.

## Derived value — SemanticDelta

For complete comparable inputs:

```text
SemanticDelta {
    commonPermitSpace
    missingPermitSpace
    excessPermitSpace
}

common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

`SemanticDelta` has no independent identity or lifecycle. It is completely determined by the two compared effective spaces and their provenance.

Provenance must remain sufficient to explain which required contributors demand a missing region and which configured evidence exposes an excess region.

## Derived value — RealizationAssessment

```text
RealizationAssessment =
    ComparableAssessment
  | Uncomparable
```

### ComparableAssessment

```text
ComparableAssessment {
    comparisonScope
    status: Realized | Drift
    delta: SemanticDelta
    requiredProvenance
    configuredProvenance
}
```

Exact invariant:

```text
Realized <=> missing is empty AND excess is empty
Drift    <=> missing is non-empty OR excess is non-empty
```

No other condition may produce `Realized`.

### Uncomparable

`Uncomparable` is produced when APR cannot establish the preconditions for exact semantic comparison, including at least:

- comparison-scope mismatch;
- configured input incomplete or unknown;
- unsupported configured semantics relevant to the scope;
- missing/unresolved required input passed as an attempted comparison boundary violation.

`Uncomparable` is neither `Realized` nor `Drift` and cannot authorize a change intent.

It is an immutable result value, not an operational failure state machine.

## Change-design rule — additive only

The first MVP has no accepted managed-policy ownership proving that NAPMS may remove unexplained configured permits.

Therefore APR change design is intentionally one-sided:

```text
missing != empty -> MAY design ENSURE-PERMIT
excess            -> evidence/report only
Realized          -> no intent
Uncomparable      -> no intent
```

APR must never derive `REMOVE`, `DENY`, `NARROW`, `REPLACE` or equivalent destructive semantics from `excess` in this MVP model.

## Value — VerifiedChangeIntent

```text
VerifiedChangeIntent {
    comparisonScope
    operation = ENSURE-PERMIT
    permitSpace
    baseConfiguredCorrelation
    requiredPolicyProvenance
    deltaProvenance
    verificationEvidence
}
```

This is an immutable semantic handoff value, not a durable aggregate in the MVP.

### Intent invariants

1. `permitSpace` is non-empty.
2. `permitSpace` is exactly the selected missing effective permit space from one ComparableAssessment.
3. `operation` is only `ENSURE-PERMIT` in the MVP vocabulary.
4. intent comparisonScope equals the assessment comparisonScope.
5. baseConfiguredCorrelation identifies the configured semantic basis against which the intent was verified.
6. no provider-native syntax/object/rule identity is part of the intent.
7. intent provenance remains sufficient to trace the required basis and delta that produced it.

## Semantic verification meaning

APR verifies the **semantic effect** of the additive intent before provider rendering.

For current configured permit space `C` and intent permit space `M`:

```text
proposed = C ∪ M
```

Verification requires at least:

```text
M == missing
C ⊆ proposed
required ⊆ proposed
```

Thus the verified additive intent:

- covers all selected missing required permits;
- never narrows previously configured effective permit space;
- does not claim authority over `excess`.

Important consequence:

If the original assessment has both `missing` and `excess`, applying the verified additive intent can satisfy all currently required permits while unexplained excess remains. APR must **not** call that resulting policy `Realized` without a new configured observation/comparison showing both missing and excess are empty.

`VerifiedChangeIntent` therefore proves the accepted additive effect, not final convergence.

## Provenance / explanation classification

Explainability is domain-significant; a result that cannot identify the semantic basis of its missing/excess/intent meaning is incomplete.

However:

- exact provenance row/schema/index structure;
- materialized attribution tables;
- cache layout;
- evidence storage normalization;

are Architecture/Implementation concerns, not Tactical DDD.

The Tactical invariant is only that the semantic values retain sufficient attribution references to explain their derivation.

## Domain operations

The minimum domain operations are:

```text
AssessRealization(required, configured)
    -> ComparableAssessment | Uncomparable

DesignAdditiveChange(ComparableAssessment)
    -> Candidate ENSURE-PERMIT | None

VerifyAdditiveChange(candidate, assessment/base correlation)
    -> VerifiedChangeIntent | verification failure
```

These are domain meanings, not frozen class/service/API names.

Comparison, change design and verification remain distinct decisions even if an implementation computes them in one call.

## Identity and lifecycle classification

For the first MVP:

- ComparisonScope is a value;
- PermitRegion/EffectivePermitSpace are values;
- SemanticDelta is a derived value;
- RealizationAssessment is a derived immutable result;
- VerifiedChangeIntent is an immutable handoff value;
- none of these require independent durable identity, aggregate lifecycle or editable state.

If a future user journey requires saving, approving, editing, scheduling or retrying remediation plans as business objects, that requirement may introduce a new APR aggregate/lifecycle. It is not pre-created now.

## Ownership invariants

1. APR owns comparison, delta, accepted change design and semantic verification.
2. RPM owns composition of complete required target policy; APR does not reconstruct ACC/AD/RC/NEP truth.
3. Provider Policy Interpreter owns provider-native interpretation into configured effective semantics.
4. Provider Policy Renderer owns provider-native representation of verified intent.
5. NEO owns controlled mutation lifecycle/outcome.
6. APR never selects a Firewall/ACL target and never infers mutation authority.

## Deferred beyond MVP DDD

Explicit future product/domain extensions:

- Prefix-aware/richer address-space comparison vocabulary;
- destructive/removal/narrowing change vocabulary after managed-policy ownership is accepted;
- durable remediation-plan lifecycle if a real user journey requires it;
- richer provider-semantic classes beyond the first supported interpreted vocabulary.

Explicit downstream non-DDD concerns:

- data-local/indexed computation strategy for large policy spaces;
- ERD/table/index/materialization choices;
- target/current code migration mechanics;
- persistence/cache decisions for derived assessment/delta values;
- provider round-trip mechanism used to prove renderer equivalence;
- transport DTOs and workflow orchestration.

## Tactical coherence result

The first MVP APR domain can now be implemented without inventing Tactical meaning:

- comparison scope has explicit value identity;
- effective permit space has explicit semantic set meaning;
- comparison/delta statuses are exact;
- unresolved evidence cannot become empty policy;
- additive-only change design is explicit;
- `VerifiedChangeIntent` has precise invariants and no invented durable lifecycle;
- remaining scale/persistence/migration questions are correctly downstream rather than open Tactical DDD.

No remaining APR Tactical decision is required by the accepted first MVP happy path.
