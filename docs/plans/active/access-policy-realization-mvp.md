# Access Policy Realization MVP slice

Status: `active S2 MVP Tactical convergence`.

Date: 2026-09-15.

## Goal

Define only the APR semantics required for one complete comparison scope to answer whether current configured effective access matches required effective access and, when it does not, what exact source-neutral semantic delta exists.

Do not complete the full APR backlog. The first vertical path stops at the smallest exact `required vs configured` result needed before change design/rendering.

## Accepted inputs

```text
TargetRequiredPolicy {
    comparisonScope = firewallId + accessListName
    requiredPermitSpace
    provenance/freshness
}

ConfiguredEffectivePolicySnapshot {
    same comparisonScope
    effectivePermitSpace
    completeness = Complete
    provenance/freshness
}
```

Incomplete/unresolved inputs are not empty policy and are not drift.

## Current task

For one complete comparable pair:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

Specify the minimum result and invariants needed to distinguish:

- `Realized` — required and configured effective permit spaces are equal;
- `Drift` — at least one of `missing` or `excess` is non-empty;
- `Unresolved/Uncomparable` — inputs are incomplete, mismatched or unsupported and exact comparison cannot be claimed.

Preserve provenance/contributors so each derived region is explainable.

## MVP guardrails

Do not yet design:

- generalized provider-specific rule editing;
- full APR region optimization vocabulary;
- data-local scaling architecture;
- provider rendering;
- mutation/execution workflow;
- persistence/ORM/API schemas;
- broad remediation strategy beyond the exact semantic delta.

## Exit criteria

- comparison-scope equality/completeness gate is explicit;
- `common/missing/excess` algebra is exact and source-neutral;
- `Realized`, `Drift`, and `Unresolved/Uncomparable` cannot be confused;
- an empty configured policy is accepted only when completeness explicitly proves it is empty;
- provenance remains sufficient for explanation;
- no provider-native syntax enters APR core;
- no implementation authorization is implied.

## Working set

- `docs/domain/access-policy-realization/README.md`
- `docs/decisions/ADR-020-required-policy-materialization-is-derived-composition.md`
- `docs/decisions/ADR-021-provider-policy-interpretation-and-rendering-boundaries.md`
- provider interpretation contract only as needed to validate completeness/comparability

## Next

Converge the minimum APR comparison result for one target. Only after that decide whether the next MVP step needs a minimal `VerifiedChangeIntent` path or can stop at realization assessment for the current journey.
