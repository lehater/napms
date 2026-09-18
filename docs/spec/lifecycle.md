# Lifecycle specification

Status: M1 COMPLETE — lifecycle contract defined; artifact schemas remain M2-owned.

## Purpose

Route a material change through the minimum semantic work required before implementation. Keep lifecycle coordination separate from stage-specific methods and artifact schemas so an agent can load only the current task contract.

## Lifecycle

```text
S0 Problem / Evidence          -> G0
S1 Requirements                -> G1
S2 Domain Design               -> G2
S3 Architecture                -> G3
S4 Implementation Readiness    -> G4
IMPLEMENTATION -> VALIDATION
```

This is not a waterfall. Start at the earliest stage whose accepted truth may change. Earlier accepted guarantees are inputs, not mandatory rework. Only affected downstream guarantees become dirty and require revalidation.

## Core model

- A **stage** creates or updates canonical knowledge for one semantic concern.
- An **artifact** materializes that knowledge in its canonical representation.
- A **gate** validates sufficient current evidence for the next stage; a gate is not a product artifact.
- A **change scope** is the smallest stable semantic slice being evaluated.
- **Implementation readiness** means an evaluated scope is executable and verifiable; it does not authorize an agent to modify product code.

Later stages must not invent unresolved truth owned by an earlier stage merely to continue.

## Stage contracts

| Stage | Owns | Minimum input | Exit guarantee |
|---|---|---|---|
| S0 Problem / Evidence | need, actors, outcome, evidence, externally imposed/non-negotiable constraints and unresolved problem questions | request, observation or conflicting evidence | the problem, its material external constraints and evidence are sufficiently bounded to derive requirements |
| S1 Requirements | observable functional behavior, quality requirements and acceptance intent | G0-accepted problem/constraint truth or already-valid equivalent | required behavior and applicable quality expectations are explicit, testable enough for domain work and solution-agnostic where practical |
| S2 Domain Design | domain responsibilities, language, semantics, ownership, boundaries and bounded contexts | applicable G1-accepted behavior | semantic ownership and boundaries are sufficient for architecture to realize without inventing domain truth |
| S3 Architecture | technical realization, system boundaries, interactions, contracts and significant technical decisions | applicable G1/G2 guarantees plus technical constraints | architecture and external/internal contracts are sufficient to prepare an implementation slice |
| S4 Implementation Readiness | exact implementation slice, dependencies, migrations, validation intent and execution order | applicable accepted upstream guarantees | one explicit implementation scope is executable and verifiable without unresolved P0/P1 design work |

Detailed working methods belong to stage-specific instructions. Artifact type definitions belong to `artifacts.md`.

## Gate contracts

| Gate | PASS means |
|---|---|
| G0 | current evidence and applicable externally imposed constraints justify requirements work for the selected problem scope |
| G1 | observable behavior, applicable qualities and acceptance intent are sufficient for domain design without redefining S0 constraints |
| G2 | affected domain semantics, responsibility and boundary ownership are sufficient for architecture |
| G3 | realization and contracts are sufficient to derive a concrete implementation-ready slice |
| G4 | the exact selected slice has sufficient current upstream evidence, dependencies and validation intent to be implementation-ready |

A gate evaluates only artifacts applicable to the current scope. `conditional` artifacts block only when their applicability condition is true. `optional` artifacts never become mandatory merely because a template exists.

## States

Stages use:

```text
NOT_STARTED
IN_PROGRESS
BLOCKED
GATE_FAILED
ACCEPTED
DIRTY
```

Gate outcomes are:

```text
PASS
REWORK
REOPEN(Sx)
BLOCKED
```

- `PASS` marks the stage `ACCEPTED` for the evaluated scope.
- `REWORK` means the deficiency belongs to the current stage; correct only that delta.
- `REOPEN(Sx)` means later work exposed missing or invalid truth owned by an earlier stage.
- `BLOCKED` means required truth cannot currently be derived; record the blocking question and stop that path.

## Dirty propagation and reopen

When accepted upstream truth materially changes:

1. identify downstream guarantees that actually depend on it;
2. mark only those guarantees `DIRTY`;
3. mark any dependent G4 readiness result invalid immediately;
4. reopen the owning stage;
5. resolve the smallest affected delta;
6. revalidate dirty downstream stages in dependency order.

Do not restart unaffected stages and do not treat `DIRTY` as proof that prior work is wrong.

## Implementation readiness and authorization

G4 PASS means the exact evaluated scope is implementation-ready. It does not grant permission to modify product code or product tests.

Implementation authorization is a separate operational/user decision and must be explicit for the requested scope. A prior authorization cannot be inferred from G4, a readiness artifact, or repository state.

A G4 readiness result becomes invalid when the scope changes materially, an upstream dependency becomes dirty, or implementation evidence exposes an unresolved earlier-stage decision. Re-establish readiness after the owning stage is resolved; obtain implementation authorization separately when code/test changes are requested.

## Validation feedback

Implementation and validation may expose defects in any earlier guarantee. Route the finding to the earliest owning stage rather than patching the later artifact to hide the inconsistency. Reopen/dirty rules then apply normally.

## Agent routing contract

A lifecycle router provides only:

```text
change-scope
current-stage
stage-state
applicable accepted upstream references
current gate or authorization state
blocking question, if any
primary stage instruction reference
artifact-type references required for the current task
next concrete task
```

The agent then loads only:

1. repository routing instructions;
2. this lifecycle contract only when routing/transition semantics are needed;
3. one primary stage/task instruction;
4. applicable artifact-type specifications;
5. the minimal current project working set;
6. additional evidence only when the task demonstrates need.

One agent execution should complete one concrete task or one gate evaluation, persist the durable result/state, and stop. It must not preload every stage protocol or the full artifact catalog.

## Ownership boundaries

This specification owns lifecycle routing, stage/gate semantics, dirty/reopen propagation and implementation readiness semantics.

It does **not** own:

- artifact schemas, applicability details or canonical formats — `artifacts.md`;
- physical paths and naming — `repository-layout.md`;
- detailed context loading and task execution — `agent-execution.md`;
- concrete automated checks — `validation.md`;
- migration from current documentation — `migration/plan.md`.

## M1 exit

M1 is complete when S0-S4 responsibilities, G0-G4 guarantees, states, reopen/dirty behavior, implementation readiness semantics and minimal agent routing data are defined without requiring detailed artifact schemas.
