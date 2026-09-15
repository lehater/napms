# Domain Design stage

## Purpose

Use this protocol for lifecycle stage `S2 Domain Design` when accepted requirements require domain-semantic modelling or later work reopens domain truth.

S2 answers:

> What business/domain meanings, responsibilities, boundaries, identities, lifecycles and invariants must exist so the accepted requirements can be expressed without implementation invention?

S2 contains two coupled but distinct levels:

- **Strategic DDD** — ubiquitous language boundaries, responsibility/decision ownership, Bounded Context boundaries and cross-context semantic contracts;
- **Tactical DDD** — semantic identity, lifecycle, invariants, aggregates/entities/value objects and domain operations inside an accepted context boundary.

Do not force every S2 task through both levels. Enter the highest domain level actually affected.

## Inputs

Use the smallest applicable set of:

- G1-accepted requirements for the affected scope;
- current strategic/tactical domain artifacts for the affected concepts;
- explicit problems reopened from Architecture/Implementation;
- consequential ADRs that constrain domain meaning;
- evidence only when required to resolve a concrete semantic question.

Implementation code, schemas and APIs are evidence of current realization, not automatic domain truth.

## Routing inside S2

Enter **Strategic DDD** when evidence may change at least one of:

- ubiquitous-language boundary;
- responsibility/decision ownership;
- Bounded Context boundary;
- independent lifecycle/invariant boundary;
- authority boundary;
- cross-context relationship or semantic contract.

Enter **Tactical DDD** when the accepted context boundary remains stable but work may change:

- semantic identity;
- aggregate/invariant ownership;
- entity/value-object meaning;
- lifecycle/state transitions;
- domain operations/events;
- idempotency/uniqueness rules.

A class, table, API, service, framework, deployment unit or shared library is not by itself evidence for Strategic DDD.

### Internal S2 dependency rule

Strategic and Tactical DDD are not separate top-level lifecycle stages, but they do depend on each other.

- A Tactical finding that puts responsibility/context boundary/cross-context contract in doubt reroutes the current S2 work to Strategic DDD; it does not `REOPEN(S2)` because S2 is already active.
- A Tactical finding of cross-context model leakage, semantic chatiness, temporal/change coupling, duplicated authority or scale amplification reroutes only the affected edge to the Strategic coupling challenge when the cause may be insufficient public meaning or a wrong semantic boundary. Do not reopen unrelated edges or contexts.
- If the affected semantic contract is already sufficient and the remaining issue is only efficient delivery, local computation, caching/materialization, transport or deployment, keep S2 semantics unchanged and record/route the concern to S3 Architecture instead.
- A Strategic change to ownership/boundary/contract marks the affected Tactical assumptions inside S2 as requiring revalidation before G2 may pass.
- Revalidate only Tactical concepts whose owner, identity, lifecycle, invariant or operation depends on the changed Strategic guarantee; unrelated context internals do not need a full remodel.
- G2 is evaluated only after the affected Strategic and Tactical views are mutually coherent.

## Working loop

1. State the semantic question without embedding an implementation answer.
2. Confirm the accepted requirement(s) that create the need; `REOPEN(S1)` if product behavior is actually unsettled.
3. Route to Strategic or Tactical level using the criteria above.
4. Resolve unknown/conflicting domain claims through `decision-protocol.md`.
5. Update the highest affected domain owner first.
6. Challenge the result against requirements, neighboring semantic ownership and affected cross-context coupling.
7. When Strategic ownership/boundaries/contracts changed, identify and revalidate only dependent Tactical semantics before G2.
8. Record unresolved material problems rather than widening DTOs/models/Aggregates to hide them.
9. Rework only the affected semantic delta.
10. Evaluate G2 for the affected scope.

When Strategic DDD is active, use `strategic-ddd-convergence.md` rather than treating the existing context map as unquestionable truth.

When Tactical DDD is active, use `tactical-ddd-stage.md` to challenge identity/lifecycle/invariant ownership and to separate domain guarantees from persistence/framework realization.

## Responsibility boundary

S2 owns semantic/domain meaning. It does not choose:

- transport/protocol/framework;
- persistence schema/technology;
- process/deployment topology;
- adapter/vendor integration mechanism;
- code package/class structure except as later realization evidence;
- performance implementation strategy unless it changes domain semantics.

Architecture may constrain feasible realization, but if Architecture requires changing business meaning/ownership it must `REOPEN(S2)` rather than redefining semantics locally.

## G2 — Domain model coherent

`G2 PASS` means Architecture may rely on these guarantees for the affected scope:

- each material authoritative domain fact/decision has an identifiable semantic owner;
- relevant Bounded Context boundaries/relationships are coherent enough for the change;
- affected Tactical assumptions have been revalidated after any Strategic ownership/boundary/contract change;
- cross-context consumers can rely on explicit public semantic meaning rather than peer-private models;
- no unresolved P0/P1 cross-context coupling defect forces peer-private knowledge, duplicated semantic authority or downstream invention; pure delivery/computation concerns may remain owned by S3;
- identity/lifecycle/invariant ownership needed by the change is explicit;
- derived/source/current state required by the change is classified well enough that Architecture need not guess what is authoritative;
- no unresolved P0/P1 semantic ownership contradiction remains;
- accepted domain meaning satisfies G1 behavior without importing architecture choices as domain facts;
- remaining domain unknowns are explicitly non-blocking with a known revisit trigger/owner.

A complete class diagram, ERD or aggregate catalogue is not required when unrelated to the current change.

### G2 outcomes

- `PASS` — mark S2 accepted for the affected scope and continue to S3/next dirty stage.
- `REWORK` — S2 owns the semantic deficiency; revise only the affected Strategic/Tactical model.
- `REOPEN(S1)` — required product behavior/authority/quality meaning is unsettled and cannot be chosen by domain modelling.
- `REOPEN(S0)` — the underlying problem/evidence boundary is itself wrong or contradictory.
- `BLOCKED` — an external semantic/business decision or missing evidence prevents honest domain closure.

Later Architecture/Implementation work may `REOPEN(S2)` when realization exposes a genuine semantic contradiction or missing domain guarantee.

## Context contract

Normal S2 startup should remain small:

```text
root AGENTS.md
-> active resume capsule
-> applicable scoped AGENTS.md
-> domain-model-change Skill when semantic change/re-entry judgement is required
-> this protocol for S2 routing/G2
-> smallest affected domain artifact(s)
-> strategic convergence protocol only for Strategic DDD work
-> tactical protocol only for Tactical DDD work
-> requirements/ADR/evidence only on demonstrated need
```

Do not preload all bounded contexts or the whole strategic model unless the current semantic question genuinely spans them.

On S2 closure/parking, promote accepted semantics to canonical `docs/domain/`/ADR owners, persist unresolved problems appropriately, refresh the capsule, and discard exploration already compressed into canonical domain truth.

## Relationship to other protocols

- `change-lifecycle.md` owns top-level stage transitions/reopen/dirty/no-progress semantics.
- `requirements-stage.md` owns S1/G1 product-behavior guarantees.
- `strategic-ddd-convergence.md` owns iterative Strategic DDD boundary/context-map/contract convergence, including affected-edge cross-context coupling challenge.
- `tactical-ddd-stage.md` owns Tactical DDD identity/lifecycle/invariant coherence inside an accepted context boundary.
- `domain-change-protocol.md` is the focused re-entry classifier used when findings arise from lower layers.
- `decision-protocol.md` owns unknown/conflict handling.
