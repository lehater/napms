# Problem / Evidence stage

## Purpose

Use this protocol for lifecycle stage `S0 Problem / Evidence` when the requested change is still an unclear need, observed defect, conflicting evidence, operational pain, external constraint or other trigger whose target behavior is not yet sufficiently framed for Requirements.

S0 answers:

> What problem/change pressure is actually observed, for whom/where, what evidence supports it, what outcome is sought, and what remains unknown — without choosing the product/domain/architecture solution?

S0 is not a requirements specification and must not invent target behavior merely to make the problem look complete.

## Inputs

Use only evidence relevant to framing the trigger:

- explicit user/stakeholder request;
- defect/incident/operational observation;
- failing journey/test/log/runtime evidence;
- external compatibility/security/regulatory constraint;
- current product behavior where relevant;
- conflicting canonical sources that triggered revalidation;
- a later-stage `REOPEN(S0)` reason.

## Responsibility boundary

S0 may establish:

- affected actor/system/product surface;
- observed current situation;
- desired outcome at problem level;
- evidence and provenance;
- constraints already known to be externally fixed;
- facts vs hypotheses vs unknowns;
- scope boundaries and explicit non-goals when needed;
- questions requiring stakeholder/product clarification.

S0 must not choose:

- detailed product behavior;
- domain ownership/model;
- architecture mechanism;
- implementation approach.

Those belong to later stages after G0.

## Working loop

1. **State the trigger neutrally.** Describe what was requested/observed without embedding a preferred solution.
2. **Identify the affected boundary.** Actor/system/surface/context only as far as evidence supports it.
3. **Collect the smallest decisive evidence.** Do not scan the repository broadly if the problem can already be framed.
4. **Separate epistemic states.** Use `decision-protocol.md` for known/hypothesis/unknown/conflict.
5. **State the desired outcome.** Express why the change matters, not how the system should implement it.
6. **Identify material constraints/non-goals.** Preserve externally fixed constraints; do not invent internal ones.
7. **Resolve obvious evidence conflicts.** Prefer canonical truth or explicit owner evidence; keep unresolved conflicts visible.
8. **Classify blocking questions.** Ask/escalate only questions required to move honestly into Requirements; defer unrelated curiosity.
9. **Update the smallest durable problem owner** (active plan/problem register/issue-like artifact as appropriate) only when the problem must survive the conversation.
10. **Evaluate G0.**

## G0 — Problem understood

`G0 PASS` means Requirements may begin because, for the affected scope:

- the observed problem/change trigger is explicit;
- the desired outcome is distinguishable from a proposed solution;
- material evidence/source is identifiable;
- known facts, assumptions and unknowns are separated;
- affected actor/surface/scope is clear enough to elicit behavior;
- no unresolved P0/P1 contradiction prevents knowing what problem is being solved;
- remaining unknowns are either requirements questions or explicitly non-blocking.

G0 does **not** require knowing the final behavior, domain model or architecture.

### G0 outcomes

- `PASS` — proceed to S1 when requirements work is needed.
- `REWORK` — S0 can improve problem framing/evidence with currently available responsibility/evidence.
- `BLOCKED` — the problem cannot be framed without external clarification/evidence; register/ask instead of inventing.

S0 has no earlier lifecycle stage to reopen. A no-progress S0 blockage requires new evidence or external clarification.

## Context contract

Normal S0 startup should be very small:

```text
root AGENTS.md
-> active resume capsule when one exists
-> scoped AGENTS.md if applicable
-> this protocol only for active S0/G0 work
-> trigger/evidence directly relevant to the problem
-> canonical/project evidence only on demonstrated need
```

Do not preload Requirements/DDD/Architecture methodologies before G0 unless a specific existing canonical conflict must be inspected to understand the problem.

## Relationship to other protocols

- `change-lifecycle.md` owns routing/transitions/no-progress semantics.
- `decision-protocol.md` owns known/hypothesis/unknown/conflict handling.
- `requirements-stage.md` owns S1 once G0 has framed the problem sufficiently.
- `plan-lifecycle.md` owns durable current execution/problem parking mechanics.
