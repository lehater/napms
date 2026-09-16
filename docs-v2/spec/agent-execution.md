# Agent execution specification

Status: SKELETON — M4 owns completion.

## Purpose

Keep agent work task-local and context-bounded while preserving lifecycle correctness.

## Execution skeleton

```text
route request
-> identify earliest affected stage
-> select one concrete task
-> load repository routing
-> load current stage protocol
-> load primary task/artifact instruction
-> load minimal project working set
-> perform one task
-> validate task result
-> persist canonical result / execution state
-> stop or select next task explicitly
```

## Context invariants

- progressive disclosure is mandatory;
- do not preload all lifecycle, artifact or bounded-context documentation;
- task instructions must reference required upstream artifact types rather than requiring broad repository reading;
- expand context only when current evidence demonstrates a need;
- canonical artifacts outrank plan/capsule summaries;
- machine-readable artifact metadata should support deterministic routing where practical.

## M4 must define

Routing inputs, task contract, instruction/Skill selection, context budget, working-set expansion rules, persistence/checkpoint rules, handoff between stages and relationship to Harness/CI.