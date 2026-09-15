# Access Policy Realization — Tactical DDD model

Status: `current target`.

## Purpose

Own the source-neutral semantic decision for one exact policy comparison scope: compare complete configured effective permit space with complete required effective permit space, explain the delta, and produce only a verified additive change intent when permitted by current semantics.

APR does not own provider syntax, enforcement-target discovery, authorization or execution.

## Core values

```text
ComparisonScope {
    firewallRef
    accessListName
}

PermitRegion {
    sourceHostAddress
    destinationHostAddress
    protocolSelector
    sourcePortConstraint
    destinationPortConstraint
}

EffectivePermitSpace = finite semantic union of PermitRegion
```

Two inputs are comparable only when their ComparisonScope values are equal. Effective permit space is compared by semantic set meaning, not native rule count, ordering or provider decomposition.

## Inputs

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

Missing or unresolved evidence is not a complete empty permit space.

## Semantic delta and assessment

For complete comparable inputs:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

```text
SemanticDelta {
    commonPermitSpace
    missingPermitSpace
    excessPermitSpace
}

RealizationAssessment = ComparableAssessment | Uncomparable
```

`Realized` iff missing and excess are both empty. `Drift` iff either is non-empty. Scope mismatch, incomplete/unknown configured input, relevant unsupported semantics or unresolved required input produce `Uncomparable`.

## Additive change design

Current automated change semantics are intentionally one-sided:

```text
missing != empty -> MAY design ENSURE-PERMIT
excess            -> evidence/report only
Realized          -> no intent
Uncomparable      -> no intent
```

APR does not derive destructive `REMOVE`, `DENY`, `NARROW` or `REPLACE` intent from excess access.

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

Intent invariants:

- permitSpace is non-empty and exactly the selected missing permit space;
- comparisonScope equals the assessment scope;
- baseConfiguredCorrelation identifies the configured semantic basis;
- no provider-native syntax/object/rule identity is part of the intent;
- provenance remains sufficient to explain required basis and delta.

For configured space `C` and missing space `M`, semantic verification uses `proposed = C ∪ M` and requires `M == missing`, `C ⊆ proposed`, and `required ⊆ proposed`. This proves the additive effect, not final convergence; a new observation/comparison is required to prove `Realized`.

## Domain operations

```text
AssessRealization(required, configured)
    -> ComparableAssessment | Uncomparable

DesignAdditiveChange(ComparableAssessment)
    -> Candidate ENSURE-PERMIT | None

VerifyAdditiveChange(candidate, assessment/base correlation)
    -> VerifiedChangeIntent | verification failure
```

## Ownership invariants

- APR owns comparison, delta, accepted change design and semantic verification.
- Required Policy Materialization owns composition of complete required target policy.
- Provider Policy Interpreter owns provider-native interpretation into configured effective semantics.
- Provider Policy Renderer owns provider-native representation of verified intent.
- NEO owns controlled mutation lifecycle and outcome.
- APR never selects a Firewall/ACL target and never infers mutation authority.
