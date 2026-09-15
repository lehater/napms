# Access Policy Realization — MVP requirements

Status: `G1 MVP comparison and additive remediation behavior accepted`.

Date: 2026-09-15.

## Purpose

Define only the observable Access Policy Realization behavior required by the first end-to-end MVP path from a complete target-specific required policy to a safe source-neutral change intent.

## Comparison scope

The current MVP comparison unit is:

```text
ComparisonScope {
    firewallId
    accessListName
}
```

APR compares only inputs that refer to the same ComparisonScope and are complete enough to establish exact source-neutral effective permit semantics.

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

RPM unresolved is not an empty TargetRequiredPolicy. `Incomplete | Unknown` configured input is not an empty configured policy.

## Exact comparison

For complete comparable inputs:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

APR shall distinguish:

- `Realized` — `missing` and `excess` are both empty;
- `Drift` — at least one of `missing` or `excess` is non-empty;
- `Uncomparable` — exact comparison cannot be established because scope, completeness or supported semantics are insufficient.

`Uncomparable` is not drift and shall not authorize remediation.

## Accepted MVP remediation boundary

The current target has no accepted managed-policy scope proving that NAPMS owns every configured permit in an ACL.

Therefore remediation is additive-only for the MVP:

```text
missing -> APR may produce ENSURE-PERMIT change intent
excess  -> report/audit only; no automatic removal or narrowing
Realized -> no change intent
Uncomparable -> no change intent
```

`excess` means configured effective access not explained by current required policy. It does not by itself establish authority to remove that access.

Automatic removal/narrowing requires a later accepted product rule defining the managed policy scope and the authority under which configured access may be removed.

## Minimal VerifiedChangeIntent

For the MVP, APR may publish only a source-neutral additive intent:

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

1. `permitSpace` is exactly the missing effective permit space selected for remediation.
2. The intent must not contain provider-native rule/object syntax.
3. The intent must not contain an automatic removal/narrowing operation.
4. The base configured correlation must be sufficient for downstream stale-base/precondition protection.
5. Verification must establish, for the supported slice, that the proposed semantic intent covers the selected missing permit space without narrowing previously configured effective permit space.
6. Provider rendering may choose a representation only if it preserves the verified semantic intent.
7. Renderer failure or inability to prove semantic equivalence produces no executable artifact.
8. NEO execution authority and mutation lifecycle remain separate from APR semantic verification.

## Explicit deferrals

- automatic cleanup of excess configured access;
- whole-ACL or managed-subscope ownership;
- generalized Add/Remove/Replace provider rule-edit vocabulary;
- provider-specific representation strategy;
- configuration optimization/compaction;
- durable editable remediation-plan lifecycle;
- generalized Prefix-aware NEP/RPM materialization.

## G1 result

`G1 PASS` for the first exact-comparison plus additive-remediation MVP slice.

No implementation authorization is implied.
