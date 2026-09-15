# Access Policy Realization requirements

## Purpose

Define exact source-neutral comparison between complete required policy and complete configured effective policy, plus the currently supported safe remediation boundary.

## Comparison scope

```text
ComparisonScope {
    firewallId
    accessListName
}
```

APR compares only inputs for the same ComparisonScope that are complete enough to establish exact source-neutral effective permit semantics.

## Inputs

```text
TargetRequiredPolicy {
    comparisonScope
    requiredPermitSpace
    contributingPolicyRuleRefs
    logicalTime
    inputProvenance
    inputFreshness
}

ConfiguredEffectivePolicySnapshot {
    comparisonScope
    effectivePermitSpace
    completeness: Complete | Incomplete | Unknown
    evidence/provenance
    interpreter identity/version
    unsupportedSemantics[]
}
```

Unresolved Required Policy Materialization is not an empty `TargetRequiredPolicy`. `Incomplete | Unknown` configured input is not an empty configured policy.

## Exact comparison

For complete comparable inputs:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

APR distinguishes:

- `Realized` — `missing` and `excess` are both empty;
- `Drift` — at least one of `missing` or `excess` is non-empty;
- `Uncomparable` — exact comparison cannot be established because scope, completeness or supported semantics are insufficient.

`Uncomparable` is not Drift and authorizes no remediation.

## Remediation boundary

The current product contract does not establish that NAPMS owns every configured permit in an ACL. Remediation is therefore additive-only:

```text
missing -> APR may produce ENSURE-PERMIT change intent
excess  -> report/audit only; no automatic removal or narrowing
Realized -> no change intent
Uncomparable -> no change intent
```

`excess` means configured effective access not explained by current required policy. It does not establish authority to remove that access.

The current contract contains no automatic cleanup of excess policy, whole-ACL ownership, generalized remove/replace vocabulary, provider-specific optimization or editable remediation-plan lifecycle.

## VerifiedChangeIntent

APR may publish this source-neutral additive intent:

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

Requirements:

1. `permitSpace` is exactly the selected missing effective permit space.
2. The intent contains no provider-native rule/object syntax.
3. The intent contains no automatic removal/narrowing operation.
4. Base configured correlation is sufficient for downstream stale-base/precondition protection.
5. Verification proves that the intent covers selected missing permit space without narrowing previously configured effective permit space.
6. Provider rendering may choose representation only when it preserves the verified semantic intent.
7. Renderer failure or inability to prove semantic equivalence produces no executable artifact.
8. NEO execution authority and mutation lifecycle remain separate from APR semantic verification.
