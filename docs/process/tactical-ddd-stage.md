# Tactical DDD stage

## Purpose

Use this protocol only when `S2 Domain Design` has been routed to Tactical DDD inside an accepted Bounded Context boundary.

Tactical DDD answers:

> Which semantic identities, lifecycles, invariants and domain operations must the context own so its accepted responsibilities and requirements can be expressed coherently?

It does not design persistence schemas, framework objects, transport DTOs or code packages.

Load this protocol only for active Tactical DDD work or tactical gate evaluation.

## Inputs

Use the smallest applicable set of:

- G1-accepted requirements for the affected behavior;
- accepted Strategic DDD responsibility/boundary when strategic ownership is material;
- current tactical model for the affected concept(s);
- reopened semantic problem from Architecture/Implementation;
- ADRs/evidence only when required to resolve the concrete tactical question.

Implementation classes, tables, ORM mappings and existing API shapes are evidence of current realization, not automatic tactical truth.

## Responsibility boundary

Tactical DDD may own and define:

- semantic identity and identity equivalence;
- entity/value-object distinction where it carries domain meaning;
- aggregate/invariant ownership where a consistency boundary is semantically required;
- lifecycle states and allowed transitions;
- domain operations/decisions;
- uniqueness/idempotency rules when they are part of domain meaning;
- domain facts/events when they represent accepted business/domain facts;
- current-vs-historical semantic state when that distinction is domain-significant;
- derived semantic values/projections when their meaning is part of the domain contract.

Tactical DDD must not choose merely to make implementation convenient:

- table/column/index structure;
- ORM mapping;
- relational normalization/denormalization;
- PostgreSQL-specific query strategy;
- persistence of a derived read model when persistence itself is only a performance mechanism;
- transport/request/response shape unless it is itself an accepted semantic contract;
- adapter/vendor state representation;
- scheduling, retry/backoff or infrastructure mechanism;
- package/class decomposition.

If a realization mechanism appears in a tactical artifact, classify the underlying statement before relying on it:

```text
semantic guarantee required by domain meaning
    -> S2 tactical truth

realization choice satisfying that guarantee
    -> S3 Architecture or S4 Implementation Readiness
```

Example: `routing state and derived reachability become visible atomically` may be a semantic consistency guarantee; `persist EffectiveReachabilitySegment rows in PostgreSQL and replace them transactionally` is an architecture/persistence choice.

## Tactical working loop

For the affected semantic question:

1. **State the invariant/identity/lifecycle question.** Do not begin from a class/table proposal.
2. **Confirm ownership.** Verify the accepted context owns the fact/decision. If ownership is unclear or cross-context, return to Strategic DDD rather than stretching the tactical model.
3. **Confirm requirement pressure.** Identify which accepted behavior or context responsibility requires the tactical concept. `REOPEN(S1)` when behavior itself is unsettled.
4. **Define semantic identity.** State what makes the concept the same/different over time and which identifiers are semantic versus technical.
5. **Define lifecycle.** State meaningful states, transitions, creation/retirement/replacement semantics only where required.
6. **Define invariants and their owner.** Each invariant must have one semantic owner capable of preserving it. Do not invent an aggregate solely because the ORM needs a transaction boundary.
7. **Classify derived/current/source data.** Distinguish authoritative domain state, source-reported facts, derived semantic results and rebuildable implementation projections.
8. **Define domain operations/facts.** Express decisions and effects in domain language; avoid service/API signatures unless needed only as examples.
9. **Challenge implementation leakage.** For every persistence/technology-shaped statement ask whether changing the mechanism would change domain meaning. If not, route it downstream.
10. **Challenge over-modelling.** Remove entities/state machines/commands that do not own independent identity, lifecycle or invariant.
11. **Resolve/route unknowns.** Use `decision-protocol.md`; reopen Strategic DDD when context ownership is wrong/unclear; reopen S1 when product behavior is missing.
12. **Update the smallest canonical domain owner first** and evaluate tactical coherence.

## Tactical coherence checks

For the affected scope, verify:

- every semantic identity has an explicit sameness rule where material;
- every lifecycle/state distinction changes domain meaning rather than only implementation state;
- every invariant has one owner and a feasible semantic consistency boundary;
- aggregate boundaries follow invariant ownership, not storage convenience;
- value objects do not accidentally receive independent identity/lifecycle;
- source evidence/current source state is not promoted to authoritative domain truth without a domain rule;
- derived values are labelled as authoritative, derived/rebuildable, or ephemeral as appropriate;
- domain operations do not depend on peer-context private models;
- technical IDs, row IDs, state versions and cache keys are not mistaken for semantic identity;
- tactical concepts satisfy accepted requirements without selecting unnecessary architecture.

## Tactical gate

Tactical work is coherent for the affected scope when:

- semantic identity/lifecycle/invariant ownership required by the change is explicit;
- aggregate/entity/value-object distinctions used by the change are justified by semantic meaning;
- domain operations/decisions preserve the accepted invariants;
- derived/source/current-state concepts are classified well enough that Architecture need not guess what is authoritative;
- no unresolved P0/P1 tactical contradiction remains;
- no persistence/framework/transport decision is being treated as domain truth merely because it exists in a tactical document;
- any remaining unknown is explicitly non-blocking with an owner/revisit trigger.

### Outcomes

- `PASS` — return to `domain-design-stage.md` for final G2 evaluation.
- `REWORK` — correct the affected tactical semantic delta.
- `REOPEN Strategic DDD` — responsibility/context boundary or cross-context contract is the real problem.
- `REOPEN(S1)` — required product behavior/authority/quality expectation is unsettled.
- `REOPEN(S0)` — the problem/evidence premise is invalid or contradictory.
- `BLOCKED` — required semantic/business decision cannot be derived from current accepted truth/evidence.

## Mixed-level canonical artifacts

Existing tactical documents may contain architecture or implementation detail. Do not treat file location as proof of semantic ownership.

During revalidation:

1. classify the specific statement by meaning;
2. keep accepted semantic guarantees in the domain owner;
3. route architecture/persistence mechanisms to S3/S4 when they become relevant to the current change;
4. do not mass-rewrite unrelated historical/current documents solely for taxonomy purity;
5. when editing an affected canonical artifact, reduce obvious mixed-level duplication if doing so is safe and local.

## Context contract

Normal startup remains narrow:

```text
root AGENTS.md
-> active resume capsule
-> scoped AGENTS.md if applicable
-> domain-model-change Skill when re-entry/classification judgement is needed
-> domain-design-stage.md for S2 routing/G2
-> this protocol for active Tactical DDD
-> smallest affected tactical/domain artifact(s)
-> requirements/Strategic/ADR/code evidence only on demonstrated need
```

Do not preload Strategic DDD convergence when the context boundary is already accepted and not under question.

## Relationship to other protocols

- `domain-design-stage.md` owns S2 routing and final G2.
- `strategic-ddd-convergence.md` owns Strategic DDD convergence when ownership/boundary/relationship is under question.
- `requirements-stage.md` owns product-behavior guarantees.
- `change-lifecycle.md` owns stage transitions/reopen/dirty/no-progress semantics.
- S3 Architecture owns realization mechanisms intentionally excluded here.
