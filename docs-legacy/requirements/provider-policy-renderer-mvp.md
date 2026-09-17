# Provider Policy Renderer — MVP contract

Status: `G1/S2 boundary contract accepted for additive MVP path`.

Date: 2026-09-15.

Decision basis: `docs/decisions/ADR-021-provider-policy-interpretation-and-rendering-boundaries.md`.

## Purpose

Translate one verified source-neutral APR change intent into one provider/target-specific artifact without changing the semantic meaning of that intent.

Provider Policy Renderer is an integration capability, not a Bounded Context and not an owner of policy authorization or remediation semantics.

## Input

For the first MVP path:

```text
VerifiedChangeIntent {
    comparisonScope {
        firewallId
        accessListName
    }
    operation = ENSURE-PERMIT
    permitSpace
    baseConfiguredCorrelation
    requiredPolicyProvenance
    deltaProvenance
    verificationEvidence
}

+ TargetProviderCapabilities
+ base target revision/correlation
```

The renderer does not receive an instruction to remove/narrow `excess` in the MVP.

## Output

On success:

```text
TargetPolicyArtifact {
    targetRef
    comparisonScope
    baseTargetCorrelation
    rendererIdentity
    rendererVersion
    artifactContent
    artifactDigest
    semanticEquivalenceEvidence
    intentProvenance
}
```

Exact transport encoding and provider command format are Architecture/Implementation concerns.

## Invariants

1. Rendering may not broaden, narrow or reinterpret the `VerifiedChangeIntent`.
2. The renderer may choose only a representation supported by the target/provider capabilities.
3. A successful result must establish semantic equivalence between the produced target representation and the verified intent for the supported slice.
4. If required provider semantics are unsupported or equivalence cannot be established, rendering fails closed and no `TargetPolicyArtifact` is published.
5. Provider-native rule/object/order syntax belongs only to the renderer/adapter representation boundary.
6. `artifactDigest` identifies the exact rendered payload supplied to NEO for idempotency/correlation; it is not policy-semantic identity.
7. `baseTargetCorrelation` must be preserved so NEO can reject stale/concurrent mutation attempts.
8. Renderer identity/version and source intent provenance remain explainable downstream.
9. Rendering success does not authorize execution; NEO independently checks mutation authority.
10. Rendering success does not prove post-apply convergence; subsequent provider observation/interpreter/APR comparison remains authoritative for convergence.

## MVP scope

The first vertical path requires only exact representation of additive `ENSURE-PERMIT` intent for a supported provider/target adapter.

No target-neutral generalized rule-edit language beyond the verified semantic permit intent is required.

## Explicit deferrals

- automatic removal/narrowing of excess access;
- whole-ACL replacement;
- provider representation optimization/compaction choices beyond exact semantic preservation;
- provider capability negotiation UI;
- generic rollback generation;
- multi-target transaction/orchestration;
- renderer persistence or lifecycle identity.

## Result

The boundary is sufficient to hand one verified additive intent to NEO without moving APR semantics into provider-specific code or moving provider rendering into NEO.

No implementation authorization is implied.
