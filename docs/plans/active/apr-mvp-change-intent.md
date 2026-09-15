# APR MVP change-intent decision

Status: `active S1 MVP remediation-boundary decision`.

Date: 2026-09-15.

## Goal

Decide the smallest safe product behavior needed to continue from an exact APR semantic delta to one verified source-neutral change intent without claiming authority over unrelated configured access.

## Accepted baseline

For one complete comparison scope:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

APR now distinguishes:

- `Realized` when missing and excess are both empty;
- `Drift` when either is non-empty;
- `Uncomparable` when exact comparison cannot be established.

The comparison scope is `firewallId + accessListName`.

## Current product gap

The target model does not currently define a managed/authoritative sub-scope proving that NAPMS owns every configured permit in an ACL.

Therefore `excess` means "configured effective permit not explained by current required policy" but does not yet prove "NAPMS is authorized to remove this permit".

The old runtime `ManagedReconciliationScope` is migration evidence and is not accepted target truth.

## Minimal MVP candidate — owner decision required

```text
Realized
    -> no change intent

Drift with missing permit space
    -> APR may create a source-neutral intent to ENSURE the missing permit space

Excess permit space
    -> report as drift/audit evidence only
    -> do not create automatic removal intent in MVP

Uncomparable
    -> no change intent
```

This gives the first end-to-end happy path a safe additive remediation without pretending that the whole ACL is NAPMS-owned.

A later feature may generate removal/narrowing intents only after an accepted product rule defines the managed policy scope/authority and proves which configured access NAPMS is allowed to remove.

## Why this is an S1 decision

Whether `excess` is merely evidence or an automatic removal target changes observable product behavior and operational risk. Tactical DDD must not infer whole-ACL ownership from the fact that APR can mathematically calculate `excess`.

## Exit criteria

- owner accepts the additive-only MVP rule, or accepts another explicit remediation authority rule;
- accepted behavior is promoted into canonical APR requirements/domain documentation;
- minimal `VerifiedChangeIntent` semantics can then be defined without provider-native rule editing;
- no implementation authorization is implied.

## Next

Obtain the owner decision on the candidate above. If accepted, define the minimum `VerifiedChangeIntent` as "ensure missing effective permit space" and continue to provider rendering / NEO handoff.
