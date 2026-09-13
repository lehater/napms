# Change lifecycle

## Purpose

This protocol defines how a non-trivial change moves from accepted need to implementation readiness without allowing lower layers to invent unresolved higher-layer truth.

It is intentionally stage-level. Detailed methods for requirements, domain design, architecture and implementation planning belong in their own protocols/Skills and are loaded only when the current stage requires them.

This protocol is primarily a **transition protocol**: use it when entering a change, evaluating a stage gate, reopening an upstream stage, propagating invalidation, or selecting the next stage. It need not remain part of the working set throughout ordinary task execution once the current stage/task is unambiguous.

## Core invariants

1. A stage must not resolve an uncertainty owned by an earlier stage merely to keep work moving.
2. A later stage may rely only on guarantees that upstream gates have accepted against the current upstream inputs.
3. If an accepted upstream guarantee changes materially, every dependent downstream acceptance becomes `DIRTY` until revalidated.
4. If accepted repository truth and available evidence are insufficient, materialize the unknown as a problem, resolve or escalate it explicitly, and stop at the affected gate when it is blocking.
5. Repeating the same work without new evidence, model change, problem-state change or decision-state change is a blockage, not progress.
6. Implementation permission is scoped: a G4 acceptance authorizes only the implementation scope it evaluated and is revoked when a required upstream guarantee becomes dirty.

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
IMPLEMENTATION EXECUTION PERMITTED FOR THE G4 SCOPE
```

The sequence is not a waterfall. Work enters at the earliest affected stage, and later work may reopen any earlier stage whose guarantees prove incomplete or wrong.

Each semantic stage has exactly four conceptual elements:

```text
Inputs -> Work -> Outputs -> Gate
```

A gate evaluates whether the stage's knowledge is sufficiently coherent and complete for the next stage to rely on it. The existence of a document does not itself satisfy a gate.

Detailed stage decomposition (for example Strategic vs Tactical Domain Design) belongs to the stage methodology. The top-level lifecycle should gain another semantic stage only when a distinct cross-project gate and dependency boundary are demonstrated.

`IMPLEMENTATION` is an execution mode after G4, not a sixth semantic design stage.

## Stage routing

For every non-trivial change, determine the earliest layer whose accepted truth may need to change:

- implementation-only concern -> start at S4;
- architecture concern -> start at S3;
- domain semantic concern -> start at S2;
- accepted behavior/product concern -> start at S1;
- unclear/raw need or conflicting evidence -> start at S0.

When uncertain, enter earlier rather than silently deciding at a lower layer.

Starting at a later stage is valid only when the earlier-stage guarantees required by that stage already exist and remain applicable. If the work exposes a missing earlier guarantee, use `REOPEN(stage)`.

## Gate outcomes

A gate produces one of four outcomes.

### PASS

The stage is sufficient for the next stage to rely on its guarantees.

- mark the stage `ACCEPTED` against its current upstream inputs;
- record a concise `Lifecycle basis` in the active capsule that points to the accepted canonical/gate evidence supporting the state;
- close or downgrade gate findings that no longer block its guarantees;
- continue to the next required or dirty downstream stage.

For G4 specifically, PASS additionally creates a scoped implementation authorization as described under **Exit to implementation**.

### REWORK

The problem belongs to the current stage and can be resolved with current-stage responsibility/evidence.

- record concrete gate findings/problems;
- mark the stage `GATE_FAILED` while the blocking finding remains;
- repeat only the affected work;
- evaluate the gate again.

Do not restart the whole stage when a smaller delta is sufficient.

### REOPEN(stage)

The current stage exposed an invalid, incomplete or missing guarantee owned by an earlier stage.

- record the reason and affected problem;
- revoke any active G4 implementation authorization whose basis depends on the reopened guarantee;
- move the target owner stage to `IN_PROGRESS` (or `BLOCKED` when external knowledge is immediately required);
- mark every stage downstream of that owner whose accepted result depends on the changed/missing guarantee `DIRTY`, including the stage that detected the problem;
- return to the owner stage;
- after that stage passes, revalidate dirty downstream stages in dependency order before relying on their previous acceptance.

A reopen may target any earlier stage, not only the immediately preceding one. Do not mark unrelated downstream work dirty merely because it is later in the conceptual sequence; invalidation follows actual dependency on the changed guarantee.

Top-level `REOPEN(stage)` targets only S0-S4. Strategic/Tactical switching inside S2 is an internal S2 reroute, not a top-level reopen.

### BLOCKED

The current stage/gate cannot honestly proceed because required knowledge is unavailable and cannot be derived from accepted truth or current evidence.

- register the blocking unknown;
- mark the current stage `BLOCKED`;
- search the allowed evidence sources;
- if still unresolved, obtain an external decision from the appropriate owner;
- do not progress past the affected gate while the unknown remains blocking.

`BLOCKED` is both a gate outcome and a resumable stage state: the outcome explains why progression stopped; the state persists that condition until new evidence/decision arrives.

## Stage state

Track only the state needed to resume and route work:

- `NOT_STARTED` — no work required yet or not entered;
- `IN_PROGRESS` — current work is being performed;
- `BLOCKED` — progress requires unresolved external knowledge/decision;
- `GATE_FAILED` — current output is insufficient but can be reworked at this stage;
- `ACCEPTED` — current gate passed against its current upstream inputs;
- `DIRTY` — previously accepted output requires revalidation because an upstream guarantee it depends on changed.

Important distinctions:

- `DIRTY` means "must be revalidated", not "known wrong";
- `GATE_FAILED` means the current stage owns a correctable deficiency;
- `BLOCKED` means progress requires knowledge/decision not currently derivable by the stage;
- `ACCEPTED` is always relative to the upstream guarantees used when the gate passed.

When a dirty stage is revisited, first determine whether its previous output still satisfies the new upstream guarantees. Reuse it if valid; rework only the affected delta.

The active capsule's `Lifecycle basis` is the compact durable pointer to those current assumptions/evidence. It is not a substitute for canonical truth and must be refreshed when its referenced assumptions change.

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

### Where problems live

Do not create a universal problem database merely for this lifecycle.

- a problem blocking the current work belongs in the active plan/resume state until resolved or parked;
- a bounded-context-local unresolved problem that must survive parking belongs in that context's existing problem register;
- an accepted semantic decision belongs in its canonical requirements/domain/architecture/ADR owner, after which the temporary problem entry is closed or updated;
- if a durable problem does not fit an existing owner, keep it with the smallest current planning artifact until a repeated need justifies a dedicated repository structure.

The lifecycle defines problem semantics; `plan-lifecycle.md` owns persistence/parking mechanics.

## No-progress rule

Iteration is allowed only when it produces observable progress by changing at least one of:

- evidence;
- accepted model/knowledge;
- problem state;
- decision state;
- scope of the unresolved uncertainty.

Before another `REWORK` or evidence-search iteration, identify what new information or state change that iteration is expected to produce. If no such delta exists, do not repeat it.

If another iteration would repeat the same reasoning without changing any of these, stop. Record a no-progress blockage and require new evidence or an external decision instead of looping.

## Gate findings

Use the repository review severity model for gate findings:

- P0 — contradictory/impossible state; gate cannot pass;
- P1 — material unresolved ownership, behavior, boundary or implementation-readiness problem; gate cannot pass;
- P2 — non-blocking improvement or clarification;
- P3 — cosmetic/local polish.

A gate may pass with P2/P3 findings when its required guarantees are otherwise satisfied. P0/P1 findings affecting the gate guarantees prevent PASS unless the appropriate decision owner resolves them into accepted canonical truth. "Accepting the risk" must not be used to silently turn an unresolved required semantic guarantee into PASS.

## Context lifecycle

The change lifecycle is paired with a context lifecycle so agents do not preload every rule and artifact.

Use progressive disclosure:

```text
L0 repository routing/kernel
L1 current transition/stage protocol when needed
L2 current task methodology/primary Skill
L3 minimal project working set
L4 evidence loaded only on demonstrated need
L5 ephemeral analysis in the current conversation/session
```

A repository index or link may tell the agent where knowledge exists without loading its full content.

### Transition context vs working context

Keep stage-transition knowledge separate from ordinary task execution:

- **transition context** is needed to enter/reopen a stage, evaluate a gate, propagate dirty state or select the next stage;
- **working context** contains only the current stage/task method, scoped instructions, minimal project artifacts and evidence actually required for the task.

After a transition is recorded in durable state, a fresh working session should not need to carry the entire top-level lifecycle protocol unless another transition decision is being made.

### Startup

For a fresh session, preserve the repository's established routing order:

1. read the root repository agent map (`AGENTS.md`);
2. read the active resume capsule;
3. read the nearest scoped `AGENTS.md` when one applies;
4. determine the current task/stage/gate from the capsule and load the smallest applicable primary Skill;
5. load the capsule's minimal `Read first` working set;
6. load the relevant transition/stage protocol only when the task requires stage routing, gate evaluation, reopen/invalidation or when the capsule explicitly names it;
7. expand evidence lazily when the current problem demonstrates the need.

Do not preload protocols for future stages. Do not load the top-level lifecycle on every ordinary implementation/review task merely because it exists.

### Promotion and discard

Before changing stage/workstream or when context becomes costly, classify current conversational knowledge:

- accepted product/domain/architecture truth -> canonical artifact;
- unresolved material problem -> durable problem register or active plan state as appropriate;
- current task/stage/gate/next action -> active resume capsule;
- current lifecycle/implementation authorization basis -> compact references in the resume capsule;
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

Stage transition is therefore a strong rollover checkpoint, but not an unconditional requirement: if the existing conversation remains small and relevant, work may continue. The durable resume state must nevertheless be sufficient for a fresh session at any material transition.

A successful rollover must be able to resume without rereading the previous conversation.

## Exit to implementation

G4 does not create a repository-wide permission to edit code. It creates a **scoped implementation lease** for the exact slice/scope evaluated by S4.

After G4 PASS:

1. record the accepted S4/G4 result and required upstream/canonical references in the active plan/capsule;
2. move the capsule execution mode to `Lifecycle stage: IMPLEMENTATION`;
3. set `Implementation authorization: G4 PASS`;
4. set a non-`none` `Authorized scope` that identifies the implementation slice/scope;
5. set a non-`none` `Authorization basis` that identifies the G4/upstream evidence the authorization depends on;
6. only then route to an implementation Skill.

For a legitimately implementation-only change entering at S4, G4 is still required and creates the same scoped lease.

An implementation Skill must refuse or route back to S4 when:

- no G4 lease exists;
- the requested work is outside `Authorized scope`;
- the authorization basis is missing/stale/dirty;
- implementation evidence exposes a new upstream decision.

If implementation invalidates a required upstream guarantee, revoke the lease before reopening the owning stage. Preserve WIP only as recoverable branch state; do not resume the affected implementation scope until dependent stages are revalidated and a new applicable G4 lease exists.

The implementation-ready state must be strong enough that the implementer is not expected to invent unresolved requirements, domain ownership or architecture decisions while editing code.

## Relationship to other process protocols

- `decision-protocol.md` defines how known/hypothesis/unknown/conflict states are handled when resolving a problem.
- `domain-change-protocol.md` provides focused domain re-entry guidance and should align with this lifecycle rather than create a parallel progression model.
- `working-loop.md` owns branch/checkpoint/validation/session execution mechanics.
- `plan-lifecycle.md` owns durable active execution state, scoped G4 lease and parked problem/roadmap semantics.

This protocol owns stage progression, gate outcomes, upstream reopen/dirty propagation, no-progress handling and the minimal-context lifecycle around that progression.
