# PLAN — I22 Network Environment Operations

Status: `S1 accepted; S2/S3 stub implementation in progress`.

## Goal

Complete one controlled target operation loop from accepted I21 rendered configuration through provider/device-facing pre-check, apply and post-check to an explicit verified or uncertain execution result, without redefining Access Policy, APR rendering, NEP placement or TAE evidence semantics.

## Inputs

- accepted I21 `RenderedConfiguration` semantics and Cisco ASA renderer contract;
- accepted Enforcement Target identity from APR/NEP;
- user-selected constraint: no real lab is available, so I22 first executable transport is a deterministic in-process stub;
- Authority Management remains owner of mutation eligibility.

## Accepted S1 decisions

1. **Semantic ownership:** Network Environment Operations is a separate semantic module because operation identity/lifecycle, mutation authority, concurrency, failure/recovery and execution audit form a distinct responsibility. It does not own desired policy, placement or rendering semantics.
2. **First transport:** deterministic in-process target stub. It proves execution semantics only and is explicitly not a Cisco integration claim.
3. **Operation identity:** `operation_id` binds exactly one Enforcement Target + artifact digest. Identical retry is idempotent; conflicting reuse fails closed.
4. **Precondition:** acquire current target revision before mutation; optional caller-expected revision and adapter-side conditional apply both fail closed on mismatch.
5. **Apply:** explicit `Applied | PreconditionFailed | Rejected | Unknown`; transport acceptance is not verification.
6. **Final outcome:** `Verified | PreconditionFailed | Rejected | Drift | Unknown`.
7. **Post-check:** `Verified` requires reacquisition proving requested artifact digest is current target state.
8. **Concurrency:** optimistic target revision is the first-slice concurrency token.
9. **Recovery:** Unknown is never blindly retried/rolled back; generic rollback is not claimed in the stub slice.
10. **Audit:** operation result preserves target, actor/scope, artifact digest, pre/apply/post evidence and provenance. First slice uses in-memory repository and does not claim crash-durable audit.
11. **Authority:** mutation admission is an explicit consumer-owned port; read access does not imply mutation authority.

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

Accepted stub-first ownership, operation identity, pre/post-check, outcome, concurrency/recovery, authority and audit contracts.

### S2 — Framework-free operation core

Status: `implemented; final gate pending`.

Implemented:
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

Status: `next`.

Compose existing I20/I21 flow into the deterministic I22 stub. Derive desired policy, render the accepted Cisco ASA artifact, calculate the execution artifact digest, execute it against the target stub and prove `Verified`. Add adversarial integration cases for stale revision, concurrent change and unknown apply outcome without owner-side semantic mutation.

### S5 — Final gate and absorption

Run applicable repository and hosted gates. Absorb durable outcomes into canonical domain/requirements/architecture/engineering artifacts, remove this completed PLAN, update the active capsule, mark I22 complete and promote I23 without selecting it. Squash-merge only after final gates are green.

## Exit criteria

- stub-first domain/requirements/architecture contracts are accepted;
- framework-free operation core has explicit fail-closed outcome semantics;
- deterministic stub proves success/rejection/uncertainty/concurrency/drift/idempotency behavior;
- one integration proof completes desired -> rendered -> stub-applied -> verified;
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

Execute S4 composition proof with the deterministic target stub, then open the I22 PR and use hosted CI as the executable gate.