# Access Policy Realization — Problem Statement and Design Directions

Status: `active Tactical DDD; strategic provider boundaries resolved by ADR-021`.

Date: 2026-09-14.

APR remains a separate Bounded Context. Its final Tactical DDD, ERD, persistence/computation model and migration design are not yet locked.

## Problem statement

For one comparable technical policy target, APR determines how exactly configured effective access realizes required effective access, identifies semantic difference, designs a vendor-neutral policy change, and verifies the proposed resulting semantics before provider rendering/execution.

APR reasons over **source-neutral effective access semantics**, not raw firewall text, native rule identity or rule count.

## Inputs

### TargetRequiredPolicy

Published by Required Policy Materialization (ADR-020): target/policy correlation + normalized required effective permit space + provenance/time.

### ConfiguredEffectivePolicySnapshot

Published by a provider interpretation adapter/integration capability (ADR-021):

```text
ConfiguredEffectivePolicySnapshot
    targetRef
    policyLocator / comparisonScope
    effectivePermitSpace
    sourceCapture/evidence references
    evidence/effective time
    completeness: Complete | Incomplete | Unknown
    interpreter identity/version
    unsupportedSemantics[]
```

APR does not parse provider-native policy syntax. Provider ordering, deny/default behavior, objects/groups, aliases and other source-specific constructs must already have been interpreted exactly into the source-neutral projection.

`Incomplete | Unknown` configured input cannot be treated as an empty policy or used for a complete realization conclusion.

TAE may preserve source-qualified evidence but does not own current configured-policy publication/completeness.

## Core semantic algebra

For complete comparable inputs:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

Policies are semantically equivalent when they denote the same effective permit space even when their native decomposition differs.

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
- comparison uses effective semantics, not configuration text;
- exact `common/missing/excess` algebra is preserved;
- assessment, delta, change design and verification remain distinct concepts;
- provider interpretation/rendering fail closed when semantics are unsupported;
- empty evidence is not proof of empty configured policy without explicit completeness;
- APR does not navigate peer-private persistence merely for performance;
- current APR provider-renderer code is migration evidence, not target domain ownership.

## Open Tactical DDD work

Still unresolved:

- final technical-region/value vocabulary and edge cases (APR-P03);
- data-local semantic computation contract (APR-P04);
- vendor-neutral change-design vocabulary (APR-P05);
- proposed-change simulation/verification contract (APR-P06);
- attribution/explanation semantics (APR-P08);
- final APR Tactical DDD/ERD/persistence classification (APR-P09);
- target-versus-current migration plan (APR-P10).

APR-P02 and APR-P07 strategic ownership questions are resolved by ADR-021. Architecture details of provider adapters/artifact format remain downstream.
