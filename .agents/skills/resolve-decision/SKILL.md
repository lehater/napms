---
name: resolve-decision
description: "Use for one bounded NAPMS product/domain/architecture/engineering choice where the question is known but the correct alternative is not yet accepted. Compare credible alternatives against current evidence, obtain human-owned decisions when required, and propagate the accepted consequence to canonical owners."
---

# Resolve Decision

1. Define one decision question and identify its current owner through `docs/canonical-graph.yaml`.
2. Read the smallest relevant evidence and current design constraints.
3. Separate known facts, hypotheses, unknowns and conflicts.
4. Identify 2-4 credible alternatives, including the simplest viable option.
5. Compare consequences against accepted requirements/domain semantics, architecture constraints, risk and reversibility.
6. Recommend only where evidence supports a preference; never convert missing human-owned truth into a default.
7. Record the accepted normative consequence in its canonical owner.
8. Add/update an ADR only when the rationale/trade-off/revisit condition itself must remain durable.
9. Revalidate only graph-affected downstream artifacts.
