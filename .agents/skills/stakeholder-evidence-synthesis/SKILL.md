---
name: stakeholder-evidence-synthesis
description: "Use when explicitly synthesizing stakeholder/user evidence, or when one or more elicitation answers contain additional requirements, use cases, journeys, actors, rules, terminology, capability clues, boundary clues or contradictions that need to be harvested without automatically accepting them as truth."
---

# Stakeholder Evidence Synthesis

This Skill can operate on one current stakeholder answer, an ongoing interview, or several evidence sources.

1. State the elicitation/synthesis question and keep the user's immediate question primary.
2. Load only current evidence relevant to it; do not preload old chats/repository history as normal evidence.
3. Extract observations before interpretations. Look not only for the literal answer, but also for additional:
   - requirements/constraints;
   - use cases, journeys, journey steps, actors and goals;
   - rules/invariants;
   - terms and meaning distinctions;
   - capability/responsibility/boundary clues;
   - contradictions, exceptions and unresolved questions.
4. Mark every extracted item as one of:
   - observed;
   - candidate interpretation;
   - explicitly accepted;
   - unresolved/contradictory.
5. Distinguish independent corroboration from copies/summaries when several sources exist. Frequency is evidence weight, not acceptance authority.
6. Use `docs/canonical-graph.yaml` to identify the smallest owner that would accept an explicitly accepted item.
7. Persist explicitly accepted semantics in that canonical owner and revalidate only graph-affected downstream artifacts.
8. If a candidate/unresolved item must survive beyond the exchange, preserve it in the nearest relevant discovery artifact or active workstream state as candidate/question/evidence. Do not place it in a canonical semantic owner as decided truth.
9. Do not interrupt the current interview for every side finding. Capture material side findings and continue unless a contradiction blocks the current line.
10. Discard transient clustering/working notes once accepted semantics or durable candidates have been persisted.

A stakeholder-proposed solution may reveal a need without becoming a requirement. Boundary clues do not themselves establish a Bounded Context. Discovered != accepted.
