# PLAN-015 — I15 Connectivity Decision Domain Closure

Status: `active`.

Date: 2026-09-09.

## Goal

Close the deferred Connectivity Decision domain so I16 can implement a durable non-local decision provider without inventing business semantics in runtime code.

## Scope

In scope:
- Strategic DDD disposition and semantic ownership;
- Tactical DDD for decision identity, subject, outcome, validity, reason/provenance and supersession;
- relationship to Access Rule Proposal, Connectivity Requirement, Authority Management and Access Policy;
- authority actions and fail-closed semantics;
- requirements and acceptance examples;
- architecture/ADR contract for the future I16 runtime.

Out of scope:
- PostgreSQL/runtime/Web implementation;
- approval queue UI;
- quorum/SoD unless domain evidence requires it;
- enterprise IdP/source integration;
- automatic Access Rule revocation/change management.

## Inputs

- `docs/domain/deferred-connectivity-decision.md`;
- `docs/decisions/ADR-003-connectivity-decision-port.md`;
- current Connectivity Requirements and Access Policy canonical truth;
- I15 roadmap questions in `docs/engineering/post-wave1-product-completion-roadmap.md`.

## Work packages

### WP1 — Semantic closure
Resolve:
- whether Connectivity Decision is a first-class Bounded Context;
- stable decision identity vs decision subject;
- governance scope;
- final outcome vocabulary;
- human/automatic/mixed participation;
- quorum/SoD disposition.

Exit: no unresolved strategic blocker for Tactical DDD.

### WP2 — Tactical model
Define:
- immutable Decision record;
- validity/effective-time semantics;
- reason and evidence references;
- decision provenance;
- reconsideration/supersession invariants;
- selection/consumption rules.

Exit: model is precise enough for executable specifications without persistence assumptions.

### WP3 — Product requirements
Record testable behavior and acceptance examples, including:
- authority separation from proposal authority;
- Allowed/NotAllowed handling;
- missing/ambiguous decision behavior;
- requirement evidence without `Required == Authorized`;
- historical immutability and supersession.

### WP4 — Architecture contract
Replace the temporary external/deferred semantic disposition with a durable owner boundary and consumer port contract while keeping Access Policy independent of Decision internals.

### WP5 — Closure
- consistency review across domain/requirements/architecture;
- update roadmap/current-state;
- run repository-local harness/knowledge gates;
- remove absorbed active-plan artifacts;
- final PR gate.

## Exit criteria

I15 is complete when:
1. Connectivity Decision ownership is explicit in Strategic DDD;
2. Tactical semantics answer every I15 roadmap question;
3. requirements/acceptance examples are testable;
4. ADR/architecture define the I16-compatible boundary;
5. no I15 runtime behavior is invented in Access Policy;
6. repository gates pass;
7. I16 is promoted as next roadmap increment.
