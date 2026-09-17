# Requirements stage

## Purpose

Use S1 when current observable product behavior or quality constraints must be created, changed, clarified or revalidated.

S1 answers:

> What observable behavior/outcome must hold, under which conditions and constraints, without choosing the implementation mechanism?

Requirements do not own Bounded Context boundaries, aggregate structure, persistence, APIs unless externally contracted, framework choice or deployment topology.

## Inputs

Load only what the affected behavior needs:

- current S0 problem/outcome when S0 was required;
- the owning current requirement artifact;
- relevant current domain language/constraints;
- authority/security/temporal/quality facts that affect observable behavior;
- a current `REOPEN(S1)` finding when work returns from a later stage.

Implementation/tests are evidence of current behavior, not automatic target truth.

## Working loop

1. Identify actor/initiator, trigger/applicability, intended outcome and owning requirement family.
2. Separate materially different use cases only when merging them would hide different observable outcomes.
3. Classify material statements with `decision-protocol.md` before promoting them to requirements.
4. State observable success, failure, denial, absence, unknown, concurrency or temporal behavior only where it materially changes the contract.
5. Separate observable constraints from proposed realization. Route architecture/implementation choices to S3/S4 unless the concrete representation is itself an external contract.
6. State material security, authority, audit/provenance, consistency, performance or availability constraints at the observable level.
7. Remove semantic leakage and implementation convenience masquerading as product behavior.
8. Check for contradictions, undefined authority/scope and ambiguous outcomes.
9. Resolve blocking product choices from current canonical evidence or the product owner; do not invent defaults.
10. Update the current owning requirement artifact and remove replaced wording rather than preserving alternative versions.
11. Evaluate G1.

Stakeholder examples are useful only for the current decision. Once accepted behavior is expressed in its requirement owner, do not keep duplicate transcript/evidence artifacts merely for historical traceability.

## Requirement quality

A material requirement is:

- **owned** — its product/requirement family is clear;
- **bounded** — actor, applicability and outcome are understandable;
- **observable** — it can be evidenced at the relevant boundary;
- **unambiguous enough** — downstream work need not invent between materially different meanings;
- **consistent** — it does not contradict current accepted behavior;
- **non-prescriptive** — it avoids implementation choice unless externally required;
- **complete enough** — material negative/unknown/temporal/authority cases are explicit where needed.

Completeness is scope-relative, not encyclopedic.

## G1 — Requirements coherent

`G1 PASS` means S2 may rely on:

- explicit observable outcome and applicability;
- explicit material failure/denial/unknown behavior;
- material temporal/quality/security constraints where relevant;
- no unresolved P0/P1 product contradiction;
- no hidden downstream product decision;
- no architecture/implementation proposal promoted to product truth merely for convenience.

Outcomes:

- `PASS` — proceed to the next required/dirty stage;
- `REWORK` — S1 owns a correctable behavior/coherence gap;
- `REOPEN(S0)` — the problem/need/evidence is insufficient;
- `BLOCKED` — an external product decision/evidence is required.

A later stage uses `REOPEN(S1)` when it discovers that observable product behavior was never actually settled.

## Context rule

Load only root/scoped instructions, the active capsule when current execution depends on it, this protocol while S1/G1 is active, the owning requirements and additional current evidence only on demonstrated need.

On transition, accepted behavior stays in `docs/requirements/`; current blockers/next action stay only in the active plan/capsule while active. Discard temporary reasoning and rejected alternatives.

## Protocol ownership

- `change-lifecycle.md` — routing, gates, dirty/reopen/no-progress semantics;
- `decision-protocol.md` — statement classification and unknown/conflict handling;
- `working-loop.md` — checkpoints/validation/session rollover;
- `plan-lifecycle.md` — current active execution state.
