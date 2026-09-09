# PLAN — I22 Network Environment Operations

Status: `S1-S4 implemented; S5 final gate next`

## Goal

Complete one controlled target operation loop from accepted I21 rendered configuration through provider/device-facing pre-check, apply and post-check to an explicit verified or uncertain execution result, without redefining Access Policy, APR rendering, NEP placement or TAE evidence semantics.

## Inputs

- accepted I21 `RenderedConfiguration` semantics and Cisco ASA renderer contract;
- accepted Enforcement Target identity from APR/NEP, projected at composition into NEO-owned `OperationTarget`;
- user-selected constraint: no real lab is available, so I22 first executable transport is a deterministic in-process stub;
- Authority Management remains owner of mutation eligibility.

## Accepted S1 decisions

1. **Semantic ownership:** Network Environment Operations is a separate semantic module because operation identity/lifecycle, mutation authority, concurrency, failure/recovery and execution audit form a distinct responsibility. It does not own desired policy, placement or rendering semantics.
2. **First transport:** deterministic in-process target stub. It proves execution semantics only and is explicitly not a Cisco integration claim.
3. **Target boundary:** NEO Domain imports no APR domain type. Composition projects APR `EnforcementTarget` identity into NEO-owned `OperationTarget` without redefining the upstream identity.
4. **Operation identity:** `operation_id` binds exactly one Operation Target + artifact digest. Identical retry is idempotent; conflicting reuse fails closed.
5. **Precondition:** acquire current target revision before mutation; optional caller-expected revision and adapter-side conditional apply both fail closed on mismatch.
6. **Apply:** explicit `Applied | PreconditionFailed | Rejected | Unknown`; transport acceptance is not verification.
7. **Final outcome:** `Verified | PreconditionFailed | Rejected | Drift | Unknown`.
8. **Post-check:** `Verified` requires reacquisition proving requested artifact digest is current target state.
9. **Concurrency:** optimistic target revision is the first-slice concurrency token.
10. **Recovery:** Unknown is never blindly retried/rolled back; generic rollback is not claimed in the stub slice.
11. **Audit:** operation result preserves target, actor/scope, artifact digest, pre/apply/post evidence and provenance. First slice uses in-memory repository and does not claim crash-durable audit.
12. **Authority:** mutation admission is an explicit consumer-owned port; read access does not imply mutation authority.

Canonical owners:
- `docs/requirements/network-environment-operations.md`;
- `docs/domain/network-environment-operations/tactical-model.md`;
- `docs/architecture/network-environment-operations-boundary.md`.

## Guardrails

- No execution result may mutate or redefine Access Rule, Connectivity Decision, NEP, TAE or APR semantic identity.
- Rendering remains I21/APR truth; I22 must not silently rewrite unsupported render semantics.
- Provider/device acquisition and mutation are outer adapters behind consumer-owned ports.
- Unknown/partial outcomes fail closed and remain distinguishable from confirmed absence or success.
- Retry is tied to accepted operation identity/idempotency semantics.
- No credentials/secrets are committed to the repository.
- Stub success is not real-device compatibility evidence.

## Execution stages

### S1 — Domain/requirements/architecture re-entry

Status: `done`.

Accepted stub-first ownership, target projection, operation identity, pre/post-check, outcome, concurrency/recovery, authority and audit contracts.

### S2 — Framework-free operation core

Status: `implemented; final gate pending`.

Implemented:
- NEO-owned `OperationTarget` projection value;
- operation command/result value model;
- apply/final outcome vocabulary;
- consumer-owned authority/target/repository ports;
- `ExecuteNetworkOperation` use case;
- fail-closed authority, stale revision, concurrent revision, rejection, uncertain apply and post-check drift handling;
- operation-id idempotency/conflict semantics.

### S3 — Deterministic target stub

Status: `implemented; final gate pending`.

Implemented:
- in-memory operation repository;
- allow/deny deterministic authority adapters for tests;
- deterministic target stub with success/reject/unknown-apply/concurrent-change/post-apply-drift scenarios;
- scenario tests for Verified, PreconditionFailed, Rejected, Unknown, Drift and idempotent retry.

No real Cisco transport is implemented or implied.

### S4 — Controlled desired -> rendered -> applied -> verified proof

Status: `implemented; final gate pending`.

Implemented:
- existing PostgreSQL-backed APR owner composition derives desired enforcement and renders the accepted Cisco ASA artifact;
- composition projects APR `EnforcementTarget` into NEO `OperationTarget`;
- execution artifact digest is calculated from rendered bytes and bound to `operation_id`;
- deterministic target stub proves pre-check -> conditional apply -> post-check -> `Verified`;
- integration proof verifies Access Policy, NEP and TAE owner counts do not change;
- adversarial integration proofs cover Unknown apply with no blind retry and concurrent target change with no false Verified result.

### S5 — Final gate and absorption

Status: `next`.

Open the I22 PR and run hosted gates. On green, absorb durable outcomes into canonical semantic ownership/current architecture/current engineering state/roadmap, remove this completed PLAN, set active execution to none, promote I23 without selecting it and squash-merge.

## Exit criteria

- stub-first domain/requirements/architecture contracts are accepted;
- framework-free operation core has explicit fail-closed outcome semantics;
- deterministic stub proves success/rejection/uncertainty/concurrency/drift/idempotency behavior;
- one integration proof completes desired -> rendered -> stub-applied -> verified;
- NEO Domain has no peer-domain dependency on APR;
- all final hosted gates are green;
- canonical state clearly says no real Cisco lab/transport has been proven.

## Blockers

No real lab is available. This is an accepted product/environment constraint, not a blocker for the stub-first I22 semantic proof. Real Cisco transport remains deferred until a lab/provider contract exists.

## Explicitly out of scope

- real Cisco SSH/REST/FMC connectivity;
- production credential/secret management;
- production-grade rollback;
- multi-vendor orchestration platform;
- enterprise IdP/source replacement from I23;
- production deployment/SLO/DR hardening from I24;
- operator UX beyond an accepted I22 requirement.

## Next

Open the I22 PR, run hosted final gates, resolve failures, then perform S5 absorption and squash merge.