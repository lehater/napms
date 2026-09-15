# Active execution

Current: `access-policy-realization-mvp.md`
Goal: continue the thin MVP vertical path from accepted AG/AP/RPM semantics into one exact source-neutral required-vs-configured comparison result.
Current task: converge the minimum APR comparison result for one complete `firewallId + accessListName` scope.
Lifecycle stage: `S2`
Stage state: `IN_PROGRESS`
Lifecycle basis: accepted Access Governance G1 behavior, revalidated AG/AP Tactical checkpoints, ADR-020 RPM composition and the aligned RPM -> APR input contract.
Implementation authorization: `none`
Authorized scope: `none`
Authorization basis: `none`

## MVP execution rule

Build the smallest working end-to-end happy path, not a feature-complete domain model. Define only semantics required by that path; preserve stable context boundaries, identities and public contracts; defer revisions, richer lifecycle/state machines, migration machinery, optimization and edge-case semantics until concrete pressure appears. Prefer a thin vertical path across contexts over completing each context in depth first.

Current progression:

```text
ACC + RC -> AD
        -> AG bilateral authorization
        -> AP current semantic Policy Rule
        -> RPM TargetRequiredPolicy
        -> APR exact semantic comparison
```

## Completed checkpoint

The first RPM vertical composition is explicit:

- current authorized AP Policy Rule + immutable ACC traffic + AD placements + RC realization + NEP candidates/locators;
- complete `TargetRequiredPolicy[]` grouped by `firewallId + accessListName`, or explicit unresolved;
- multiple NEP candidates/locators are preserved rather than arbitrarily selected;
- missing target/locator/placement/address evidence is unresolved, not empty policy;
- Prefix is never expanded into hosts; the first NEP/RPM happy path is HostAddress-to-HostAddress and Prefix currently yields unresolved until that affected edge is explicitly widened.

## Working set

Read first:

- `docs/plans/active/access-policy-realization-mvp.md`
- `docs/domain/access-policy-realization/README.md`
- `docs/decisions/ADR-020-required-policy-materialization-is-derived-composition.md`
- `docs/decisions/ADR-021-provider-policy-interpretation-and-rendering-boundaries.md`

Expand only when a concrete APR comparison invariant requires it.

## Current baseline

```text
TargetRequiredPolicy
    comparisonScope = firewallId + accessListName
    requiredPermitSpace

ConfiguredEffectivePolicySnapshot
    same comparisonScope
    effectivePermitSpace
    completeness = Complete
        |
        v
APR
    common  = required ∩ configured
    missing = required - configured
    excess  = configured - required
```

Unresolved/incomplete/mismatched inputs are not drift and cannot be compared as though empty.

## Gate

No current upstream ownership or S1 product blocker prevents the first APR comparison happy path.

The current work is semantic/Tactical only. No implementation authorization exists.

## Next

Define the minimum APR assessment/result that distinguishes exact realization, semantic drift and unresolved/uncomparable input without solving provider rendering or execution yet.
