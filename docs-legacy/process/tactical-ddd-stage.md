# Tactical DDD stage

## Purpose

Use this protocol only when S2 Domain Design is routed to Tactical DDD inside an accepted Bounded Context boundary.

Tactical DDD answers:

> Which semantic identities, lifecycles, invariants and domain operations must this context own so its current responsibilities and requirements remain coherent?

It does not design persistence schemas, framework objects, transport DTOs or code packages.

## Inputs

Load only:

- G1-accepted behavior for the affected scope;
- the accepted Strategic responsibility/boundary when material;
- the current tactical model for the affected concept;
- a current reopen finding when Architecture/Implementation exposed a semantic gap;
- additional evidence only when needed for that question.

Classes, tables, ORM mappings and API shapes are realization evidence, not automatic domain truth.

## What Tactical DDD owns

- semantic identity and sameness;
- entity/value-object distinction where semantically meaningful;
- aggregate/invariant ownership;
- lifecycle/state transitions;
- domain operations/decisions/facts;
- semantic uniqueness/idempotency;
- current vs historical state when that distinction is domain-significant;
- derived semantic values when their meaning belongs to the domain contract.

It does not own table/index shape, ORM mapping, database-specific strategy, transport shape, adapter/vendor representation, scheduling/retry mechanics or package/class decomposition unless the mechanism itself changes domain meaning.

## Working loop

1. State the identity/lifecycle/invariant question without starting from a class/table proposal.
2. Confirm the current context owns the fact/decision. If not, reroute the affected question to Strategic DDD inside S2.
3. Confirm the accepted behavior requiring the concept; `REOPEN(S1)` when product behavior is unsettled.
4. Define semantic identity/sameness and distinguish semantic IDs from technical IDs.
5. Define only lifecycle states/transitions that change domain meaning.
6. Define each invariant and its single semantic owner; aggregate boundaries follow invariants, not storage convenience.
7. Classify authoritative state, source-reported facts, derived semantic results and rebuildable implementation projections.
8. Define domain operations/facts in domain language.
9. Remove implementation-shaped statements whose mechanism can change without changing meaning; route them to S3/S4.
10. Remove entities/state machines/commands without independent identity, lifecycle or invariant responsibility.
11. Update the smallest current domain owner and evaluate coherence.

## Coherence checks

For the affected scope:

- material identity has an explicit sameness rule;
- lifecycle/state distinctions are semantic rather than technical;
- each invariant has one owner and feasible semantic consistency boundary;
- value objects do not gain false independent identity;
- source evidence is not promoted to authoritative domain truth without a domain rule;
- derived values are classified appropriately;
- operations do not depend on peer-context private models;
- row IDs, versions and cache keys are not mistaken for semantic identity;
- no unnecessary architecture is frozen into domain truth.

## Tactical gate

Tactical work is coherent when required identity/lifecycle/invariant ownership is explicit, aggregate/entity/value-object distinctions are semantically justified, operations preserve invariants, authoritative/source/derived state is clear enough for Architecture, and no P0/P1 tactical contradiction remains.

Outcomes:

- `PASS` — return to `domain-design-stage.md` for G2;
- `REWORK` — correct the affected tactical delta;
- `REROUTE Strategic DDD` — ownership/boundary/public contract is the real problem;
- `REOPEN(S1)` or `REOPEN(S0)` — upstream product/problem truth is insufficient;
- `BLOCKED` — required semantic/business evidence or decision is unavailable.

Strategic/Tactical switching is internal to S2, not a top-level lifecycle reopen.

## Current-artifact rule

When a tactical artifact contains mixed implementation detail, keep only current semantic guarantees in the domain owner and route currently relevant realization decisions to S3/S4. Do not keep supersession notes, historical alternatives or decision archives in the tactical document.

Load this protocol only for active Tactical work; do not preload Strategic convergence when the context boundary is not under question.
