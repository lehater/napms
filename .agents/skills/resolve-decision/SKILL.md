---
name: resolve-decision
description: "Use for one bounded NAPMS To-Be product/domain/architecture/engineering choice where the question is known but the correct alternative is not yet accepted. Check repository evidence, expose unknowns, compare credible alternatives and consequences, obtain the owner decision, then propagate it. Do not use for ordinary code choices already governed by accepted architecture."
---

# Resolve Decision

## Procedure

1. Define one decision question and the owning truth layer.
2. Sweep the smallest relevant current evidence, including as-built contracts and applicable current ADRs when they constrain the choice.
3. Separate known facts, hypotheses, unknowns and conflicts.
4. Identify 2-4 credible alternatives, including the simplest viable option.
5. Compare against current accepted requirements, domain semantics, architecture drivers, current compatibility constraints, risk and reversibility.
6. Recommend only when evidence supports a preference; otherwise make the missing decision explicit.
7. Record normative consequences in their current canonical owners.
8. Create or update an ADR when the consequential choice/rationale/trade-offs/revisit conditions themselves are required to reconstruct or safely evolve the current design.
9. Propagate only the consequences required by dependent current artifacts.

Do not use ADRs as a chronological decision diary or supersession archive. An implemented ADR remains current while its choice is still part of the designed as-built/target system. Superseded-only decision history belongs in Git history.

Never convert a blocking unknown into a default.
