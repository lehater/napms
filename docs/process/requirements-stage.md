# Requirements stage

## Purpose

Use this protocol for lifecycle stage `S1 Requirements` when accepted product behavior or quality expectations may need to be created, changed, clarified or revalidated.

This stage answers:

> What observable behavior/outcome must the system provide, under which conditions and constraints, without deciding the implementation mechanism?

Requirements own observable product behavior and quality expectations. They do not own domain identity/invariant meaning already owned by DDD artifacts, and they do not choose architecture, persistence, APIs, classes or deployment topology.

Load this protocol only while S1 work or G1 evaluation is active.

## Inputs

Start from the smallest applicable set of:

- accepted problem/need and evidence from S0 when S0 was required;
- existing requirement family that owns the behavior under change;
- relevant accepted domain language/constraints when already established;
- actor/stakeholder and authority facts needed to state behavior;
- quality/security/temporal constraints that materially affect observable outcomes;
- open problems explicitly routed to S1 by a later stage.

Existing implementation and tests may provide evidence of current behavior, but they do not define target behavior by themselves.

## Responsibility boundary

S1 must determine behavior well enough that Domain Design can reason about semantic ownership without inventing product intent.

S1 may define:

- actor/user/system goal;
- preconditions and applicability;
- observable success outcome;
- observable negative/failure/unknown outcomes where material;
- authority/scope expectations as product behavior;
- temporal and consistency expectations where externally meaningful;
- quality attributes and acceptance constraints;
- examples/scenarios that disambiguate behavior.

S1 must not decide merely to unblock later work:

- bounded-context ownership;
- aggregate/entity/value-object structure;
- internal domain identity implementation;
- ports/adapters/service boundaries;
- database schema;
- API shape unless the API itself is an accepted external product contract;
- framework/deployment/infrastructure choice.

If such a decision is actually required product truth, state the observable constraint rather than the implementation mechanism.

## Working loop

For the behavior under change:

1. **State the requirement boundary.** Identify actor/initiator, trigger or starting condition, intended outcome and affected requirement family.
2. **Separate fact from assumption.** Mark material statements as accepted/known, hypothesis, unknown or conflict using `decision-protocol.md`.
3. **Express observable behavior.** Describe what must be true from the relevant actor/system boundary, not how code achieves it.
4. **Cover material alternatives.** Add failure, denial, absence, unknown, timeout, concurrency, cancellation or partial-state behavior only when it changes the product contract.
5. **State quality constraints.** Capture performance, security, audit/provenance, temporal, consistency or availability expectations only where they constrain downstream design.
6. **Check semantic leakage.** Remove architecture/implementation choices masquerading as requirements. Preserve external compatibility constraints when genuinely required.
7. **Check internal coherence.** Look for contradictory outcomes, undefined authority/scope, impossible combinations, ambiguous terms and requirements that cannot be observed or verified.
8. **Resolve or route unknowns.** Resolve from canonical evidence; ask/escalate blocking product choices; register non-blocking deferred questions instead of inventing answers.
9. **Update the owning requirement artifact first.** Do not make the active plan or conversation the durable owner of accepted behavior.
10. **Evaluate G1.** Rework only the affected behavior delta. If G1 exposes an upstream problem-definition/evidence gap, `REOPEN(S0)`.

## Requirement quality checks

A material requirement should be sufficiently:

- **owned** — its requirement family/product surface is identifiable;
- **bounded** — actor, trigger/scope and expected outcome are understandable;
- **observable** — success/failure can be evidenced from the relevant boundary;
- **unambiguous enough** — downstream work need not choose between materially different product meanings;
- **consistent** — it does not contradict accepted requirements without an explicit resolution;
- **non-prescriptive** — it constrains behavior rather than selecting an implementation unnecessarily;
- **complete enough** — material negative/unknown/temporal/authority behavior is stated where omission would force downstream invention;
- **traceable** — the reason/evidence or accepted decision can be located when consequential.

Do not demand exhaustive specification of behavior irrelevant to the current change. Completeness is gate-relative, not encyclopedic.

## Outputs

S1 produces only the durable outputs needed by downstream work:

- updated accepted requirement artifact(s);
- acceptance examples/scenarios where they materially disambiguate behavior;
- explicit open problems/deferrals with owner and revisit trigger;
- concise lifecycle/capsule state needed to resume or transition.

Do not create a separate requirements packet merely to mirror the stage if an existing requirement family is the correct owner.

## G1 — Requirements coherent

`G1 PASS` means Domain Design may rely on the following guarantees for the affected scope:

- the required observable outcome is explicit;
- relevant actor/scope/applicability is explicit enough for semantic modelling;
- material failure/denial/unknown behavior is explicit where downstream semantics depend on it;
- material temporal/quality/security constraints are explicit where they constrain the model;
- accepted requirements do not contain unresolved P0/P1 contradictions for this scope;
- no downstream product decision is being hidden as an unspecified implementation choice;
- remaining unknowns are explicitly classified as non-blocking for G1 with a known later owner/revisit trigger.

A document existing, examples existing, or tests currently passing do not by themselves constitute G1 PASS.

### G1 outcomes

- `PASS` — mark S1 accepted against current upstream inputs and proceed to the next required/dirty stage.
- `REWORK` — requirement wording/coverage/coherence is insufficient but S1 owns the answer; fix the affected requirement delta.
- `REOPEN(S0)` — the need, evidence, stakeholder intent or problem boundary is insufficient/contradictory, so Requirements cannot legitimately choose the answer.
- `BLOCKED` — the required product decision is owned externally and current evidence cannot resolve it; register/ask rather than invent.

A later stage may also `REOPEN(S1)` when it discovers that a product behavior choice was never actually settled.

## Context contract

Normal S1 startup should remain small:

```text
root AGENTS.md
-> active resume capsule
-> applicable scoped AGENTS.md
-> smallest applicable Skill (if any)
-> this protocol only when S1 work/gate is active
-> owning requirement artifact(s)
-> evidence/domain constraints only on demonstrated need
```

Do not preload all requirement families, DDD documentation, architecture or code.

When G1 passes or S1 becomes blocked/parked:

- promote accepted behavior to `docs/requirements/`;
- persist unresolved material questions in the current planning/problem owner;
- update lifecycle stage/state/gate/next action in the resume capsule;
- discard exploration and evidence already compressed into accepted requirements;
- prefer session rollover when moving into Domain Design if the Requirements conversation has accumulated substantial task-specific context.

## Relationship to other protocols

- `change-lifecycle.md` owns entry, gate transition, `REOPEN`, dirty propagation and no-progress semantics.
- `decision-protocol.md` owns known/hypothesis/unknown/conflict handling.
- `domain-change-protocol.md` may route later findings back into S1 but does not define requirements quality.
- `plan-lifecycle.md` owns durable current execution/problem parking state.
- `working-loop.md` owns checkpoint/rollover/validation execution mechanics.
