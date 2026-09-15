---
name: agent-harness-design
description: "Use when designing, reviewing, or auditing the NAPMS repository environment for coding agents: context loading, AGENTS routing, Skills, lifecycle/gates, active-plan continuity, process protocols, validators/evals and CI. Prefer the smallest change that removes demonstrated Harness problems. Do not use for product/domain architecture."
---

# Agent Harness Design

## Start here

Classify the Harness concern before loading process detail.

- For startup/context loading, AGENTS/Skill routing, validator/eval or CI discoverability work, stay task-local and do not preload the product change lifecycle.
- Load `docs/process/change-lifecycle.md` only when the Harness change actually modifies or evaluates S0-S4/G0-G4 progression, reopen/dirty propagation or implementation-lease semantics.
- Load only the additional protocol/project artifacts required by the demonstrated Harness problem.

## Audit dimensions

- stage/gate progression and upstream re-entry;
- no-invention and blocked-unknown handling;
- startup/progressive disclosure;
- context promotion/discard/rollover;
- current-plan recoverability without forcing current-plan context into unrelated tasks;
- project truth vs process vs Skill ownership;
- Skill trigger overlap;
- validator/eval and CI alignment;
- CI discoverability: agents can find applicable hosted gates, exact triggers/commands and manual-dispatch fallback without blind repository scans;
- stale/dead paths and duplicated truth;
- unnecessary Harness complexity.

Classify findings P0-P3.

## Rules

- one agent + repository instructions/Skills is the default;
- lifecycle protocols decide when product lifecycle work is required; Skills describe judgement-heavy reusable work;
- deterministic invariants belong in validators, not prose-only Skills;
- deterministic routing-corpus validation is not evidence that a model routed correctly; score actual observations separately when routing behavior is under test;
- extend before adding;
- no current project facts in reusable Skill bodies;
- do not turn the conceptual lifecycle into a runtime workflow engine/state-machine framework without demonstrated need;
- durable accepted truth/problems/execution state must be promoted out of conversation history before context rollover;
- completed audit artifacts are not permanent repository archives;
- before treating a required deterministic check as unavailable, inspect the applicable `.github/workflows/` definition and distinguish repository capability from connector/runtime capability;
- run `make harness-check` after changes, locally when possible or through the equivalent hosted workflow when local execution is unavailable.
