# Change lifecycle

## Purpose

This protocol defines how a non-trivial change moves from accepted need to implementation readiness without allowing lower layers to invent unresolved higher-layer truth.

It is intentionally stage-level. Detailed methods for requirements, domain design, architecture and implementation planning belong in their own protocols/Skills and are loaded only when the current stage requires them.

## Core invariant

A stage must not resolve an uncertainty owned by an earlier stage merely to keep work moving.

If accepted repository truth and available evidence are insufficient, materialize the unknown as a problem, resolve or escalate it explicitly, and stop at the affected gate when it is blocking.

## Lifecycle stages

The default conceptual sequence is:

```text
S0 Problem / Evidence
  -> G0
S1 Requirements
  -> G1
S2 Domain Design
  -> G2
S3 Architecture
  -> G3
S4 Implementation Readiness
  -> G4
CODE CHANGE PERMITTED
```

The sequence is not a waterfall. Work enters at the earliest affected stage, and later work may reopen any earlier stage whose guarantees prove incomplete or wrong.

Each stage has exactly four conceptual elements:

```text
Inputs -> Work -> Outputs -> Gate
```

A gate evaluates whether the stage's knowledge is sufficiently coherent and complete for the next stage to rely on it. The existence of a document does not itself satisfy a gate.

## Stage routing

For every non-trivial change, determine the earliest layer whose accepted truth may need to change:

- implementation-only concern -> start at S4;
- architecture concern -> start at S3;
- domain semantic concern -> start at S2;
- accepted behavior/product concern -> start at S1;
- unclear/raw need or conflicting evidence -> start at S0.

When uncertain, enter earlier rather than silently deciding at a lower layer.

## Gate outcomes

A gate produces one of four outcomes.

### PASS

The stage is sufficient for the next stage to rely on its guarantees.

- mark the stage accepted;
- continue to the next required or dirty downstream stage.

### REWORK

The problem belongs to the current stage.

- record concrete gate findings/problems;
- repeat only the affected work;
- evaluate the gate again.

Do not restart the whole stage when a smaller delta is sufficient.

### REOPEN(stage)

The current stage exposed an invalid, incomplete or missing guarantee owned by an earlier stage.

- record the reason and affected problem;
- mark the owner stage and dependent downstream stages dirty;
- return to the owner stage;
- after that stage passes, revalidate affected downstream stages in dependency order.

A reopen may target any earlier stage, not only the immediately preceding one.

### BLOCKED

The gate cannot honestly pass because required knowledge is unavailable and cannot be derived from accepted truth or current evidence.

- register the blocking unknown;
- search the allowed evidence sources;
- if still unresolved, obtain an external decision from the appropriate owner;
- do not progress past the gate while the unknown remains blocking.

## Stage state

Track only the state needed to resume and route work:

- `NOT_STARTED` — no work required yet or not entered;
- `IN_PROGRESS` — current work is being performed;
- `BLOCKED` — progress requires unresolved external knowledge/decision;
- `GATE_FAILED` — current output is insufficient but can be reworked at this stage;
- `ACCEPTED` — current gate passed against its current upstream inputs;
- `DIRTY` — previously accepted output requires revalidation because an upstream dependency changed.

An upstream semantic change marks dependent downstream stages `DIRTY`, not automatically wrong. Revalidate them before relying on their previous acceptance.

## Problem and unknown handling

Every material unresolved issue must be classified rather than hidden in conversation history.

A useful problem record contains:

- stable problem/question identifier when durable tracking is warranted;
- stage where it was detected;
- stage that owns the missing decision/truth;
- question or contradiction;
- why it matters to the current gate;
- evidence already inspected;
- what is still missing;
- blocking vs deferred status;
- next resolution action.

Classify unknowns as:

- **blocking** — required to pass the current gate; resolve/escalate now;
- **deferred-required** — not needed for the current gate but required by a known later stage; register and continue;
- **non-required** — not material to the current change; do not expand context merely to answer it.

Prefer existing canonical truth and authoritative evidence before asking for a new decision. Current implementation is evidence of current behavior, not automatic target truth.

## No-progress rule

Iteration is allowed only when it produces observable progress by changing at least one of:

- evidence;
- accepted model/knowledge;
- problem state;
- decision state;
- scope of the unresolved uncertainty.

If another iteration would repeat the same reasoning without changing any of these, stop. Record a no-progress blockage and require new evidence or an external decision instead of looping.

## Gate findings

Use the repository review severity model for gate findings:

- P0 — contradictory/impossible state; gate cannot pass;
- P1 — material unresolved ownership, behavior, boundary or implementation-readiness problem; gate cannot pass;
- P2 — non-blocking improvement or clarification;
- P3 — cosmetic/local polish.

A gate may pass with P2/P3 findings when its required guarantees are otherwise satisfied. P0/P1 findings affecting the gate guarantees prevent PASS unless explicitly accepted by the appropriate decision owner and recorded in canonical truth.

## Context lifecycle

The change lifecycle is paired with a context lifecycle so agents do not preload every rule and artifact.

Use progressive disclosure:

```text
L0 Harness kernel/routing
L1 current stage protocol
L2 current task methodology/primary Skill
L3 minimal project working set
L4 evidence loaded only on demonstrated need
L5 ephemeral analysis in the current conversation/session
```

A repository index or link may tell the agent where knowledge exists without loading its full content.

### Startup

For a fresh session:

1. read the repository agent map;
2. read the active resume capsule;
3. determine current stage, gate and task;
4. load only the current stage protocol;
5. load the smallest applicable primary Skill;
6. load only the capsule's minimal `Read first` working set;
7. expand evidence lazily when the current problem demonstrates the need.

Do not preload protocols for future stages.

### Promotion and discard

Before changing stage/workstream or when context becomes costly, classify current conversational knowledge:

- accepted product/domain/architecture truth -> canonical artifact;
- unresolved material problem -> durable problem register or active plan state as appropriate;
- current task/stage/gate/next action -> active resume capsule;
- evidence references worth preserving -> canonical artifact/problem record/plan as appropriate;
- temporary reasoning, tool dumps, duplicated explanation, rejected exploration -> discard.

No durable project fact or blocker may exist only in conversation history.

### Rollover

A fresh session is the reliable unload mechanism for model context. After durable promotion/checkpointing, prefer rollover when:

- the semantic stage changes;
- the workstream/task changes materially;
- loaded evidence/rules no longer belong to the current task;
- the conversation is dominated by stale exploration or large tool output;
- continuing would require carrying substantially more context than a fresh session reconstructed from durable state.

A successful rollover must be able to resume without rereading the previous conversation.

## Exit to implementation

Code modification is authorized only when the applicable implementation-readiness gate passes.

The implementation-ready state must be strong enough that the implementer is not expected to invent unresolved requirements, domain ownership or architecture decisions while editing code.

Implementation may still discover new evidence. If that evidence invalidates an earlier guarantee, use `REOPEN(stage)` and return through the lifecycle rather than patching around the semantic gap.

## Relationship to other process protocols

- `decision-protocol.md` defines how known/hypothesis/unknown/conflict states are handled when resolving a problem.
- `domain-change-protocol.md` provides focused domain re-entry guidance and should align with this lifecycle rather than create a parallel progression model.
- `working-loop.md` owns branch/checkpoint/validation/session execution mechanics.
- `plan-lifecycle.md` owns durable active execution state and parked problem/roadmap semantics.

This protocol owns stage progression, gate outcomes, upstream reopen/dirty propagation, no-progress handling and the minimal-context lifecycle around that progression.
