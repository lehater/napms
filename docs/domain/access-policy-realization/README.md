# Access Policy Realization

Status: `S2 MVP Tactical DDD aligned for the first vertical 2026-09-15; future generalization deferred`.

Date: 2026-09-15.

Canonical MVP Tactical model: `tactical-model.md`.

APR remains a separate Bounded Context. It owns source-neutral realization assessment, semantic delta, accepted vendor-neutral change design and semantic verification. It does not own provider-native interpretation/rendering, target selection, authorization or execution.

## Problem statement

For one comparable technical policy target, APR determines how configured effective access realizes required effective access, identifies the exact semantic difference, and may produce a verified vendor-neutral additive change intent for the accepted MVP path.

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

RPM may publish several values for several candidate Firewall/access-list scopes. APR evaluates each scope independently.

RPM `unresolved` is not an empty required policy. Missing placement, Resource realization, target or locator evidence must never be converted into `requiredPermitSpace = []`.

The first MVP path reaches APR only for HostAddress-to-HostAddress technical materialization. Prefix remains upstream truth and causes unresolved until Prefix-aware NEP semantics are accepted.

### ConfiguredEffectivePolicySnapshot

Published by Provider Policy Interpreter (ADR-021):

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

APR does not parse provider-native syntax. Provider ordering, deny/default behavior, objects/groups and aliases must already be interpreted into trustworthy source-neutral effective semantics.

`Incomplete | Unknown` is not empty configured policy.

## Comparability gate

APR performs exact comparison only when:

```text
required.comparisonScope == configured.comparisonScope
required materialization == complete
configured.completeness == Complete
unsupported configured semantics == none for the compared space
```

Otherwise the result is `Uncomparable`, not `Drift` or `Realized`.

## Core semantic algebra

For complete comparable inputs:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

Policies are compared by semantic permit-space meaning, not provider decomposition.

```text
Realized <=> missing is empty AND excess is empty
Drift    <=> missing is non-empty OR excess is non-empty
```

Explicit complete emptiness is valid. Unresolved/unknown evidence is not.

## MVP Tactical classification

The first MVP requires no durable APR aggregate or editable remediation-plan lifecycle.

The canonical Tactical model classifies:

- `ComparisonScope` — value;
- `PermitRegion` / `EffectivePermitSpace` — values;
- `SemanticDelta` — derived value;
- `RealizationAssessment` — derived immutable result;
- `VerifiedChangeIntent` — immutable semantic handoff value.

Their domain meaning is complete without prescribing ERD, tables, caches, workflow state or APIs.

## Accepted remediation boundary

The target has no accepted managed-policy scope proving that NAPMS owns every configured permit in an ACL.

Therefore:

```text
missing -> may produce ENSURE-PERMIT intent
excess  -> report/audit only; no automatic removal or narrowing
Realized -> no intent
Uncomparable -> no intent
```

A future destructive/removal capability requires a separate accepted managed-policy ownership rule.

## VerifiedChangeIntent

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

MVP invariants:

- `permitSpace` is non-empty and equals the selected missing permit space;
- no provider-native syntax is part of the intent;
- no destructive operation exists in the MVP vocabulary;
- base correlation is retained for stale-base protection downstream;
- provenance explains required basis and delta;
- semantic verification proves additive effect without narrowing previously configured access.

For configured space `C` and missing space `M`:

```text
proposed = C ∪ M
M == missing
C ⊆ proposed
required ⊆ proposed
```

If `excess` existed before the additive change, it may remain afterwards. The verified intent therefore does not itself claim final `Realized` convergence. A new provider observation and APR comparison are required.

## Provenance / explainability

APR must preserve enough attribution to explain:

- which required contributors demand a missing region;
- which configured evidence exposes an excess region;
- which basis produced a VerifiedChangeIntent.

Exact provenance storage/index/materialization is downstream Architecture/Implementation work.

## Ownership

APR owns:

- comparability validation;
- exact effective-policy algebra;
- `Realized | Drift | Uncomparable` assessment;
- Semantic Delta;
- accepted additive change design;
- semantic verification;
- source-neutral `VerifiedChangeIntent` handoff.

APR does not own:

- authorization or Policy Rule governance;
- ACC/AD/RC source truth;
- NEP target discovery;
- RPM source composition;
- provider-native interpretation;
- provider-specific rendering;
- network mutation lifecycle.

## Provider / NEO handoff

```text
VerifiedChangeIntent
+ target/provider capabilities
+ base target correlation
    -> Provider Policy Renderer
    -> TargetPolicyArtifact
    -> NEO
```

Rendering may not broaden, narrow or reinterpret verified intent and must fail closed when semantic equivalence cannot be established.

NEO owns operation identity, mutation authority, preconditions/concurrency, apply outcome and execution provenance. Apply success is not convergence proof.

## Scale classification

APR must remain capable of very large policy spaces, but the choice between in-memory, indexed, database-local or other computation is Architecture. It does not create new Tactical entities or ownership.

## Deferred beyond MVP DDD

Future product/domain extensions:

- Prefix-aware/richer address-space algebra;
- destructive/remove/narrow change semantics after managed-policy ownership is accepted;
- durable remediation-plan lifecycle if a real user journey needs saved/editable/scheduled plans;
- richer provider-semantic classes beyond the first supported vocabulary.

Downstream non-DDD work:

- data-local computation/index strategy;
- ERD/table/cache/materialization choices;
- target/current migration mechanics;
- provider round-trip/equivalence mechanism;
- transport DTOs and orchestration.

## MVP Tactical result

The first MVP APR domain is now closed sufficiently for DDD convergence:

```text
complete comparable inputs
    -> exact common/missing/excess
    -> Realized | Drift
    -> if missing != empty: VerifiedChangeIntent(ENSURE-PERMIT)

incomplete/mismatched/unsupported inputs
    -> Uncomparable
    -> no change intent
```

No remaining APR Tactical decision is required by the accepted first MVP happy path. Future generalization is reopened only when a concrete product journey requires it.
