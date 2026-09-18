---
name: domain-model-change
description: "Use when a requirement, evidence item, design question or implementation finding may change NAPMS domain semantics: language, identity/lifecycle, invariants, responsibility ownership, Bounded Context boundaries or cross-context contracts. Update the smallest current semantic owner first and propagate only affected downstream design."
---

# Domain Model Change

1. State the observed trigger without converting it into a conclusion.
2. Use `docs/canonical-graph.yaml` to locate the smallest current owner: use-case/requirement, one context model/process, or strategic model.
3. Read that owner and only the direct dependencies needed to judge the change.
4. Separate known facts, hypotheses, missing human truth and contradictions.
5. For strategic changes, require evidence of changed language/responsibility/decision ownership, independent lifecycle/invariants, authority boundary or context relationship; a journey/class/table/API is not itself a Bounded Context argument.
6. For tactical changes, preserve semantic identity, lifecycle and invariant ownership separately from persistence/framework realization.
7. Change the highest semantic owner that actually changed, then use the graph to identify downstream artifacts requiring revalidation.
8. Record a durable decision only when its rationale/trade-off is itself needed to reproduce or safely evolve the design.
9. Run `make design-check` and `make design-sync` for affected projections.

Missing business truth remains an explicit question/blocker; do not fill it with implementation assumptions.
