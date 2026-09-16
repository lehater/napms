# Documentation System v2

Status: DRAFT / non-canonical.

This tree designs the next documentation and engineering-artifact system before any product knowledge is migrated.

Until explicit cutover, `docs/` remains the canonical project knowledge base. Agents and implementation work MUST NOT treat `docs-v2/` as product truth.

## Design goals

- lifecycle stages produce durable canonical artifacts; gates validate their sufficiency;
- requirements remain solution- and bounded-context-agnostic until domain design establishes boundaries;
- prefer machine-readable canonical artifacts where a useful standard notation exists;
- load only the protocol, artifact specification and project evidence required by the current task;
- one agent execution performs one concrete task and persists its result before moving on;
- generated views are never canonical when a source artifact exists;
- optional structure is created only when needed.

## Design workstreams

1. M0 — charter and invariants.
2. M1 — lifecycle skeleton.
3. M2 — artifact model and catalog.
4. M3 — repository layout and naming.
5. M4 — agent execution and progressive disclosure.
6. M5 — validation and CI/gate model.
7. M6 — migration and cutover plan.
8. M7 — pilot on one bounded vertical slice.

The files under `spec/` are design specifications. They are intentionally skeletal until their dedicated iteration is executed.