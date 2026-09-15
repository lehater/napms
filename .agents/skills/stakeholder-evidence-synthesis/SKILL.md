---
name: stakeholder-evidence-synthesis
description: "Use when the task explicitly asks to synthesize several current stakeholder/user evidence sources into problem themes, requirement candidates, capability clues or boundary hypotheses. Do not use for routine S0/S1 elicitation or as a reason to maintain a repository evidence archive."
---

# Stakeholder Evidence Synthesis

## Responsibility

Synthesize the current evidence sources explicitly available to the task without turning frequency, wording or an earlier interpretation into accepted project truth.

This Skill does not depend on a persistent repository evidence corpus. Git history and old conversations are not normal inputs. If the user supplies several current interviews/messages/files or asks to compare current evidence, use those sources directly.

## Inputs

Load the narrowest current evidence set that can answer the question, plus current accepted requirements/domain truth only when needed for comparison.

Do not preload unrelated conversations, historical repository states, all journeys/use cases or the whole domain model.

## Procedure

1. State the synthesis question.
2. Load only current sources relevant to that question.
3. Separate source observation from interpretation.
4. Group equivalent observations without erasing materially different actors, contexts, constraints or contradictions.
5. Distinguish independent corroboration from copies/summaries of the same source.
6. Produce candidates only: problem themes, journeys/use cases, requirements, capability clues or boundary hypotheses as applicable.
7. Classify consequential candidates with `decision-protocol.md`.
8. Route acceptance to the owning lifecycle stage: S0 problem framing, S1 observable behavior, S2 domain meaning/boundaries.
9. Persist only conclusions accepted by their owning stage in current canonical artifacts.
10. Discard working clustering after the current canonical owner absorbs any accepted result.

## Output

Return only what the current task needs: supported themes, contradictions/weak areas, relevant candidates, their owner/status and the next owning lifecycle action.

## Guardrails

- Evidence volume is not acceptance authority.
- A stakeholder-proposed solution may reveal a need without becoming a requirement.
- Do not create transcript stores, synthesis archives, permanent evidence taxonomies or traceability graphs.
- This Skill does not validate an implemented UI journey; use the journey-validation Skill for that.
- This Skill does not decide Bounded Context boundaries by itself; boundary clues route to S2 Strategic DDD.
