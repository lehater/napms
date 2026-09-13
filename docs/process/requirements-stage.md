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
- database schema or persistence projection shape;
- API shape unless the API itself is an accepted external product contract;
- framework/deployment/infrastructure choice;
- algorithm/database execution strategy unless it is itself an externally required quality constraint.

If such a decision is actually required product truth, state the observable constraint rather than the implementation mechanism.

A concrete suggestion made during requirements discussion is not automatically a requirement. Before recording it, classify it with `decision-protocol.md` on both axes:

1. semantic owner/lifecycle level;
2. decision status/obligation.

An implementation or architecture suggestion may be explicit and even accepted while still belonging to S3/S4. S1 shall preserve any independent observable requirement and route the realization choice to its actual owner rather than promoting it into the requirement family.

Example:

```text
User discussion: "read routing and ACL names together so they have one update date"

S1 question: what externally observable freshness/provenance must downstream receive?
S3 question: should acquisition form one logical snapshot, separate snapshots, one session, multiple commands, etc.?
```

If the first is accepted and the second is only proposed, write only the first into S1 requirements and preserve the second as a later-stage proposal. If both are explicitly accepted, they are still recorded in their respective semantic owners.

Journeys and use cases are discovery views over product intent, not automatic requirements or architecture boundaries. When discussion exposes several independently useful outcomes, distinguish the candidate use cases before flattening them into requirements. One use case may participate in several journeys, and one use case may later require several capabilities; none of those facts by itself creates a Bounded Context.

## Working loop

For the behavior under change:

1. **State the requirement boundary.** Identify actor/initiator, trigger or starting condition, intended outcome and affected requirement family.
2. **Separate materially distinct use cases when needed.** If the discussion contains independently useful outcomes, identify only the smallest set needed to avoid merging different product goals. Keep candidate/deferred uses non-authoritative until accepted; do not build an exhaustive journey map unless the current decision requires it.
3. **Classify every material statement.** Apply both axes from `decision-protocol.md`: semantic owner/stage and decision status/obligation. Do this before turning conversation wording into canonical requirements.
4. **Separate fact from assumption.** Mark material statements as accepted/known, constraint, proposal, hypothesis, unknown or conflict.
5. **Express observable behavior.** Describe what must be true from the relevant actor/system boundary, not how code achieves it.
6. **Split behavior from realization.** When one discussion statement contains both, preserve the observable constraint in S1 and route architecture/implementation detail to S3/S4 unless the concrete representation is itself an accepted external contract.
7. **Cover material alternatives.** Add failure, denial, absence, unknown, timeout, concurrency, cancellation or partial-state behavior only when it changes the product contract.
8. **State quality constraints.** Capture performance, security, audit/provenance, temporal, consistency or availability expectations only where they constrain downstream design.
9. **Check semantic leakage.** Remove architecture/implementation choices masquerading as requirements. Preserve external compatibility constraints when genuinely required.
10. **Check internal coherence.** Look for contradictory outcomes, undefined authority/scope, impossible combinations, ambiguous terms and requirements that cannot be observed or verified.
11. **Resolve or route unknowns.** Resolve from canonical evidence; ask/escalate blocking product choices; register non-blocking deferred questions instead of inventing answers.
12. **Preserve consequential deferred usage discoveries.** Candidate journeys/use cases/capability clues that are not accepted S1 behavior belong only in the smallest existing durable owner (for example the active problem/capsule or a parked context problem register) when losing them would harm later work. Do not use `docs/requirements/` as memory storage.
13. **Update the owning requirement artifact first.** Do not make the active plan or conversation the durable owner of accepted behavior.
14. **Evaluate G1.** Rework only the affected behavior delta. If G1 exposes an upstream problem-definition/evidence gap, `REOPEN(S0)`.

## Existing mixed-level artifacts

The lifecycle classifies statements by semantic ownership, not entire files by filename.

Existing requirement files may contain historical domain or architecture/implementation decisions mixed with product behavior. When such a file is touched:

1. classify only the statements material to the current change;
2. preserve accepted behavior needed by S1;
3. treat lower-level design statements as constraints/evidence for their owning later stage, not automatically as G1 guarantees;
4. move or restate them in the correct canonical owner when the current change actually requires revalidation;
5. do not start a repository-wide documentation migration merely to make old files structurally pure.

A later-stage choice that has become an intentional product contract may remain represented as a requirement only if its externally observable constraint is explicit. The implementation mechanism itself should still live with its proper owner.

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

A requirement fails the non-prescriptive check when its only justification is that a suggested realization seems convenient. Explicit user wording does not waive this check; the statement must still belong to S1 semantically.

Do not demand exhaustive specification of behavior irrelevant to the current change. Completeness is gate-relative, not encyclopedic.

## Outputs

S1 produces only the durable outputs needed by downstream work:

- updated accepted requirement artifact(s);
- acceptance examples/scenarios where they materially disambiguate behavior;
- explicit open problems/deferrals with owner and revisit trigger;
- concise lifecycle/capsule state needed to resume or transition.

Later-stage proposals and candidate journeys/use cases/capability clues discovered while discussing requirements may be preserved only in their correct owner/problem register when they are consequential enough to survive; do not copy them into requirements merely as memory storage and do not create a permanent discovery report by default.

Do not create a separate requirements packet merely to mirror the stage if an existing requirement family is the correct owner.

## G1 — Requirements coherent

`G1 PASS` means Domain Design may rely on the following guarantees for the affected scope:

- the required observable outcome is explicit;
- relevant actor/scope/applicability is explicit enough for semantic modelling;
- material failure/denial/unknown behavior is explicit where downstream semantics depend on it;
- material temporal/quality/security constraints are explicit where they constrain the model;
- accepted requirements do not contain unresolved P0/P1 contradictions for this scope;
- no downstream product decision is being hidden as an unspecified implementation choice;
- no architecture/implementation proposal has been promoted into S1 merely because it was explicit, concrete or convenient;
- lower-level design choices found in mixed artifacts are not being mistaken for S1 guarantees without revalidation;
- materially distinct usage outcomes surfaced in the active S1 discussion are either represented by accepted behavior, explicitly deferred/routed, or deliberately discarded as non-consequential rather than silently merged or lost;
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

Do not preload all requirement families, DDD documentation, architecture or code. Do not preload all known journeys/use cases merely because discovery evidence exists; load only those needed by the current behavior question.

When G1 passes or S1 becomes blocked/parked:

- promote accepted behavior to `docs/requirements/`;
- persist unresolved material questions and consequential deferred usage discoveries in the smallest correct current planning/problem owner;
- update lifecycle stage/state/gate/next action in the resume capsule;
- discard exploration and evidence already compressed into accepted requirements;
- prefer session rollover when moving into Domain Design if the Requirements conversation has accumulated substantial task-specific context.

## Relationship to other protocols

- `change-lifecycle.md` owns entry, gate transition, `REOPEN`, dirty propagation and no-progress semantics.
- `decision-protocol.md` owns semantic-level plus decision-status classification and unknown/conflict handling.
- `domain-change-protocol.md` may route later findings back into S1 but does not define requirements quality.
- `plan-lifecycle.md` owns durable current execution/problem parking state.
- `working-loop.md` owns checkpoint/rollover/validation execution mechanics.
