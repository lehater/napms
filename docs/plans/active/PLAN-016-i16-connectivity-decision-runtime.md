# PLAN-016 — I16 Connectivity Decision Runtime and Workflow

Status: `active`.

Date: 2026-09-09.

## Goal

Implement the I15 Connectivity Decision model end-to-end and remove the deterministic local allow adapter from the normal product journey.

## Current stage

WP1 — Domain/Application/Ports core and executable specifications. Infrastructure gate is closed until the core contract is proven.

## Inputs

- `docs/domain/connectivity-decision-model.md`;
- `docs/requirements/connectivity-decision-core.md`;
- `docs/requirements/connectivity-decision-acceptance-examples.md`;
- `docs/architecture/connectivity-decision-boundary.md`;
- `docs/decisions/ADR-004-connectivity-decision-bounded-context.md`.

## Work packages

### WP1 — Decision core
Implement framework-free Domain/Application/Ports:
- immutable Decision aggregate/value types;
- DecideConnectivity / ReadConnectivityDecision authority;
- record/supersede;
- select effective decision;
- exact subject/scope/time and fail-closed ambiguity;
- core/architecture tests.

### WP2 — PostgreSQL
After core gate:
- module-owned schema/migration/repository;
- immutable history;
- concurrency-safe supersession/current selection;
- unknown commit/non-success semantics;
- PostgreSQL integration tests.

### WP3 — Access Policy integration
Evolve the consumer port from subject-only lookup to exact subject + governance scope + logical proposal time. Preserve Access Policy ownership and existing materialization semantics.

### WP4 — HTTP/Web participant workspace
Add:
- decision scope/interaction discovery;
- direct final Allowed/NotAllowed recording;
- decision read/details and reason/provenance;
- explicit no-decision behavior in Compose Connectivity;
- no Pending/approval queue.

### WP5 — Composition/Docker/E2E
- seed usable Decision authority and a durable demo Decision path;
- remove `local-dev:allowed` from normal local composition;
- prove proposal -> durable Decision -> Rule and NotAllowed/no-materialization;
- public nginx smoke.

### WP6 — Closure
Architecture/security review, repository gates, roadmap/current-state absorption, active-plan removal and final squash merge.

## Exit criteria

1. Normal local product journey uses durable Connectivity Decision persistence, not `local-dev:allowed`.
2. Allowed/NotAllowed Decision identity/reason/provenance/validity/supersession are executable.
3. Access Policy selects exact effective Decision by subject + scope + proposal logical time.
4. Decision mutation/read authority is independent from proposal authority.
5. No approval queue or automatic Rule revocation is invented.
6. Core/PostgreSQL/Web/Docker/harness/knowledge gates pass.
7. I17 is promoted.

## Blockers

The execution sandbox cannot clone github.com directly. Core/infrastructure stage gates will therefore use the repository's PR CI as executable proof, with the PR returned to draft whenever material changes follow a gate.

## Next

Implement WP1 only, run the core PR gate, then open the infrastructure gate.
