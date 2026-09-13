# Architecture stage

## Purpose

Use this protocol for lifecycle stage `S3 Architecture` when accepted requirements/domain guarantees must be realized through system structure, boundaries and technical mechanisms.

S3 answers:

> How will the accepted semantics be realized while preserving ownership, dependency direction, consistency, security and operational constraints?

Architecture may choose mechanisms. It must not invent product behavior or redefine domain ownership.

Load this protocol only while S3 design or G3 evaluation is active.

## Inputs

Use the smallest applicable set of:

- G1/G2 accepted guarantees for the affected scope;
- current architecture/ADR owners relevant to the change;
- existing implementation structure only as current-state evidence;
- explicit constraints from security, operations, migration or external integration;
- reopened architecture findings from S4/implementation.

Do not preload unrelated architecture documentation or the whole codebase.

## Responsibility boundary

S3 may define:

- application/use-case boundaries;
- ports/adapters and dependency direction;
- consumer/provider contract realization;
- workflow/orchestration placement;
- persistence ownership and repository boundaries;
- transaction/consistency strategy;
- synchronous vs asynchronous interaction mechanism;
- migration/compatibility strategy;
- failure/retry/idempotency mechanism where semantics are already accepted;
- security/authentication/authorization realization preserving accepted authority semantics;
- deployment/process boundaries when technically required;
- observability and operational seams;
- architecture-testable structural constraints.

S3 must not decide merely to unblock implementation:

- missing product behavior;
- new domain identity/lifecycle/invariant;
- Bounded Context responsibility transfer;
- cross-context semantic meaning not accepted in S2;
- authority/business policy not already owned upstream.

If an architecture choice requires such a decision, use `REOPEN(S1)` or `REOPEN(S2)`.

## Architecture working loop

For the affected change:

1. **Restate accepted guarantees.** Identify the specific S1/S2 guarantees Architecture must preserve.
2. **Map current realization.** Inspect only the affected packages/contracts/data paths; distinguish current implementation from target architecture.
3. **Choose responsibility placement.** Map each technical responsibility to context/workflow/platform ownership without moving semantic ownership implicitly.
4. **Define dependency direction.** Identify inbound use cases, consumer-owned ports, provider adapters and composition/wiring.
5. **Define data ownership.** State which context owns writes, authoritative persistence and permitted read projections; reject peer-private persistence access.
6. **Define consistency/transaction semantics.** Choose transaction boundaries, snapshots, sequencing or eventual consistency that satisfy accepted guarantees.
7. **Define failure/unknown behavior realization.** Preserve upstream fail-closed/open, timeout, retry, unknown and provenance semantics rather than inventing them.
8. **Define migration/compatibility path.** When current and target differ, state temporary compatibility constraints and the removal condition; avoid permanent transitional ownership buckets.
9. **Challenge unnecessary complexity.** Prefer local/in-process/simple mechanisms unless distribution, messaging, caching or abstraction has demonstrated pressure.
10. **Challenge semantic leakage.** If architecture must understand or decide peer-private domain semantics, reopen S2 rather than widening interfaces.
11. **Make mechanical rules executable where useful.** Add/update architecture tests for stable structural invariants rather than relying only on prose.
12. **Review the proposed architecture.** Use `architecture-review` for an independent P0-P3 challenge before G3 when the increment is material.
13. **Update the smallest canonical architecture/ADR owner first** and evaluate G3.

## Architecture coherence checks

For the affected scope verify:

- every technical responsibility has one clear owner;
- dependencies point toward accepted semantic owners;
- cross-context interaction uses explicit semantic/application contracts, not peer domain imports;
- workflows/orchestration own no authoritative business truth;
- persistence ownership cannot be bypassed by convenience reads/writes;
- transaction/consistency choices are sufficient for accepted invariants without creating stronger guarantees accidentally;
- security/authority/provenance are preserved end-to-end;
- unknown/failure/temporal semantics survive adapter and persistence boundaries;
- migration does not silently preserve obsolete semantic ownership;
- infrastructure/distribution/abstraction exists only where required;
- architecture choices are separable from product/domain truth.

## G3 — Architecture fit

`G3 PASS` means Implementation Readiness may rely on these guarantees for the affected scope:

- accepted S1/S2 semantics have a feasible target realization;
- responsibility placement and dependency direction are explicit;
- cross-context contracts and adapter boundaries are sufficient;
- persistence/data ownership and consistency strategy are explicit where material;
- security/authority/failure/temporal constraints are preserved;
- migration/compatibility constraints are known where current implementation differs;
- no unresolved P0/P1 architecture contradiction remains;
- implementation need not invent architecture or upstream semantics.

### G3 outcomes

- `PASS` — mark S3 accepted and proceed to S4/next dirty stage.
- `REWORK` — architecture owns the deficiency; revise the affected realization design.
- `REOPEN(S2)` — architecture exposed missing/wrong semantic ownership, identity, invariant or cross-context contract.
- `REOPEN(S1)` — required observable behavior/quality/authority expectation is unsettled.
- `REOPEN(S0)` — the underlying problem/evidence premise is invalid.
- `BLOCKED` — a required external technical constraint/evidence/decision is unavailable.

## Mixed-level artifacts

Existing domain/requirements/code artifacts may contain architecture choices, and architecture documents may contain stale semantic claims. File location does not make a statement authoritative.

During revalidation:

1. classify the statement by meaning;
2. keep product/domain truth with S1/S2 owners;
3. keep realization choices with architecture/engineering owners;
4. treat current code as evidence, not target architecture by default;
5. avoid mass-cleanup unrelated to the active change.

## Context contract

Normal S3 startup:

```text
root AGENTS.md
-> active resume capsule
-> scoped AGENTS.md if applicable
-> this protocol for S3/G3
-> smallest relevant architecture/ADR artifact(s)
-> accepted S1/S2 guarantees for affected scope
-> architecture-review Skill only when reviewing a material proposal
-> code/tests only on demonstrated need
```

Do not preload full domain/requirements families or all architecture documents.

## Relationship to other protocols/Skills

- `change-lifecycle.md` owns stage transitions/reopen/dirty/no-progress semantics.
- `requirements-stage.md` owns S1 guarantees.
- `domain-design-stage.md` owns S2 guarantees.
- `architecture-review` is a review Skill used inside S3; it does not own stage progression or accepted architecture truth.
- `working-loop.md` owns execution/checkpoint/rollover mechanics.
- S4 Implementation Readiness owns exact code-impact/slicing after G3.
