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
2. Classify the highest affected layer:
   - implementation only;
   - requirements/quality;
   - Tactical DDD inside one BC;
   - Strategic DDD/context relationship.
3. If the highest affected layer is Requirements, `REOPEN(S1)` rather than deciding product behavior here.
4. For S2 work, inspect only the smallest affected canonical domain/requirements/ADR evidence.
5. Apply `docs/process/decision-protocol.md` to unknowns/conflicts.
6. For Strategic DDD, require evidence of changed language, responsibility/decision ownership, independent lifecycle/invariants, authority boundary or context relationship; then run the strategic convergence protocol.
7. For Tactical DDD, challenge semantic identity/lifecycle/invariant ownership and separate domain guarantees from persistence/framework realization using the tactical protocol.
8. Update the highest affected canonical artifact first.
9. Return to the S2 gate and propagate only required deltas downstream after G2 passes.
10. Run `make knowledge-check` plus code checks when implementation changes are later performed.

## Guardrail

A class, database table, API, protocol, framework, deployment unit or code-sharing concern is not by itself a Bounded Context argument.

Do not preload the whole strategic model or every context when the semantic question is local.
