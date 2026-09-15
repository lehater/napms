# Problem / Evidence stage

## Purpose

Use S0 when a requested change is still an unclear need, observed defect, conflicting evidence, operational pain or external constraint whose target behavior is not yet sufficiently framed for Requirements.

S0 answers:

> What problem/change pressure is observed, for whom/where, what current evidence supports it, what outcome is sought, and what remains unknown?

S0 does not choose detailed product behavior, domain ownership, architecture or implementation.

## Inputs

Use only evidence needed to frame the current trigger:

- explicit user/stakeholder request;
- concrete examples or workarounds;
- defect/incident/runtime/test evidence;
- external compatibility/security/regulatory constraints;
- current product/repository behavior where relevant;
- current canonical contradictions that triggered revalidation;
- a later-stage `REOPEN(S0)` reason.

## Working loop

1. State the trigger neutrally without embedding a preferred solution.
2. Identify the affected actor/system/surface only as far as evidence supports it.
3. Collect the smallest decisive current evidence.
4. Separate accepted fact, constraint, hypothesis, unknown and conflict using `decision-protocol.md`.
5. State the desired problem-level outcome rather than an implementation mechanism.
6. Identify externally fixed constraints and explicit non-goals.
7. Resolve evidence contradictions needed to know what problem is being solved.
8. Ask/escalate only blocking questions required to enter Requirements honestly.
9. When active execution must resume later, keep the unresolved blocker/current evidence reference in the active capsule or plan; do not create a permanent evidence archive.
10. Evaluate G0.

If a stakeholder example contains a requirement-relevant fact that remains true for the current target, absorb that fact into the appropriate current requirements artifact once S1 accepts it. Do not preserve transcript fragments or duplicate source-evidence documents merely for historical traceability.

## G0 — Problem understood

`G0 PASS` means S1 may begin because:

- the current trigger/problem is explicit;
- desired outcome is distinguishable from a proposed solution;
- material current evidence/source can be identified;
- facts, hypotheses, unknowns and conflicts are separated;
- affected actor/surface/scope is clear enough to elicit observable behavior;
- no P0/P1 contradiction prevents understanding the problem.

G0 does not require final behavior, a complete journey inventory, domain design or architecture.

Outcomes:

- `PASS` — proceed to S1 when requirements work is needed;
- `REWORK` — S0 can improve framing with available evidence;
- `BLOCKED` — current evidence is insufficient; require new evidence/owner clarification rather than inventing truth.

## Context rule

Load only:

```text
root AGENTS.md
-> active capsule when current execution depends on it
-> scoped AGENTS.md when applicable
-> this protocol for active S0/G0 work
-> evidence directly relevant to the current problem
-> other canonical project evidence only on demonstrated need
```

Do not preload old conversations or broad repository history.

## Protocol ownership

- `change-lifecycle.md` owns routing/transitions/no-progress behavior;
- `decision-protocol.md` owns epistemic/semantic classification;
- `requirements-stage.md` owns S1;
- `plan-lifecycle.md` owns current active execution state.
