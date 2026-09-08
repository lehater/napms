---
name: skill-design
description: "Use when admitting, reviewing, refactoring, or validating one NAPMS repository Agent Skill. Decide whether the workflow deserves a Skill, make its trigger/responsibility distinct, keep project truth out, ensure progressive disclosure and routing-eval coverage, and prefer extending an existing Skill over overlap."
---

# Skill Design

## Admission test

A workflow becomes a Skill only when it is:
- repeatable;
- stable enough to centralize;
- distinguishable by prompt intent;
- judgement-heavy enough that a validator alone is insufficient;
- valuable across multiple future tasks.

Classify a candidate as:
- **ADMIT** — new stable responsibility;
- **EXTEND** — existing Skill owns it;
- **PROTOCOL** — shared mechanics, deliberately non-routable;
- **DEFER** — plausible but insufficiently exercised;
- **REJECT** — trivial/one-off/overlapping.

## Acceptance

Check:
- directory and frontmatter name match;
- concise trigger description includes neighbor boundaries;
- body owns workflow, not current NAPMS facts;
- shared mechanics link to `docs/process/`;
- routing corpus includes positive and confusable negative cases;
- `make harness-check` passes.
