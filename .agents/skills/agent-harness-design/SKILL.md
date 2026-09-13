---
name: agent-harness-design
description: "Use when designing, reviewing, or auditing the NAPMS repository environment for coding agents: lifecycle stages/gates, context loading, AGENTS.md routing, Skills, active-plan continuity, process protocols, validators/evals and CI. Prefer the smallest change that removes demonstrated harness problems. Do not use for product/domain architecture."
---

# Agent Harness Design

## Start here

For lifecycle/routing changes, read `docs/process/change-lifecycle.md` first. Treat it as the top-level progression model; do not create a competing stage/gate algorithm inside a Skill.

Load only the protocol and project artifacts required by the current Harness task. Do not preload every process document merely because the task concerns Harness design.

## Audit dimensions

- stage/gate progression and upstream re-entry;
- no-invention and blocked-unknown handling;
- startup/progressive disclosure;
- context promotion/discard/rollover;
- current-plan recoverability;
- project truth vs process vs Skill ownership;
- Skill trigger overlap;
- validator/eval and CI alignment;
- CI discoverability: agents can find applicable hosted gates, exact triggers/commands and manual-dispatch fallback without blind repository scans;
- stale/dead paths and duplicated truth;
- unnecessary harness complexity.

Classify findings P0-P3.

## Rules

- one agent + repository instructions/Skills is the default;
- lifecycle protocols decide when work is required; Skills describe how to perform judgement-heavy reusable work;
- deterministic invariants belong in validators, not prose-only Skills;
- extend before adding;
- no current project facts in reusable Skill bodies;
- do not turn the conceptual lifecycle into a runtime workflow engine/state-machine framework without demonstrated need;
- durable accepted truth/problems/execution state must be promoted out of conversation history before context rollover;
- completed audit artifacts are not permanent repository archives;
- before treating a required deterministic check as unavailable, inspect the applicable `.github/workflows/` definition and distinguish repository capability from connector/runtime capability;
- run `make harness-check` after changes, locally when possible or through the equivalent hosted workflow when local execution is unavailable.
