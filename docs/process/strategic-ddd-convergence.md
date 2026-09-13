# Strategic DDD convergence

## Purpose

Use this protocol only when S2 Domain Design has been routed to Strategic DDD.

Its purpose is to converge on coherent semantic ownership and context boundaries by iterating between:

```text
candidate contexts
<-> responsibilities/decisions
<-> context relationships
<-> semantic contracts
<-> boundary challenge
```

The current strategic model is a starting hypothesis to validate, not proof that existing Bounded Context boundaries are correct.

## Inputs

Load only the affected strategic scope:

- accepted requirements that create the semantic need;
- affected context/domain artifacts;
- current context-map/relationship statements when they exist;
- accepted ADRs constraining ownership/boundaries;
- concrete cross-context consumer/provider needs;
- code/persistence only as secondary evidence when a semantic claim cannot otherwise be resolved.

Do not preload every bounded context merely because Strategic DDD is active.

## Context responsibility check

For every affected candidate context, make these explicit enough to challenge:

- purpose;
- authoritative semantic responsibility;
- decisions/facts it owns;
- key identities;
- lifecycle/invariants that justify autonomy;
- language boundary;
- authority/responsibility boundary where material;
- required inputs from other contexts;
- public outputs/semantic facts supplied to others.

Signals of a bad boundary:

- two contexts claim authoritative ownership of the same decision/fact;
- no context owns a required decision/fact;
- one context must understand peer-private entities/state transitions to perform its responsibility;
- contexts cannot change independently because one semantic lifecycle/invariant is artificially split;
- a context exists only because of a table/service/deployment/package boundary.

## Relationship and contract check

For every relationship material to the current change, state:

- purpose of the relationship;
- provider / semantic owner;
- consumer;
- semantic request/input when applicable;
- semantic response/fact/output;
- identity references crossing the boundary;
- temporal semantics (`current`, `asOf`, validity interval, snapshot) where material;
- unknown/absence/error semantics where material;
- provenance/authority expectations where material;
- consumer obligations and forbidden reinterpretation.

The contract is semantic before it is a Python/HTTP/message interface.

Prefer consumer-owned ports for local dependency inversion unless a genuinely shared/provider-published language has been intentionally accepted. Do not create a generic shared business-model package merely to avoid explicit boundaries.

## Boundary challenge

For each affected edge ask:

1. Why does the consumer need this fact?
2. Who has authority to decide/derive it?
3. Can the consumer fulfil its responsibility from the public semantic contract alone?
4. Is the consumer re-deriving an upstream decision from raw upstream internals?
5. Is the provider exporting more internal model than the consumer actually needs?
6. Would moving this responsibility change identity/lifecycle/invariant ownership more coherently?
7. Do time/unknown/provenance semantics make the apparent contract ambiguous?

If the smallest stable contract still requires peer-private model knowledge, challenge the context boundary before expanding the DTO/API.

## Convergence loop

Run only the affected portion of this loop:

1. establish/restate candidate context responsibilities;
2. map affected relationships;
3. describe the semantic contract for each affected edge;
4. boundary-challenge each contract;
5. classify contradictions/gaps P0-P3;
6. change context boundary/ownership/relationship when required;
7. rebuild only contracts affected by that change;
8. repeat until no P0/P1 finding requires another boundary/ownership/contract change.

A later iteration must change evidence, model, problem state or decision state. Otherwise apply the lifecycle no-progress rule and block/escalate rather than looping.

## Strategic convergence gate

Strategic work is converged for the affected scope when:

- authoritative semantic responsibilities have one coherent owner;
- all relationships needed by the current change are explicit;
- each such relationship has a sufficient semantic contract;
- consumers do not require peer-private domain models to perform their responsibility;
- no unresolved P0/P1 ownership/boundary/semantic-cycle contradiction remains;
- relevant identity/time/unknown/provenance semantics are explicit where omission would force downstream invention;
- one full boundary-challenge pass produces no new P0/P1 requiring a strategic-model change.

P2/P3 findings may remain when they do not undermine these guarantees.

## Output

Promote accepted results to the smallest canonical owners:

- strategic model/context documentation for responsibility/boundary changes;
- context-map/relationship documentation for accepted edges;
- semantic contract documentation near the owner/consumer as appropriate;
- ADR only for consequential decisions that need durable rationale;
- context problem register for unresolved parked context-local issues.

Do not create a permanent analysis report or preserve rejected alternatives unless they carry durable decision rationale.

After strategic convergence, return to `domain-design-stage.md` for any required Tactical DDD and final G2 evaluation.
