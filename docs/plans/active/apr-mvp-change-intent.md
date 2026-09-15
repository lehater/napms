# APR MVP change-intent decision

Status: `S1 MVP remediation boundary accepted`.

Date: 2026-09-15.

## Goal

Define the smallest safe product behavior needed to continue from an exact APR semantic delta to one verified source-neutral change intent without claiming authority over unrelated configured access.

## Accepted baseline

For one complete comparison scope:

```text
common  = required ∩ configured
missing = required - configured
excess  = configured - required
```

APR distinguishes:

- `Realized` when missing and excess are both empty;
- `Drift` when either is non-empty;
- `Uncomparable` when exact comparison cannot be established.

The comparison scope is `firewallId + accessListName`.

## Accepted MVP remediation boundary

The target model does not currently define a managed/authoritative sub-scope proving that NAPMS owns every configured permit in an ACL.

Therefore the first MVP remediation behavior is intentionally additive-only:

```text
Realized
    -> no change intent

Drift with missing permit space
    -> APR may create a source-neutral ENSURE-PERMIT intent for the missing permit space

Excess permit space
    -> report as drift/audit evidence only
    -> no automatic removal/narrowing intent in MVP

Uncomparable
    -> no change intent
```

`excess` means configured effective permit not explained by current required policy. It does not prove that NAPMS is authorized to remove that permit.

The old runtime `ManagedReconciliationScope` remains migration evidence and is not accepted target truth.

A later removal/narrowing feature requires an explicit accepted managed-policy scope/authority rule that proves which configured access NAPMS may remove.

## Consequences for change design

The minimum MVP `VerifiedChangeIntent` may express only the semantic operation:

```text
ENSURE-PERMIT(missingPermitSpace)
```

It must retain:

- comparison scope;
- base configured snapshot/revision correlation required for safe application;
- semantic permit space to ensure;
- provenance back to required policy and semantic delta;
- verification evidence proving that the intent does not narrow existing effective access and that applying it would cover the intended missing permit space for the supported slice.

Provider-native rule/object edits are not APR domain semantics.

## Deferred

- automatic removal of excess access;
- whole-ACL ownership semantics;
- generalized Add/Remove/Replace rule-edit vocabulary;
- cleanup/optimization of existing rules;
- provider-specific representation strategy.

## Exit result

`S1 PASS` for the additive-only MVP remediation boundary.

The next step is Tactical convergence of the minimal `VerifiedChangeIntent`, provider-renderer handoff and NEO execution boundary. No implementation authorization is implied.
