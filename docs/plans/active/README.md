# Active execution

Current: `apr-mvp-change-intent.md`
Goal: continue the thin MVP vertical path from exact APR semantic comparison into one safe source-neutral change intent without claiming authority over unrelated configured access.
Current task: resolve the S1 remediation boundary — whether APR may automatically remove `excess` or MVP is additive-only on `missing`.
Lifecycle stage: `S1`
Stage state: `IN_PROGRESS`
Lifecycle basis: accepted AG/AP/RPM semantics and the completed APR MVP exact-comparison checkpoint.
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
        -> APR common/missing/excess
        -> current S1: safe MVP change-intent boundary
```

## Completed checkpoint

APR comparison for one complete `firewallId + accessListName` scope is now explicit:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

- `Realized` iff missing and excess are empty;
- `Drift` iff either is non-empty;
- `Uncomparable` is distinct from drift and never authorizes remediation;
- complete empty configured policy is valid; incomplete/unknown evidence is not empty;
- required/configured provenance is retained for explanation.

## Current blocker

The target model has no accepted managed-policy scope proving that NAPMS owns every configured permit in an ACL. Therefore APR can calculate `excess`, but automatic removal of that excess is not yet justified.

Current non-authoritative MVP candidate:

```text
missing -> may generate source-neutral ENSURE-PERMIT intent
excess  -> report only; no automatic removal
Realized -> no intent
Uncomparable -> no intent
```

This candidate remains S1 until explicitly accepted by the owner.

## Working set

Read first:

- `docs/plans/active/apr-mvp-change-intent.md`
- `docs/domain/access-policy-realization/README.md`
- `docs/decisions/ADR-021-provider-policy-interpretation-and-rendering-boundaries.md`

Use current runtime `ManagedReconciliationScope` only as migration evidence, not target truth.

## Gate

The exact APR comparison slice is coherent. The next change-design step is blocked only on the product decision above.

No implementation authorization exists.

## Next

Obtain the owner decision on additive-only MVP remediation. If accepted, define the minimal `VerifiedChangeIntent` and continue to provider rendering / NEO handoff.
