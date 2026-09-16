# Agent execution specification

Status: M4 COMPLETE — task-local execution and context-loading contract defined; concrete checks remain M5-owned.

## Purpose

Keep agent work task-local and context-bounded while preserving lifecycle correctness. The lifecycle may span many stages; one agent execution should solve one concrete task with the smallest sufficient instruction and evidence set.

## Execution unit

The default execution unit is a **task capsule**:

```text
one change scope
+ one current lifecycle stage
+ one concrete task or gate evaluation
+ one primary instruction/skill
+ explicit applicable artifact types
+ minimal project working set
+ explicit validation intent
= one bounded agent execution
```

A capsule is coordination state, not canonical product truth.

## Execution flow

```text
route request/change
-> identify earliest affected stage
-> select one concrete task
-> construct task capsule
-> load repository routing
-> load one primary task/stage instruction
-> load only applicable artifact specifications
-> load minimal canonical project evidence
-> perform one task
-> run task-local validation
-> persist canonical result and lifecycle state
-> record unresolved/blocking findings
-> stop
```

A new capsule is selected explicitly for the next task. Do not silently continue through the entire lifecycle in one context merely because the next stage is known.

## Routing inputs

The router should require only:

```text
change-scope
change-kind / observed delta
known affected artifact ids or paths, if any
current lifecycle state, if any
active implementation authorization, if any
explicit user/task intent
```

From these it derives:

```text
earliest-affected-stage
current-task
primary-instruction
applicable-artifact-types
minimal-upstream-references
validation-profile
```

If the earliest stage cannot be determined without domain evidence, route to a narrow classification task rather than loading all stages.

## Task capsule contract

A durable/serializable capsule should be representable as:

```yaml
scope: <stable semantic scope>
stage: S2
state: IN_PROGRESS
task: <one concrete outcome>
primary_instruction: <skill/protocol id>
artifact_types:
  - domain-model
inputs:
  - <canonical artifact ref>
outputs:
  - <expected canonical artifact ref/type>
validation_profile:
  - <rule/profile id>
blockers: []
next: <single next task or null>
```

This is a target data contract, not yet a committed schema. Machine-readable implementation is introduced only after M5 validates what fields automation actually needs.

## Instruction loading order

Load instructions in this order and stop when sufficient:

1. repository-level routing/invariants (`AGENTS.md`-equivalent);
2. task capsule;
3. one primary stage/task skill or protocol;
4. artifact-type specification entries explicitly required by the task;
5. canonical upstream artifacts explicitly referenced by the capsule;
6. affected current canonical artifacts;
7. implementation/source evidence only when the task requires realization evidence;
8. additional instructions/evidence only after a concrete gap is identified.

Do not preload sibling skills, all stage protocols, the full artifact catalog, all bounded-context documentation or historical plans.

## Primary instruction rule

Every task has one primary instruction/skill. Secondary instructions are loaded only for a demonstrated cross-cutting concern that the primary instruction cannot resolve.

Examples:

```text
Task: clarify observable requirement
Primary: requirements-stage
Artifacts: functional-requirement + applicable acceptance/quality entries
```

```text
Task: update one bounded-context semantic model
Primary: domain-design-stage
Artifacts: domain-model + only applicable context/state/trace entries
```

```text
Task: validate HTTP boundary change
Primary: architecture-stage or contract-specific skill
Artifacts: http-contract + directly affected architecture/domain references
```

Avoid meta-skills that merely load several other skills. Routing should select the narrowest capable primary instruction.

## Context budget model

Context is expanded by **need**, not by repository adjacency.

### Base set

Always small:

```text
repository invariants
+ capsule
+ primary instruction
```

### Working set

Add only:

```text
applicable artifact-spec entries
+ direct canonical inputs
+ artifact being changed
```

### Expansion set

Load only when a concrete question cannot be answered from the working set, for example:

- ownership ambiguity requires the context map;
- a contract change requires the directly related architecture flow;
- implementation evidence contradicts accepted design;
- a gate check requires one missing conditional artifact;
- a referenced identifier cannot be resolved.

