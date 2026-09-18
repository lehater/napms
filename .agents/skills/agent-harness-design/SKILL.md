---
name: agent-harness-design
description: "Use when designing, reviewing or auditing the NAPMS repository environment for coding/design agents: context loading, AGENTS routing, Skills, canonical graph navigation, validators/evals and CI. Prefer the smallest change that removes a demonstrated problem. Do not use for product/domain architecture."
---

# Agent Harness Design

Start from root `AGENTS.md`, `docs/canonical-graph.yaml` and the specific agent/CI files implicated by the problem. Do not preload historical H/CM process records.

Audit:
- startup and progressive disclosure;
- canonical-owner routing and affected dependency discovery;
- workstream resume behavior;
- Skill trigger overlap and stale instructions;
- validator/CI discoverability and exact commands;
- duplicated/stale truth or generated output presented as authority;
- unnecessary Harness complexity.

Rules:
- one agent plus repository instructions/Skills is the default;
- deterministic invariants belong in small validators;
- no task capsules, lifecycle engines, gate state machines or universal design DSL without demonstrated independent need;
- durable current truth/state lives in canonical owners/workstream state, not chat;
- completed audit/migration artifacts are history, not normal workflow;
- inspect `.github/workflows/` before claiming a repository check is unavailable;
- run `make design-check` after changes that affect normal design navigation/control;
- run `python tools/validate_skill_routing.py` when Skill routing metadata/corpus changes.
