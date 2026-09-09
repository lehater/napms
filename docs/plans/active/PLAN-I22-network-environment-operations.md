# PLAN — I22 Network Environment Operations

Status: `selected; domain/requirements/architecture re-entry first`.

## Goal

Complete one controlled target operation loop from accepted I21 rendered configuration through provider/device-facing pre-check, apply and post-check to an explicit verified or uncertain execution result, without redefining Access Policy, APR rendering, NEP placement or TAE evidence semantics.

## Input baseline

I21 provides a deterministic, provenance-preserving Cisco Secure Firewall ASA CLI extended ACL representation for its accepted supported subset and independently proves semantic equivalence to desired enforcement intent.

I22 starts downstream of that artifact. It owns no authorization, desired-policy derivation, enforcement placement or rendering meaning.

## P0 unknowns to resolve before mutation code

1. **Semantic ownership.** Decide whether Network Environment Operations is a first-class Bounded Context, an application/operations capability, or another accepted boundary. Device API/CLI code alone is not BC evidence.
2. **First execution transport.** Select the concrete Cisco ASA interaction contract supported by actual product/environment evidence; do not invent SSH/API/FMC mechanics merely to complete the loop.
3. **Operation identity.** Define command/change identity and idempotency key so retry cannot silently duplicate mutation.
4. **Precondition contract.** Define what current-state evidence must match before an I21 render may be applied and how stale/ambiguous state fails closed.
5. **Outcome model.** Define explicit `Applied/Verified`, rejected/not-applied, partial, timeout and unknown outcomes; transport success alone is not semantic success.
6. **Post-check semantics.** Define how post-change state is reacquired and compared with intended rendered/desired semantics, including timing and completeness requirements.
7. **Concurrency.** Define conflict detection for another actor/device change between pre-check and apply/post-check.
8. **Recovery/rollback.** Define when retry is safe, when rollback is representable, and when the only correct result is Unknown requiring operator reconciliation.
9. **Audit/provenance.** Define durable execution evidence: target, renderer contract/artifact reference, pre-state, attempted mutation, device/provider response, post-state, actor/authority where applicable, timestamps and correlation.
10. **Authority boundary.** Determine the action-specific authority required to execute network mutation; read/acquisition authority must not imply mutation authority.

## Guardrails

- No execution result may mutate or redefine Access Rule, Connectivity Decision, NEP, TAE or APR semantic identity.
- Rendering remains I21/APR truth; I22 must not silently rewrite unsupported render semantics.
- Provider/device acquisition and mutation are outer adapters behind consumer-owned ports.
- Unknown/partial outcomes fail closed and remain distinguishable from confirmed absence or success.
- Retry must be tied to accepted operation identity/idempotency semantics.
- No credentials/secrets are committed to the repository.
- No enterprise identity/source work from I23 is pulled forward except the minimum authority contract required by I22 semantics.

## Execution stages

### S1 — Domain/requirements/architecture re-entry

Inspect canonical ownership, Authority Management, APR rendering, TAE evidence and runtime contracts. Classify each P0 item as accepted / hypothesis / unknown / conflict using the repository decision protocol. Update the highest owning canonical artifacts first.

Exit: ownership, first execution transport, operation identity, pre/post-check, outcome, concurrency, recovery and audit contracts are accepted.

### S2 — Framework-free operation core

Implement only accepted operation vocabulary and use cases/ports: operation request/identity, precondition result, mutation result, verification result and durable audit contract where justified.

Exit: core tests prove fail-closed state transitions, idempotency semantics and no infrastructure dependency.

### S3 — First Cisco ASA outer adapter

Implement the selected concrete device/provider acquisition and mutation adapter. Parsing and transport mechanics stay outside Domain/Application. Unsupported or ambiguous device responses map explicitly to Unknown/Partial rather than guessed success.

Exit: adapter contract tests cover acquisition, apply, rejection, timeout/uncertainty and deterministic correlation.

### S4 — Controlled desired -> rendered -> applied -> verified proof

Compose existing I20/I21 owner-preserving flow into I22. Require accepted pre-check, execute one mutation, reacquire post-state and prove semantic satisfaction through the accepted comparison boundary. Persist execution audit only according to S1 ownership/lifecycle decisions.

Exit: one integration proof completes desired -> rendered -> applied -> verified and adversarial proofs cover stale pre-state, concurrent drift and unknown apply outcome.

### S5 — Final gate and absorption

Run applicable repository and hosted gates. Absorb durable outcomes into canonical domain/requirements/architecture/engineering artifacts, remove this completed PLAN, update the active capsule, mark I22 complete and promote I23 without selecting it. Squash-merge only after final gates are green.

## Explicitly out of scope

- broad multi-vendor orchestration/platform abstractions;
- production credential/secret management beyond interfaces needed to keep secrets outside domain/repo;
- enterprise IdP/source replacement from I23;
- production deployment/SLO/DR hardening from I24;
- operator UX beyond an accepted I22 requirement;
- changing I21 Cisco ASA rendering semantics for execution convenience.

## Immediate next action

Execute S1. Do not write device mutation code until the concrete transport and fail-closed operation contracts are accepted.