When expansion occurs, record the reason in execution evidence when it materially affects routing or a gate decision.

## Search before broad load

When the exact artifact path is unknown, search metadata/indexes first. Fetch the matching artifact, not the entire directory tree. Machine-readable catalog/index support should make this deterministic after M5/M6 implementation.

## Canonical precedence

When sources conflict, precedence is:

```text
current canonical artifact
> accepted lifecycle/gate state derived from canonical evidence
> active task capsule / implementation plan
> generated projection/index
> historical/retired material
```

A capsule may point to truth but cannot override it.

## One-task completion rule

A task is complete when:

- its declared output exists or the requested evaluation is recorded;
- task-local validation passes or explicit blockers are persisted;
- any lifecycle state transition is recorded;
- discovered upstream semantic gaps are routed through `REOPEN(Sx)` rather than patched locally;
- the next task, if known, is named but not automatically executed in the same capsule.

Small mechanical substeps required to produce the single output are part of the same task; unrelated semantic decisions are not.

## Stop and reopen behavior

Stop the current task when:

- required canonical input is missing or contradictory;
- the task discovers unresolved truth owned by an earlier stage;
- scope materially expands beyond the capsule;
- a conditional artifact becomes applicable but requires a distinct semantic task;
- implementation authorization becomes invalid;
- validation exposes a P0/P1 issue outside the current task ownership.

Persist the finding and route the next capsule to the owning stage/task. Do not resolve it opportunistically under the wrong instruction.

## Persistence and handoff

At the end of a capsule persist only durable state:

```text
canonical artifact delta
lifecycle/gate state delta
validation result/reference
blocker/reopen finding, if any
next concrete task
```

Do not preserve chain-of-thought, exploratory reasoning, redundant summaries or copied upstream content as project knowledge.

A stage handoff references accepted outputs by stable identifiers/paths. The next stage loads those references only when its task requires them.

## Relationship to plans

An active plan coordinates a multi-task increment and may hold capsule-level execution state. It does not become a parallel specification. When a task establishes durable truth, update the canonical owner immediately; do not defer truth into a growing plan document.

Plans should remain concise: scope, current stage/state, blockers, completed increments, next concrete task and authorization state.

## Relationship to Harness

Harness responsibilities are:

- route requests to the earliest affected lifecycle stage;
- select the narrowest capable skill/instruction;
- construct/validate the task capsule;
- resolve canonical artifact references using catalog/layout metadata;
- prevent unauthorized implementation before G4;
- enforce stop/reopen rules;
- expose CI/validation capabilities relevant to the current task;
- persist only the required execution/lifecycle state.

Harness should not contain duplicated domain/product truth or large embedded process manuals.

## Relationship to CI

CI is validation/execution infrastructure, not an agent memory substitute. The task capsule/primary instruction should expose relevant existing checks so the agent can use them rather than rediscovering repository automation.

An agent must know, through repository/Harness routing metadata, which validation profiles CI will run for its changed artifact types. It should run the narrowest practical local/pre-commit checks first; authoritative repository CI remains final integration evidence where configured.

M5 defines the validation profiles and which checks are local, CI, gate-level or generated-index checks.

## Parallel work

Parallel agents are safe only when capsules have non-overlapping semantic ownership or explicit coordination. Do not parallelize two tasks that can independently change the same canonical truth. Integration validation occurs after their outputs meet at a shared boundary.

## Machine-readable direction

The eventual routing layer should derive capsules from small machine-readable registries rather than parsing large prose documents. Candidate registries are:

```text
lifecycle metadata
artifact catalog
repository layout/path rules
validation profiles
skill/task routing map
```

Do not encode these registries until their fields stabilize through M5 and the M7 pilot.

## M4 exit

M4 is complete when routing inputs, one-task capsule semantics, instruction selection, progressive context loading, expansion rules, persistence/handoff, stop/reopen behavior and Harness/CI responsibilities are defined without implementing the validators or migrating product documentation.
