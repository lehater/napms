# Problem / Evidence stage

## Purpose

Use this protocol for lifecycle stage `S0 Problem / Evidence` when the requested change is still an unclear need, observed defect, conflicting evidence, operational pain, external constraint or other trigger whose target behavior is not yet sufficiently framed for Requirements.

S0 answers:

> What problem/change pressure is actually observed, for whom/where, what evidence supports it, what outcome is sought, and what remains unknown — without choosing the product/domain/architecture solution?

S0 is not a requirements specification and must not invent target behavior merely to make the problem look complete.

## Inputs

Use only evidence relevant to framing the trigger:

- explicit user/stakeholder request;
- stakeholder examples, workarounds and descriptions of real usage;
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
4. **Separate epistemic states.** Use `decision-protocol.md` for known/hypothesis/unknown/conflict and keep stakeholder evidence separate from interpretation.
5. **State the desired outcome.** Express why the change matters, not how the system should implement it.
6. **Harvest consequential stakeholder evidence.** A stakeholder answer may reveal more than the question it was asked to resolve. Preserve material problems, goals, usage context, examples, workarounds, constraints, risks or independently useful outcomes that would remain valuable even if the current interpretation changes. Do not preserve the full conversation.
7. **Capture consequential usage discoveries.** When evidence suggests a materially distinct actor/consumer goal, journey or possible use of an outcome, preserve only enough of the candidate to avoid losing later Requirements work. Keep it non-authoritative unless its owning stage accepts it; do not expand every mention into a full journey map or requirement set.
8. **Identify material constraints/non-goals.** Preserve externally fixed constraints; do not invent internal ones.
9. **Resolve obvious evidence conflicts.** Prefer canonical truth or explicit owner evidence for current accepted state, while keeping contradictory stakeholder evidence visible when it may matter to later revalidation.
10. **Classify blocking questions.** Ask/escalate only questions required to move honestly into Requirements; defer unrelated curiosity.
11. **Update the smallest durable problem owner** (active plan/problem register/issue-like artifact as appropriate) only when the problem, consequential source evidence or discovery must survive the conversation. Do not create a new evidence/discovery artifact when an existing owner is sufficient.
12. **Evaluate G0.**

## G0 — Problem understood

`G0 PASS` means Requirements may begin because, for the affected scope:

- the observed problem/change trigger is explicit;
- the desired outcome is distinguishable from a proposed solution;
- material evidence/source is identifiable;
- known facts, assumptions and unknowns are separated;
- affected actor/surface/scope is clear enough to elicit behavior;
- no unresolved P0/P1 contradiction prevents knowing what problem is being solved;
- remaining unknowns are either requirements questions or explicitly non-blocking.

G0 does **not** require knowing the final behavior, complete journey/use-case inventory, domain model or architecture. Material stakeholder evidence already surfaced in the active discussion should not be silently lost merely because it is not needed to pass G0.

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

Do not preload all historical stakeholder evidence, Requirements/DDD/Architecture methodologies or unrelated conversations before G0. Search/load additional evidence only when the current problem framing demonstrates the need.

## Relationship to other protocols

- `change-lifecycle.md` owns routing/transitions/no-progress semantics.
- `decision-protocol.md` owns known/hypothesis/unknown/conflict handling and stakeholder-evidence interpretation boundaries.
- `requirements-stage.md` owns S1 once G0 has framed the problem sufficiently.
- `plan-lifecycle.md` owns durable current execution/problem parking mechanics.
