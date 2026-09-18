---
name: skill-design
description: "Use when admitting, reviewing, refactoring or validating one NAPMS repository Agent Skill. Decide whether the workflow deserves a Skill, keep its trigger distinct, keep current project truth out, and prefer extending an existing Skill over overlap."
---

# Skill Design

A workflow deserves a Skill only when it is repeatable, stable, distinguishable by prompt intent and judgement-heavy enough that a validator alone is insufficient.

Classify candidates as ADMIT, EXTEND, DEFER or REJECT.

Check:
- directory/frontmatter name match;
- trigger description clearly separates neighboring Skills;
- body owns reusable judgement, not current NAPMS facts;
- current owners are discovered through root `AGENTS.md` / `docs/canonical-graph.yaml`, not hard-coded into reusable workflow text;
- no retired gate/capsule/process instructions remain;
- routing corpus has positive and confusable-negative cases.

Run `python tools/validate_skill_routing.py` after routing changes. Use captured model-routing observations when actual routing behavior is under evaluation; corpus structure alone is not routing evidence.
