# Architecture stage

## Purpose

Use S3 when accepted requirements/domain guarantees must be realized through system structure, boundaries and technical mechanisms.

S3 answers:

> How will current accepted semantics be realized while preserving ownership, dependency direction, consistency, security and operational constraints?

Architecture may choose mechanisms. It does not invent product behavior or redefine domain ownership.

## Inputs

Load only:

- G1/G2 guarantees for the affected scope;
- current architecture owners relevant to the change;
- current implementation structure as realization evidence when needed;
- current security/operations/external-integration constraints;
- a current reopen finding from S4/implementation.

## What S3 owns

S3 may define:

- application/use-case boundaries and orchestration placement;
- ports/adapters and dependency direction;
- realization of cross-context contracts;
- persistence ownership/repository boundaries;
- transaction and consistency strategy;
- synchronous/asynchronous mechanisms;
- currently required compatibility/changeover mechanics;
- retry/idempotency/failure mechanisms preserving accepted semantics;
- authentication/authorization realization;
- deployment/process boundaries when technically required;
- observability seams;
- mechanically enforceable architecture rules.

S3 does not choose missing product behavior, new domain identity/lifecycle/invariant, context responsibility transfer or unaccepted authority/business policy. Those use `REOPEN(S1|S2)`.

## Working loop

1. Restate the exact S1/S2 guarantees Architecture must preserve.
2. Inspect only the affected realization path.
3. Place each technical responsibility without moving semantic ownership implicitly.
4. Define dependency direction, ports, adapters and composition.
5. Define authoritative persistence ownership and forbid peer-private reads/writes.
6. Define consistency/transaction/snapshot/sequencing behavior sufficient for accepted invariants.
7. Preserve accepted failure, unknown, timeout, retry, temporal and provenance semantics through adapters/persistence.
8. When the current runtime differs from the target, define only the temporary compatibility mechanism needed for the selected change and its removal condition; do not create permanent transitional ownership.
9. Prefer local/in-process/simple mechanisms unless distribution, messaging, caching or abstraction has demonstrated pressure.
10. If realization requires peer-private semantic knowledge or a new domain decision, reopen S2 instead of widening the interface.
11. Make stable structural constraints executable with architecture tests where practical.
12. Use `architecture-review` for a material independent P0-P3 challenge.
13. Update the smallest current architecture owner and evaluate G3.

## G3 — Architecture fit

`G3 PASS` means S4 may rely on:

- feasible realization of current S1/S2 semantics;
- explicit responsibility placement and dependency direction;
- sufficient cross-context/application/adapter contracts;
- explicit persistence/data ownership and consistency strategy where material;
- preserved security/authority/failure/temporal semantics;
- current-runtime-to-target compatibility constraints where needed for the selected change;
- no unresolved P0/P1 architecture contradiction;
- no architecture decisions left for implementation to invent.

Outcomes:

- `PASS` — proceed to S4/next dirty stage;
- `REWORK` — S3 owns the realization deficiency;
- `REOPEN(S2|S1|S0)` — an upstream semantic/product/problem guarantee is missing or wrong;
- `BLOCKED` — required current external technical evidence/constraint is unavailable.

## Context rule

Load root/scoped instructions, the active capsule when relevant, this protocol while S3/G3 is active, the smallest current architecture artifacts and only the affected S1/S2/code evidence.

Architecture docs contain current target constraints only. Replaced designs and rationale remain in Git history rather than ADR/supersession archives in the working tree.
