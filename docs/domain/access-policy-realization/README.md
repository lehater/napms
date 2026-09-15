# Access Policy Realization — Problem Statement and Design Directions

Status: `S2 MVP comparison checkpoint aligned; deeper APR Tactical work remains open`.

Date: 2026-09-15.

APR remains a separate Bounded Context. Its final Tactical DDD, ERD, persistence/computation model and migration design are not yet locked.

## Problem statement

For one comparable technical policy target, APR determines how exactly configured effective access realizes required effective access, identifies semantic difference, designs a vendor-neutral policy change, and verifies the proposed resulting semantics before provider rendering/execution.

APR reasons over **source-neutral effective access semantics**, not raw firewall text, native rule identity or rule count.

## Inputs

### TargetRequiredPolicy

Published by Required Policy Materialization (ADR-020) only when materialization for the comparison scope is complete:

```text
TargetRequiredPolicy {
    comparisonScope {
        firewallId
        accessListName
    }
    requiredPermitSpace
    contributingPolicyRuleRefs
    logicalTime
    inputProvenance
    inputFreshness
}
```

`requiredPermitSpace` is the normalized vendor-neutral effective permit semantics derived from current authorized Policy Rules, complete ACC traffic alternatives and current technical realization.

RPM may produce several `TargetRequiredPolicy` values for one governed interaction when NEP reports several relevant Firewalls and/or access-list names. APR evaluates each comparison scope independently; candidate ordering has no route meaning.

RPM `unresolved` is not a `TargetRequiredPolicy` with an empty permit space. APR must not infer an empty required policy from missing placements, Resource realization, target selection, policy locator or other incomplete upstream materialization.

The first MVP vertical path currently reaches APR only for HostAddress-to-HostAddress NEP materialization. Prefix input remains upstream truth but causes RPM unresolved until Prefix-aware NEP query semantics are explicitly designed.

### ConfiguredEffectivePolicySnapshot

Published by a provider interpretation adapter/integration capability (ADR-021):

```text
ConfiguredEffectivePolicySnapshot {
    comparisonScope {
        firewallId
        accessListName
    }
    effectivePermitSpace
    sourceCapture/evidence references
    evidence/effective time
    completeness: Complete | Incomplete | Unknown
    interpreter identity/version
    unsupportedSemantics[]
}
```

The configured snapshot must correlate to the same explicit comparison scope as `TargetRequiredPolicy` before APR performs complete realization algebra.

APR does not parse provider-native policy syntax. Provider ordering, deny/default behavior, objects/groups, aliases and other source-specific constructs must already have been interpreted exactly into the source-neutral projection.

`Incomplete | Unknown` configured input cannot be treated as an empty policy or used for a complete realization conclusion.

TAE may preserve source-qualified evidence but does not own current configured-policy publication/completeness.

## Comparability gate

APR performs semantic comparison only when both inputs are complete and refer to the same comparison scope.

At minimum:

```text
required.comparisonScope == configured.comparisonScope
required materialization == complete
configured.completeness == Complete
unsupported configured semantics == none for the compared space
```

A mismatch, unresolved required materialization, incomplete/unknown configured snapshot or unsupported source semantics is not policy drift; it is an uncomparable realization result.

Exact freshness acceptance thresholds remain downstream Tactical/product work unless a concrete journey requires them. APR must preserve the input freshness/provenance needed to explain the assessment.

## Core semantic algebra

For complete comparable inputs:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

Policies are semantically equivalent when they denote the same effective permit space even when their native decomposition differs.

For the MVP happy path, `requiredPermitSpace` may contain several normalized predicates from one or more contributing Policy Rules; APR reasons over their effective union rather than native rule decomposition.

## MVP comparison result

The current slice needs no independently persisted comparison lifecycle. The result is a derived semantic value for one explicit comparison scope.

```text
APRComparisonResult =
    ComparableAssessment
  | Uncomparable
```

### ComparableAssessment

```text
ComparableAssessment {
    comparisonScope
    status: Realized | Drift
    commonPermitSpace
    missingPermitSpace
    excessPermitSpace
    requiredProvenance
    configuredProvenance
}
```

The status is derived exactly:

```text
Realized <=> missingPermitSpace is empty
              AND excessPermitSpace is empty

Drift    <=> missingPermitSpace is non-empty
              OR excessPermitSpace is non-empty
```

`commonPermitSpace` may legitimately be empty. Empty `configured.effectivePermitSpace` is also legitimate when and only when the configured input is explicitly `Complete`; in that case all required permit space is `missing`.

Likewise, an explicitly complete empty required permit space is distinct from unresolved materialization. If configured permit space is then non-empty, that space is `excess`.

