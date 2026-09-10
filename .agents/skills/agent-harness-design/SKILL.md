---
name: agent-harness-design
description: "Use when designing, reviewing, or auditing the NAPMS repository environment for coding agents: AGENTS.md routing, Skills, active-plan continuity, process protocols, validators/evals and CI. Prefer the smallest change that removes demonstrated harness problems. Do not use for product/domain architecture."
---

# Agent Harness Design

## Audit dimensions

- startup/progressive disclosure;
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
- Skills are judgement-heavy reusable workflows; deterministic invariants belong in validators;
- extend before adding;
- no current project facts in reusable Skill bodies;
- completed audit artifacts are not permanent repository archives;
- before treating a required deterministic check as unavailable, inspect the applicable `.github/workflows/` definition and distinguish repository capability from connector/runtime capability;
- run `make harness-check` after changes, locally when possible or through the equivalent hosted workflow when local execution is unavailable.
