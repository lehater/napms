---
name: resolve-decision
description: "Use for one bounded NAPMS To-Be product/domain/architecture/engineering choice where the question is known but the correct alternative is not yet accepted. Check repository evidence, expose unknowns, compare credible alternatives and consequences, obtain the owner decision, then propagate it. Do not use for ordinary code choices already governed by accepted architecture."
---

# Resolve Decision

## Procedure

1. Define one decision question and the owning truth layer.
2. Sweep relevant current evidence before asking the owner.
3. Separate known facts, hypotheses, unknowns and conflicts.
4. Identify 2-4 credible alternatives, including the simplest viable option.
5. Compare against current accepted requirements, domain semantics, architecture drivers, risk and reversibility.
6. Recommend only when evidence supports a preference; otherwise make the missing decision explicit.
7. Record the accepted result directly in its current canonical owner.
8. Propagate only the consequences required by dependent current artifacts.

Do not create a separate decision-history document when the accepted result belongs in requirements, domain, architecture or engineering truth. Git history preserves the replaced state.

Never convert a blocking unknown into a default.