### Uncomparable

```text
Uncomparable {
    comparisonScope?
    reasons[]
    requiredProvenance?
    configuredProvenance?
}
```

Minimum reason classes for the current path:

```text
RequiredMaterializationUnresolved
ComparisonScopeMismatch
ConfiguredIncomplete
ConfiguredUnknown
UnsupportedConfiguredSemantics
```

`Uncomparable` is not `Drift`, not `Realized`, and does not authorize remediation.

## Provenance / explanation invariant

APR must preserve enough attribution to explain where derived regions came from:

- required-side regions retain contributing PolicyRule references/provenance from `TargetRequiredPolicy`;
- configured-side regions retain configured snapshot/evidence provenance;
- a derived `missing` region remains traceable to the required contributors that demand it;
- a derived `excess` region remains traceable to configured evidence that exposes it.

Exact region-level storage/index representation is deferred. The semantic requirement is explainability, not a particular schema.

## APR responsibilities

APR owns:

- comparability validation for its two published inputs;
- exact effective-policy algebra;
- realization assessment;
- exact Semantic Delta;
- vendor-neutral Policy Change Design;
- semantic verification of the proposed resulting effective policy;
- provenance/explainability of derived results;
- a source-neutral `VerifiedChangeIntent` result suitable for downstream provider rendering.

APR does not own:

- authorization or Policy Rule governance;
- Resource/ACC truth;
- NEP target selection/relevance;
- RPM source composition ownership;
- provider-native configured-policy interpretation;
- provider-specific rendering implementation;
- provider/device mutation lifecycle.

## Provider rendering handoff

ADR-021 places provider rendering outside APR core:

```text
VerifiedChangeIntent
+ target/provider capabilities
+ base target revision/correlation
    -> Provider Policy Renderer
    -> TargetPolicyArtifact
    -> NEO
```

Rendering is an adapter/integration capability. It may not widen, narrow or reinterpret verified intent.

A successful rendering path must establish semantic equivalence of the target representation for the supported provider semantics. If equivalence cannot be established, rendering fails closed and NEO receives no executable artifact.

The proof mechanism belongs to Architecture: deterministic construction, round-trip interpretation, provider simulation or another validated mechanism may satisfy the invariant.

## NEO handoff

NEO owns operation identity, mutation authority, concurrency/pre-check, apply outcome and execution provenance for the supplied `TargetPolicyArtifact`. NEO does not rewrite policy semantics.

An apply success is not convergence proof. Subsequent provider state must be collected/interpreted into another `ConfiguredEffectivePolicySnapshot` and compared again.

## Scale direction

APR must support very large policy spaces without mandatory full in-memory hydration. Data-local computation/worksets/indexes may be used behind APR semantic contracts. Such state remains derived unless a future accepted lifecycle establishes independent durable business meaning.

## Stable constraints

- target selection is upstream truth;
- RPM unresolved is not empty required policy;
- comparison scope is explicit `firewallId + accessListName` for the current MVP contract;
- comparison uses effective semantics, not configuration text;
- exact `common/missing/excess` algebra is preserved;
- `Realized`, `Drift` and `Uncomparable` are distinct semantic outcomes;
- assessment, delta, change design and verification remain distinct concepts;
- provider interpretation/rendering fail closed when semantics are unsupported;
- empty evidence is not proof of empty configured policy without explicit completeness;
- APR does not navigate peer-private persistence merely for performance;
- current APR provider-renderer code is migration evidence, not target domain ownership.

## MVP Tactical checkpoint

The first exact comparison slice is now coherent without resolving the whole APR Tactical backlog:

```text
complete comparable inputs
    -> exact common/missing/excess
    -> Realized | Drift

incomplete/mismatched/unsupported inputs
    -> Uncomparable
```

No provider-native syntax, rendering or execution semantics are required to make this comparison result correct.

## Open Tactical DDD work beyond this checkpoint

Still unresolved:

- broader technical-region/value vocabulary and edge cases beyond the first MVP comparison (APR-P03);
- data-local semantic computation contract (APR-P04);
- vendor-neutral change-design vocabulary (APR-P05);
- proposed-change simulation/verification contract (APR-P06);
- richer attribution/explanation storage semantics (APR-P08);
- final APR Tactical DDD/ERD/persistence classification (APR-P09);
- target-versus-current migration plan (APR-P10).

APR-P02 and APR-P07 strategic ownership questions are resolved by ADR-021. RPM/APR input correlation and the minimum exact comparison result for the first HostAddress-based MVP vertical path are now explicit; deeper work is reopened only when the next vertical step requires it.
