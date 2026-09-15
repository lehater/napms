# Network Environment Operations requirements

## Purpose

Define controlled provider/device-facing execution semantics downstream of a rendered `TargetPolicyArtifact`.

## Input

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

ExecutionContext {
    operationId
    actorId
    mutationAuthorityScope
    expectedPreStateRevision?
}
```

Artifact encoding may be provider-specific. NEO does not recompute authorization, required policy, target placement, APR change design or provider rendering, and it does not reinterpret the artifact for transport convenience.

## Authority

Network mutation requires explicit action-specific Authority Management admission. Read/acquisition authority does not imply mutation authority. Denied or unknown authority fails closed before apply.

Target-to-authority-scope mapping is an explicit integration/authority contract and is not inferred from Resource ownership/contact metadata.

## Operation identity and idempotency

`operationId` identifies one intended mutation lifecycle.

- same operation ID + same target/artifact intent is idempotent and does not repeat mutation;
- same operation ID + different target/artifact intent is a conflict and fails closed;
- uncertain transport outcome is not blindly retried.

## Pre-check

Before apply, NEO acquires operation-scoped current target state/revision.

Apply is allowed only when acquisition succeeds, the state is complete enough for the selected execution contract, artifact/base correlation is valid, any expected revision matches, and no operation conflict is known.

Stale correlation/revision or unavailable/ambiguous pre-state prevents mutation.

## Apply outcome

```text
Applied | Rejected | Unknown
```

- `Applied` — the adapter confirms the mutation command was accepted;
- `Rejected` — the adapter confirms no mutation was accepted;
- `Unknown` — the adapter cannot establish whether mutation occurred.

`Applied` is not verified desired state.

## Post-check and final outcome

After definite `Applied`, NEO reacquires operation-scoped target state and verifies correspondence under the selected adapter contract.

```text
Verified | Rejected | PreconditionFailed | Drift | Unknown
```

- `Verified` — immediate post-check proves correspondence to the supplied artifact;
- `Drift` — complete post-check proves a mismatch;
- `Unknown` — correctness cannot be established;
- `Rejected` — no mutation was accepted;
- `PreconditionFailed` — pre-check prevented mutation.

`Verified` is execution/artifact verification, not semantic convergence. Final convergence requires provider observation/interpretation followed by APR comparison against current required policy.

## Concurrency

The acquired pre-state revision/token plus artifact base correlation form the optimistic-concurrency boundary. Conflict before apply prevents mutation. Post-apply change is represented by `Drift` or `Unknown`, not silent success.

## Recovery

- `Rejected` and `PreconditionFailed` require no rollback because mutation was not accepted.
- `Unknown` does not trigger blind retry or rollback.
- `Applied` followed by `Drift` or `Unknown` requires reconciliation/operator handling.

NEO makes no generic rollback-safety claim.

## Provenance

Every operation result preserves enough evidence to correlate operation ID, target/comparison scope, actor and mutation-authority scope, renderer/artifact identity, source intent provenance, base/pre-state correlation, provider apply outcome/reference, post-state observation and final outcome.

Durability requirements follow the selected runtime architecture. Test-only in-memory adapters must not be mistaken for crash-safe operation history.

## Current execution boundary

A deterministic in-process target adapter is valid as a test/proof adapter for success, rejection, uncertain apply, stale/concurrent preconditions, post-apply drift and operation-id idempotency/conflict behavior. Such a test adapter proves NEO orchestration semantics only and makes no claim of compatibility with a real provider/device.

Real provider transport, credentials, rollback and multi-target orchestration are not part of the current NEO product contract unless separately introduced by accepted requirements.
