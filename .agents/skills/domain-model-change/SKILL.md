---
name: domain-model-change
description: "Use when a new requirement, code finding, or design question may change NAPMS domain semantics: aggregate invariants, semantic identity/lifecycle, ubiquitous language, authority/responsibility ownership, Bounded Context boundaries, or cross-context contracts. Classify the highest affected truth layer, update it first, then propagate downward."
---

# Domain Model Change

Use `docs/process/domain-change-protocol.md` as the canonical re-entry method.

## Procedure

1. State the observed trigger without turning it into a conclusion.
2. Classify the highest affected layer:
   - implementation only;
   - requirements/quality;
   - Tactical DDD inside one BC;
   - Strategic DDD/context relationship.
3. Inspect current canonical domain/requirements/architecture evidence.
4. Apply `docs/process/decision-protocol.md` to unknowns/conflicts.
5. For Strategic DDD, require evidence of changed language, responsibility/decision ownership, independent lifecycle/invariants, authority boundary or context relationship.
6. Update the highest affected canonical artifact first.
7. Propagate required deltas through semantic contracts/architecture/ADRs/Tactical DDD/code/tests.
8. Run `make knowledge-check` plus code checks when implementation changes.

## Guardrail

A class, database table, API, protocol, framework, deployment unit or code-sharing concern is not by itself a Bounded Context argument.
