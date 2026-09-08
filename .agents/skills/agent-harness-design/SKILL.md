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
- validators/evals and CI alignment;
- stale/dead paths and duplicated truth;
- unnecessary harness complexity.

Classify findings P0-P3.

## Rules

- one agent + repository instructions/Skills is the default;
- Skills are judgement-heavy reusable workflows; deterministic invariants belong in validators;
- extend before adding;
- no current project facts in reusable Skill bodies;
- completed audit artifacts are not permanent repository archives;
- run `make harness-check` after changes.
