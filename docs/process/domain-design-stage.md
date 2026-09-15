# Domain Design stage

## Purpose

Use S2 when accepted requirements require domain-semantic modelling or later work exposes a missing/incorrect semantic guarantee.

S2 answers:

> What meanings, responsibilities, boundaries, identities, lifecycles and invariants must exist so current requirements can be realized without invention?

S2 contains two levels:

- **Strategic DDD** — language/responsibility ownership, Bounded Context boundaries and cross-context semantic contracts;
- **Tactical DDD** — identity, lifecycle, invariants, aggregates/entities/value objects and domain operations inside an accepted context boundary.

Enter only the level actually affected.

## Inputs

Load the smallest applicable current set:

- G1-accepted requirements for the affected scope;
- affected current strategic/tactical domain artifacts;
- a current reopen finding from Architecture/Implementation;
- additional evidence only when needed for one semantic question.

Code, schemas and APIs are realization evidence, not automatic domain truth.

## Routing inside S2

Use **Strategic DDD** when responsibility/decision ownership, Bounded Context boundary, authority boundary, language boundary, independent lifecycle/invariant ownership, or a cross-context semantic contract may change.

Use **Tactical DDD** when the context boundary remains stable and the question concerns identity, aggregate/invariant ownership, entity/value-object meaning, lifecycle/state transitions, operations/events or semantic idempotency/uniqueness.

A class, table, API, service, package, framework or deployment unit is not by itself evidence for a Bounded Context change.

A Tactical finding reroutes only the affected edge to Strategic DDD when it exposes insufficient public meaning, duplicated authority or a wrong semantic boundary. Pure delivery, caching, materialization, transport or deployment concerns route to S3 instead.

A Strategic change requires revalidation only of Tactical semantics that depend on that ownership/boundary/contract change.

## Working loop

1. State the semantic question without an implementation answer.
2. Confirm the accepted requirement creating the need; `REOPEN(S1)` if behavior is unsettled.
3. Route to Strategic or Tactical DDD.
4. Resolve material unknown/conflicting claims through `decision-protocol.md`.
5. Update the highest affected current domain owner first.
6. Challenge ownership, identity, lifecycle, invariants and affected cross-context contracts.
7. Revalidate dependent Tactical semantics after any Strategic change.
8. Route pure realization concerns to S3 instead of expanding domain semantics.
9. Evaluate G2.

Use `strategic-ddd-convergence.md` or `tactical-ddd-stage.md` only for the applicable subproblem.

## S2 boundary

S2 does not choose transport/protocol/framework, persistence technology/schema, deployment/process topology, provider adapter mechanics, package/class layout or performance realization unless such a choice changes semantic meaning.

Architecture that requires a semantic change uses `REOPEN(S2)` rather than redefining domain meaning locally.

## G2 — Domain model coherent

`G2 PASS` means S3 may rely on:

- one coherent semantic owner for each material authoritative fact/decision;
- sufficient context boundaries and relationships for the affected behavior;
- explicit public cross-context meaning without peer-private model dependence;
- explicit identity/lifecycle/invariant ownership where material;
- authoritative vs derived/source/current state classified well enough for Architecture;
- no P0/P1 semantic ownership, boundary or coupling contradiction;
- current domain meaning satisfying G1 without importing realization choices.

Outcomes:

- `PASS` — proceed to S3/next dirty stage;
- `REWORK` — S2 owns the semantic deficiency;
- `REOPEN(S1)` — observable product behavior is unsettled;
- `REOPEN(S0)` — the problem/evidence boundary is wrong or contradictory;
- `BLOCKED` — an external semantic/business decision or evidence is required.

## Context rule

Load root/scoped instructions, active capsule when relevant, this routing protocol, the smallest affected domain artifacts and only the applicable Strategic/Tactical protocol. Do not preload the whole model by default.

Accepted semantics live in current `docs/domain/` artifacts. Current blockers live in the active capsule/plan while active. Do not retain exploration, ADR history or parked problem registers after current canonical truth absorbs the result.
