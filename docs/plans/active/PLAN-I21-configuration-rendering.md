# PLAN — I21 Configuration Rendering

Status: `selected; domain re-entry first`.

## Goal

Translate accepted vendor-neutral `DesiredEnforcementIntent` into a target-specific configuration representation while preserving the exact desired traffic semantics and provenance established by Access Policy Realization.

## Input baseline

I20 provides derived-on-demand desired enforcement intent with:
- `EnforcementTarget = Logical Firewall + Enforcement Attachment`;
- normalized technical region fragments;
- Access Rule and Domain Interaction provenance;
- placement provenance;
- fail-closed derivation when material realization knowledge is incomplete.

I21 consumes this accepted output. It does not recompute authorization, domain resolution, placement or reconciliation.

## P0 unknowns to resolve before implementation

1. **Semantic ownership.** Decide whether rendering is a downstream capability inside Access Policy Realization or evidence requires a distinct Bounded Context. A renderer class/module alone is not evidence for a new context.
2. **First concrete target.** Select one target/vendor representation from actual product need. Do not invent a production vendor contract merely to exercise the architecture.
3. **Rendered artifact identity/lifecycle.** Decide whether a render is a value/result derived on demand or a durable artifact with independent identity/version/lifecycle.
4. **Equivalence contract.** Define the normalized semantic projection used to prove that rendered configuration neither broadens nor narrows each desired technical region.
5. **Representation constraints.** Establish accepted behavior for target limits, grouping, ordering, object naming/reuse and unsupported constructs.
6. **Failure semantics.** Define fail-closed outcomes for unsupported/unrepresentable intent and partial rendering; no executable-looking artifact may be emitted as if complete when equivalence is unproven.
7. **Provenance boundary.** Define the minimum provenance carried from desired intent through rendered output so I22 can execute/audit without reconstructing semantic ownership.

## Guardrails

- Rendering is downstream of I20 vendor-neutral realization semantics.
- Target grouping/order/object identity is technical representation and does not redefine Access Rule, Domain Interaction, Logical Firewall or Enforcement Attachment identity.
- No provider/device acquisition or mutation enters I21; those belong to I22.
- No target-specific apply/remove/retry/rollback semantics enter I21 except representation mechanics strictly required to express the artifact.
- No cross-context SQL or ownership shortcuts.
- Unsupported target semantics fail closed rather than approximating traffic.

## Execution stages

### S1 — Domain/requirements/architecture re-entry

Read the smallest canonical set for Access Policy Realization and I21. Classify each P0 item as accepted / hypothesis / unknown / conflict. Resolve material unknowns through the repository decision protocol. Update the highest owning canonical artifacts first.

Exit: rendering ownership, first target, artifact semantics, equivalence and failure/provenance contracts are accepted.

### S2 — Framework-free contracts and core

Implement only the accepted semantic core:
- consumer-facing render use case/port;
- target-independent render request/result vocabulary where justified;
- concrete target renderer behind the port;
- explicit unsupported/unrepresentable result;
- deterministic output for identical semantic input and renderer contract/version.

Exit: core tests prove deterministic rendering and fail-closed unsupported behavior without infrastructure or execution.

### S3 — Semantics-equivalence proof

Add an independent semantic projection/parser for the selected rendered representation where feasible; compare its normalized meaning with the I20 desired technical regions. The proof must detect broadening, narrowing and omitted intent.

Exit: positive and adversarial tests establish exact semantic equivalence for the supported first slice.

### S4 — Provenance/composition proof

Compose I20 desired-policy derivation into I21 rendering through owner-preserving application adapters. Carry accepted target, intent and renderer provenance into the result. Persistence is added only if S1 establishes an independent durable lifecycle.

Exit: one executable integration proof derives desired intent and renders it without Access Rule/Decision/TAE/NEP side effects.

### S5 — Final gate and absorption

Run applicable repository checks and hosted final PR gate. Absorb durable outcomes into canonical domain/requirements/architecture/engineering artifacts, remove this completed PLAN, update the active capsule, mark I21 complete in the roadmap and promote I22 without selecting it.

## Explicitly out of scope

- device/provider login, fetch, apply or post-check;
- retry, rollback, idempotent mutation or concurrency control;
- production credentials/secrets;
- multi-vendor abstraction beyond evidence from the first concrete target;
- operator UI unless an accepted I21 requirement specifically needs a render preview.

## Immediate next action

Execute S1. Do not start renderer code until the first concrete target and equivalence/failure contracts are accepted.