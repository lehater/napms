---
name: user-journey-validation
description: "Use when validating one NAPMS user journey end-to-end from a user goal through the UI to a durable outcome. Assess journey completeness, usability, essential negative/recovery states and evidence; classify gaps P0-P3 and route them to the owning workflow. Do not invent product semantics or implement fixes as part of validation."
---

# User Journey Validation

## Responsibility

Decide whether one accepted user goal can be completed through the product interface without implementation knowledge or bypasses, and produce actionable evidence when it cannot.

## Inputs

- active plan and local journey gate when present;
- accepted product requirements and relevant UI guidance;
- explicit actor, start condition, goal and expected durable outcome;
- the running UI or other executable acceptance surface;
- the smallest fixture needed to exercise the journey.

## Procedure

1. State the journey boundary: actor, start state, goal, end state and required durable result.
2. Separate accepted behavior from assumptions. Route missing or conflicting product truth through `docs/process/decision-protocol.md`; do not invent behavior to make the journey pass.
3. Define the smallest representative fixture and happy path. Use user-facing names and concepts; stable IDs and backend details are diagnostic evidence, not required user knowledge.
4. Execute the journey through the same UI actions available to the actor. Direct API/database manipulation may prepare fixtures or diagnose a failure only when clearly separated from journey evidence.
5. At each step assess:
   - discoverability: the next useful action is understandable;
   - capability: the required action exists and is admitted correctly;
   - correctness: the resulting state matches accepted behavior;
   - feedback/recovery: loading, success, validation, cancellation, retry and failure states are understandable where material;
   - durability: saved state survives the reload/reopen boundary required by the journey.
6. Exercise the smallest negative and correction paths needed to prove the actor can recover from ordinary mistakes. Do not expand into exhaustive screen testing unrelated to the journey goal.
7. Classify findings P0-P3. P0/P1 prevent journey closure. Record the blocked step, observed result, expected accepted result and evidence.
8. Route gaps by owner:
   - missing/conflicting semantics, lifecycle, authority or ownership -> `domain-model-change` or `resolve-decision` as appropriate;
   - accepted behavior missing or incorrect in implementation -> the implementation workflow, using `implement-slice` when its vertical-slice boundary applies;
   - presentation/interaction defect with accepted semantics unchanged -> scoped Web work under the active plan and `web/AGENTS.md`.
9. After fixes, rerun from a clean representative start state. Do not infer closure from unit/component tests alone.
10. Once the journey is stable, add or refresh automated E2E regression for deterministic high-value paths when useful. Automation protects behavior; manual/judgement evidence remains the owner of usability conclusions.

## Journey gate

A journey passes only when:
- the goal is reachable end-to-end through the supported UI;
- the expected durable result can be reopened/reloaded as required;
- ordinary user mistakes have an understandable correction/recovery path where material;
- no P0/P1 journey findings remain;
- evidence identifies what was executed and the observed result;
- any automated regression claims are backed by executable tests.

## Output state

Keep visible: journey identifier/goal, fixture, executed path, P0-P3 findings, evidence, gate verdict and next owning workflow.
