# Provider Policy Renderer — target contract

Status: `current target`.

## Purpose

Translate one verified source-neutral APR change intent into one provider/target-specific artifact without changing its semantic meaning.

Provider Policy Renderer is an integration capability, not a Bounded Context and not an owner of policy authorization or remediation semantics. It is outside the selected Required Access Matrix implementation MVP.

## Input

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

## Output

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

## Invariants

1. Rendering may not broaden, narrow or reinterpret VerifiedChangeIntent.
2. A successful result establishes semantic equivalence for the supported target/provider capability set.
3. Unsupported semantics or unprovable equivalence fail closed; no artifact is published.
4. Provider-native syntax remains inside the renderer/adapter boundary.
5. `artifactDigest` correlates the exact rendered payload; it is not policy-semantic identity.
6. `baseTargetCorrelation` is preserved for downstream stale/concurrent mutation protection.
7. Renderer identity/version and intent provenance remain explainable.
8. Rendering does not authorize execution and does not prove post-apply convergence.

Current accepted change vocabulary is additive `ENSURE-PERMIT`; no automatic removal/narrowing of excess access is authorized.
