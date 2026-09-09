# Network Environment Operations requirements

Status: `accepted I22 stub-first behavior`.

Date: 2026-09-10.

## Purpose

Define controlled provider/device-facing execution semantics downstream of an accepted rendered configuration artifact.

The current product environment has no real Cisco lab. Therefore the first executable I22 transport is a deterministic in-process stub. It exists to prove operation semantics, failure handling, idempotency, concurrency and audit boundaries. It is not evidence that NAPMS can connect to or configure a real Cisco device.

## Input

An execution request contains:
- stable operation id;
- Enforcement Target;
- renderer identity + contract version;
- complete rendered artifact bytes/text;
- artifact digest used for idempotency/correlation;
- actor id and governance/authority scope;
- expected pre-state revision/token when known.

I22 must not recompute authorization, desired policy, placement or rendering.

## Authority

Executing network mutation requires an explicit action-specific authority admission. Read/acquisition authority does not imply mutation authority. Unknown or denied mutation authority fails closed before apply.

## Operation identity and idempotency

`operation_id` identifies one intended mutation attempt lifecycle.

For the same operation id:
- identical target + artifact digest is idempotent and must not perform the mutation twice;
- a different target or artifact digest is a conflict and must fail closed;
- retry after an uncertain transport outcome may only continue through an accepted reconciliation/readback path; it must not blindly repeat mutation.

## Pre-check

Before apply, I22 acquires current target state and revision.

Apply is allowed only when:
- acquisition succeeded;
- the state is complete enough for the selected adapter contract;
- an expected revision, when supplied, matches the acquired revision;
- no already-known operation conflict exists.

Stale revision or ambiguous/unavailable pre-state produces a non-applied result.

## Apply outcome

Transport/apply outcome is explicitly one of:
- `Applied` — adapter confirms the mutation command was accepted;
- `Rejected` — adapter confirms no mutation was accepted;
- `Unknown` — adapter cannot establish whether mutation occurred (for example timeout after submission).

`Applied` is not equivalent to verified desired state.

## Post-check

After `Applied`, I22 reacquires target state. Successful operation completion requires post-state semantic/content equivalence according to the selected execution adapter contract.

Outcome is:
- `Verified` — applied and post-check proves the target state corresponds to the requested artifact;
- `Drift` — post-check is complete and proves the target differs;
- `Unknown` — post-check cannot establish correctness;
- `Rejected` — mutation definitely not accepted;
- `PreconditionFailed` — mutation was not attempted because pre-check failed.

## Concurrency

The acquired pre-state revision/token is the optimistic-concurrency boundary for the first slice. A revision change before mutation is a conflict and no mutation is attempted. A revision change after apply is represented by post-check Drift/Unknown rather than silently treated as success.

## Recovery and rollback

The stub-first slice does not claim generic rollback safety.

- `Rejected` and `PreconditionFailed` need no rollback because no mutation occurred.
- `Unknown` must not trigger automatic blind retry or rollback.
- `Applied` followed by `Drift`/`Unknown` requires reconciliation/operator handling until a target-specific safe recovery contract is accepted.

## Audit/provenance

Every operation result preserves:
- operation id;
- target;
- actor/scope;
- renderer identity/version and artifact digest;
- pre-state revision and digest when acquired;
- apply outcome/reference;
- post-state revision and digest when acquired;
- final outcome;
- deterministic ordered event/provenance references.

The first slice may keep audit in memory for executable tests. Durable persistence is not claimed until a persistence lifecycle is accepted and implemented.

## Stub scenarios

The deterministic stub must support at least:
- success -> Verified;
- explicit rejection;
- timeout/uncertain apply -> Unknown;
- stale expected revision -> PreconditionFailed;
- concurrent change between read and apply -> PreconditionFailed;
- post-apply drift -> Drift;
- repeated identical operation id -> idempotent same result;
- reused operation id with a different artifact -> conflict/fail-closed.

## Non-goals

- real Cisco SSH/REST/FMC connectivity;
- production credentials/secrets;
- production-grade rollback;
- multi-vendor orchestration platform;
- operator UI;
- claiming lab/device compatibility from stub tests.