---
name: stakeholder-evidence-synthesis
description: "Use when the task is to re-analyze accumulated stakeholder/user evidence across discussions or preserved sources to find recurring problems, usage patterns, journeys/use cases, requirement candidates, capability clues or boundary hypotheses. Do not use for routine stage-end evidence capture, ordinary S0/S1 elicitation, accepted UI journey validation, or Strategic DDD unless the prompt is explicitly about synthesizing the evidence corpus itself."
---

# Stakeholder Evidence Synthesis

## Responsibility

Synthesize already preserved stakeholder/user evidence without turning frequency, wording or current interpretation into canonical truth.

This Skill is deliberately lazy-loaded. Routine S0/S1 work captures consequential evidence through the stage protocols and `working-loop.md`; it does not invoke this Skill merely because a stakeholder gave an example.

## Inputs

Start from the narrowest evidence scope that can answer the synthesis question:

- current problem area/topic;
- relevant preserved stakeholder evidence atoms or problem-register entries;
- accepted requirements/domain truth only when needed to compare evidence against current interpretation;
- provenance needed to distinguish independent observations from duplicated summaries.

Do not preload all historical conversations, all problem registers, all journeys/use cases or the whole domain model.

## Procedure

1. **State the synthesis question.** Examples: identify recurring user problems, find independently useful outcomes, test requirement completeness, or look for capability/boundary clues.
2. **Load narrowly.** Search/load only evidence for the affected topic and widen only when contradictions, gaps or cross-workstream reuse demonstrate the need.
3. **Separate source from interpretation.** Preserve what stakeholders actually revealed independently from earlier requirement/domain conclusions.
4. **Normalize without erasing differences.** Group equivalent observations, but retain materially different actors, contexts, constraints, minority cases and contradictions.
5. **Distinguish repetition from duplication.** Multiple independent stakeholder observations strengthen evidence; copies/summaries of the same source do not.
6. **Derive candidates, not truth.** Produce only the candidate views justified by the task: problem themes, journeys, use cases, requirement candidates, examples/scenarios, capability clues or Bounded Context hypotheses.
7. **Classify each candidate.** Use `docs/process/decision-protocol.md` for semantic owner and accepted/constraint/proposal/hypothesis/unknown/conflict status.
8. **Route to the owning stage.** S0 owns problem framing, S1 observable behavior, S2 domain meaning/boundaries. Do not accept cross-stage conclusions inside this Skill.
9. **Persist minimally.** Update canonical artifacts only when the owning stage actually accepts a conclusion. Otherwise preserve only consequential synthesis findings in the smallest existing durable owner.
10. **Discard working clustering.** Do not create a permanent synthesis report, global traceability graph or evidence taxonomy merely because the analysis was performed.

## Output

Return a compact synthesis containing only what the current task needs, normally:

- recurring/problem themes with supporting source references;
- contradictions or weakly supported areas;
- candidate journeys/use cases/requirements/capabilities/boundary clues as applicable;
- semantic owner and decision status for each consequential candidate;
- next owning lifecycle stage/action.

## Guardrails

- Evidence volume is not acceptance authority.
- A stakeholder-proposed solution may reveal an underlying need without making the solution a requirement.
- One example may support several later interpretations; do not copy it into every artifact.
- Old evidence may be stale or superseded; retain provenance/time context where material.
- This Skill does not validate whether an accepted UI journey works end-to-end; use `user-journey-validation` for that.
- This Skill does not decide Bounded Context boundaries by itself; capability/boundary findings are evidence for S2 Strategic DDD.
