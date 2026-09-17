# Network Environment Operations requirements

Status: `G1 target execution behavior retained; TargetPolicyArtifact boundary aligned 2026-09-15`.

Date: 2026-09-15.

## Purpose

Define controlled provider/device-facing execution semantics downstream of an accepted rendered configuration artifact.

The current product environment has no real Cisco lab. Therefore the first executable transport is a deterministic in-process stub. It exists to prove operation semantics, failure handling, idempotency, concurrency and audit boundaries. It is not evidence that NAPMS can connect to or configure a real Cisco device.

## Input

NEO consumes a `TargetPolicyArtifact` produced by an accepted Provider Policy Renderer boundary plus execution context:

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

`artifactContent` may be bytes/text/provider-specific payload. Its exact encoding is not NEO domain meaning.

NEO must not recompute authorization, desired policy, placement, APR change design or provider rendering. It must not reinterpret or modify the supplied artifact for device convenience.

## Authority

Executing network mutation requires an explicit action-specific authority admission through Authority Management. Read/acquisition authority does not imply mutation authority. Unknown or denied mutation authority fails closed before apply.

The exact mapping from target to mutation authority scope is an upstream authority contract and is not inferred by NEO from Resource ownership/contact metadata.

## Operation identity and idempotency

`operationId` identifies one intended mutation attempt lifecycle.

For the same operation id:
- identical target + artifact digest is idempotent and must not perform the mutation twice;
- a different target or artifact digest is a conflict and must fail closed;
- retry after an uncertain transport outcome may only continue through an accepted reconciliation/readback path; it must not blindly repeat mutation.

## Pre-check

Before apply, NEO acquires current target state and revision.

Apply is allowed only when:
- acquisition succeeded;
- the state is complete enough for the selected adapter contract;
- the artifact/base target correlation is still valid for the current target;
- an expected revision, when supplied, matches the acquired revision;
- no already-known operation conflict exists.

Stale base correlation, stale revision or ambiguous/unavailable pre-state produces a non-applied result.

## Apply outcome

Transport/apply outcome is explicitly one of:
- `Applied` — adapter confirms the mutation command was accepted;
- `Rejected` — adapter confirms no mutation was accepted;
- `Unknown` — adapter cannot establish whether mutation occurred, for example timeout after submission.

`Applied` is not equivalent to verified desired state.

## Post-check

After `Applied`, NEO reacquires target state. Successful operation completion requires post-state correspondence according to the selected execution adapter contract.

Outcome is:
- `Verified` — applied and immediate post-check proves the target state corresponds to the requested artifact under the adapter contract;
- `Drift` — post-check is complete and proves the target differs;
- `Unknown` — post-check cannot establish correctness;
- `Rejected` — mutation definitely not accepted;
- `PreconditionFailed` — mutation was not attempted because pre-check failed.

`Verified` is execution/artifact verification, not final semantic convergence proof. Final convergence remains a later provider observation/interpreter publication and APR comparison against `TargetRequiredPolicy`.

## Concurrency

The acquired pre-state revision/token plus artifact base correlation form the optimistic-concurrency boundary for the first slice. A conflicting revision/correlation before mutation prevents apply. A revision change after apply is represented by post-check `Drift`/`Unknown` rather than silently treated as success.

## Recovery and rollback

The stub-first slice does not claim generic rollback safety.

- `Rejected` and `PreconditionFailed` need no rollback because no mutation occurred.
- `Unknown` must not trigger automatic blind retry or rollback.
- `Applied` followed by `Drift`/`Unknown` requires reconciliation/operator handling until a target-specific safe recovery contract is accepted.

## Audit/provenance

Every operation result preserves:
- operation id;
- target/comparison scope;
- actor/mutation authority scope;
- renderer identity/version and artifact digest;
- source intent provenance;
- base target correlation;
- pre-state revision and digest when acquired;
- apply outcome/reference;
- post-state revision and digest when acquired;
- final outcome;
- deterministic ordered event/provenance references.

The first slice may keep audit in memory for executable tests. Durable persistence is not claimed until a persistence lifecycle is accepted and implemented.

## Stub scenarios

The deterministic stub must support at least:
- success -> `Verified`;
- explicit rejection;
- timeout/uncertain apply -> `Unknown`;
- stale expected revision/base correlation -> `PreconditionFailed`;
- concurrent change between read and apply -> `PreconditionFailed`;
- post-apply drift -> `Drift`;
- repeated identical operation id -> idempotent same result;
- reused operation id with a different artifact -> conflict/fail-closed.

## Non-goals

- real Cisco SSH/REST/FMC connectivity;
- production credentials/secrets;
- production-grade rollback;
- multi-vendor orchestration platform;
- operator UI;
- semantic reinterpretation of APR intent;
- provider rendering inside NEO;
- claiming lab/device compatibility from stub tests.

## G1 result

The existing NEO execution semantics are sufficient for the first additive MVP vertical path once supplied with an accepted `TargetPolicyArtifact`. No new product behavior is required for this handoff.

No implementation authorization is implied.
