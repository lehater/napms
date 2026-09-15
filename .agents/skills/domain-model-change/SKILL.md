---
name: domain-model-change
description: "Use when a new requirement, code finding, or design question may change NAPMS domain semantics: aggregate invariants, semantic identity/lifecycle, ubiquitous language, authority/responsibility ownership, Bounded Context boundaries, or cross-context contracts. Classify the highest affected truth layer, update it first, then propagate downward."
---

# Domain Model Change

Use `docs/process/domain-change-protocol.md` as the focused re-entry classifier.

When the lifecycle routes work to S2, use `docs/process/domain-design-stage.md` for S2/G2 responsibility and routing. Load:
- `docs/process/strategic-ddd-convergence.md` only when Strategic DDD is actually affected;
- `docs/process/tactical-ddd-stage.md` only when Tactical DDD work is active.

## Procedure

1. State the observed trigger without turning it into a conclusion.
2. Classify the highest affected layer: implementation, requirements/quality, Tactical DDD inside one BC, or Strategic DDD/context relationship.
3. If Requirements are affected, `REOPEN(S1)` rather than deciding product behavior here.
4. For S2 work, inspect only the smallest affected current domain and requirements evidence.
5. Apply `docs/process/decision-protocol.md` to material unknowns or conflicts.
6. For Strategic DDD, require evidence of changed language, responsibility/decision ownership, independent lifecycle/invariants, authority boundary or context relationship. Treat candidate context groupings as candidates until the strategic convergence protocol accepts them.
7. For Tactical DDD, challenge semantic identity, lifecycle and invariant ownership; keep domain guarantees separate from persistence/framework realization.
8. Update the highest affected current owner first.
9. Preserve unresolved consequential discoveries only in the smallest existing current owner when they must survive the session; do not create discovery archives or traceability histories.
10. Return to the S2 gate and propagate only required deltas after G2 passes.
11. Run `make knowledge-check` plus applicable code checks when implementation changes are later performed.

## Guardrail

A journey, use case or capability is not automatically a Bounded Context. A class, database table, API, protocol, framework, deployment unit or code-sharing concern is not by itself a Bounded Context argument.

Do not preload the whole strategic model, every context, or all known journeys/use cases when the semantic question is local. Expand only when the current boundary question demonstrates the need.
