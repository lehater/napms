# PLAN-016 — I16 Connectivity Decision Runtime and Workflow

Status: `active`

Date: 2026-09-09.

## Goal

Implement the I15 Connectivity Decision model end-to-end and remove the deterministic local allow adapter from the normal product journey.

## Current stage

WP3 — Access Policy integration remains active. WP4 Web UI Quality Gate is active and its functional/accessibility browser suite has passed; visual-regression baselines are being established before any new Decision UI. WP1 core and WP2 PostgreSQL gates passed.

## Inputs

- `docs/domain/connectivity-decision-model.md`;
- `docs/requirements/connectivity-decision-core.md`;
- `docs/requirements/connectivity-decision-acceptance-examples.md`;
- `docs/architecture/connectivity-decision-boundary.md`;
- `docs/decisions/ADR-004-connectivity-decision-bounded-context.md`.

## Work packages

### WP1 — Decision core — done
Implemented framework-free Domain/Application/Ports:
- immutable Decision aggregate/value types;
- DecideConnectivity / ReadConnectivityDecision authority;
- record/supersede;
- select effective decision;
- exact subject/scope/time and fail-closed ambiguity;
- core/architecture tests.

### WP2 — PostgreSQL — done
With core gate passed:
- module-owned schema/migration/repository;
- immutable history;
- concurrency-safe supersession/current selection;
- unknown commit/non-success semantics;
- PostgreSQL integration tests.

### WP3 — Access Policy integration — active
Evolve the consumer port from subject-only lookup to exact subject + governance scope + logical proposal time. Preserve Access Policy ownership and existing materialization semantics.

### WP4 — Web UI Quality Gate — active
Before adding new Decision UI:
- use the accepted desktop-first operational UI contract in `docs/requirements/web-ui-requirements.md`;
- treat NetBox only as a class-of-product UX reference: dense professional desktop operations, not a visual/IA clone;
- primary browser/visual target: 1440 x 900/1000 class;
- minimum desktop target: 1280 x 800;
- tablet/mobile are compatibility targets preserving the same IA through collapsed/off-canvas navigation;
- add Playwright browser E2E against the real Docker public endpoint;
- test real login, navigation, form controls, buttons, mutations, reload/persisted state and error states;
- use role/label-based selectors so missing accessible names are treated as defects rather than hidden by test IDs;
- add automated WCAG 2.2 AA checks for critical screens/states;
- capture screenshots/traces/videos on failure;
- establish committed pixel visual-regression baselines for stable desktop states plus selected narrow-screen compatibility states;
- classify discovered defects P0/P1/P2/P3 and fix P0/P1 before WP5.

Current evidence:
- functional/accessibility browser suite reached 5/5 PASS after fixing real contrast, accessible-name and mobile-navigation defects;
- visual-regression test is present;
- first baseline generation run intentionally fails until generated reference PNGs are committed and re-gated.

### WP5 — HTTP/Web participant workspace
Only after WP4 passes:
- decision scope/interaction discovery;
- direct final Allowed/NotAllowed recording;
- decision read/details and reason/provenance;
- explicit no-decision behavior in Compose Connectivity;
- no Pending/approval queue.

### WP6 — Composition/Docker/E2E
- seed usable Decision authority and a durable demo Decision path;
- remove `local-dev:allowed` from normal local composition;
- prove proposal -> durable Decision -> Rule and NotAllowed/no-materialization;
- public nginx smoke;
- keep the browser quality gate green against the durable Decision journey.

### WP7 — Closure
Architecture/security/UI-quality review, repository gates, roadmap/current-state absorption, active-plan removal and final squash merge.

## Exit criteria

1. Normal local product journey uses durable Connectivity Decision persistence, not `local-dev:allowed`.
2. Allowed/NotAllowed Decision identity/reason/provenance/validity/supersession are executable.
3. Access Policy selects exact effective Decision by subject + scope + proposal logical time.
4. Decision mutation/read authority is independent from proposal authority.
5. No approval queue or automatic Rule revocation is invented.
6. Playwright browser scenarios cover critical existing UI workflows, with P0/P1 UI defects closed.
7. Core/PostgreSQL/Web/browser/Docker/harness/knowledge gates pass.
8. I17 is promoted.

## Blockers

The execution sandbox cannot clone github.com directly. Core/infrastructure stage gates will therefore use the repository's PR CI as executable proof, with the PR returned to draft whenever material changes follow a gate.

## Next

Finish WP4 by committing the generated stable visual baselines and obtaining a green browser/visual gate. Then resume WP3 backend integration and proceed to new Decision UI only with the desktop-first quality contract continuously enforced.
