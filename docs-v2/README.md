# Documentation System v2

Status: DRAFT / non-canonical.

This tree designs the next documentation and engineering-artifact system before any product knowledge is migrated.

Until explicit cutover, `docs/` remains the canonical project knowledge base. Agents and implementation work MUST NOT treat `docs-v2/` as product truth.

## Durable META coordination

The current Documentation System v2 / Harness redesign roadmap is machine-readable and repository-resident:

- `docs-v2/meta/roadmap.yaml` — ordered redesign phases, dependencies, exit criteria and test-first policy;
- `docs-v2/meta/workstream-state.yaml` — current phase/task, completed work, blockers, authorization state and next task.

A new chat/session must read the workstream state first and use the roadmap to resolve dependencies. Conversation history is not the source of execution state.

## Design goals

- lifecycle stages produce durable canonical artifacts; gates validate their sufficiency;
- requirements remain solution- and bounded-context-agnostic until domain design establishes boundaries;
- every Design Anchor is expected to acquire a canonical machine-readable representation as the redesign progresses;
- prefer established machine-readable standards/DSLs where they preserve the required semantics;
- load only the protocol, artifact specification and project evidence required by the current task;
- one agent execution performs one concrete task and persists its result before moving on;
- generated views are never canonical when a source artifact exists;
- optional structure is created only when needed;
- define Harness conformance/eval cases before future runtime implementation, then implement against those checks after explicit authorization.

## Legacy design workstreams

The original M0-M7 sequence remains historical input to the redesign:

1. M0 — charter and invariants.
2. M1 — lifecycle skeleton.
3. M2 — artifact model and catalog.
4. M3 — repository layout and naming.
5. M4 — agent execution and progressive disclosure.
6. M5 — validation and CI/gate model.
7. M6 — migration and cutover plan.
8. M7 — pilot on one bounded vertical slice.

M7 exposed structural gaps in the earlier specification. The active continuation is therefore governed by `meta/roadmap.yaml`; existing M1-M6 specifications are inputs that may be revised, not frozen final contracts.

The files under `spec/` are design specifications. Product implementation remains out of scope for the current documentation-design work.
