# PLAN-016 — I16 Connectivity Decision Runtime and Workflow

Status: `active`

Date: 2026-09-09.

## Goal

Implement the I15 Connectivity Decision model end-to-end and remove the deterministic local allow adapter from the normal product journey.

## Current stage

WP5 — HTTP/Web participant workspace is active. WP1 Decision core, WP2 PostgreSQL, WP3 Access Policy integration and WP4 Web UI Quality Gate are done and gated.

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

### WP3 — Access Policy integration — done
Implemented:
- Access Policy-owned Decision projection includes governance scope and validity;
- Decision lookup is exact subject + proposal governance scope + logical proposal time;
- Access Policy defensively fails closed on subject/scope mismatch and non-effective Decision;
- Decision BC selection is translated through an outer adapter, with no cross-BC import in Access Policy core;
- NotFound/Ambiguous selection remains explicit non-success through the existing DecisionUnknown materialization outcome;
- core/postgres/web/browser/docker/harness/knowledge gates pass.

### WP4 — Web UI Quality Gate — done
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
- expose accepted future user-facing roadmap capabilities as explicit `Preview · Planned Ixx` routes before baseline lock;
- preview routes must be navigable but must not fake runtime data, authority or successful mutations;
- establish committed pixel visual-regression baselines for the resulting full future shell, stable live desktop states and selected narrow-screen compatibility states;
- classify discovered defects P0/P1/P2/P3 and fix P0/P1 before WP5.

Current evidence:
- permanent browser suite passes 7/7 on the real Docker public endpoint;
- functional mutation/reload, error-state, accessibility and mobile off-canvas scenarios pass;
- preview routes are implemented for I16 Connectivity Decisions, I17 Technical Evidence, I18 Access Resolution, I19 Enforcement Placement, I20 Reconciliation, I21 Configuration Rendering, I22 Network Operations and I25 Explainability/Audit;
- I23/I24 are intentionally not fabricated as product pages without an accepted human workflow;
- committed Playwright pixel baselines cover Login, Compose desktop, Access Rules desktop and Compose mobile;
- baseline creation bootstrap was removed; the normal read-only browser gate verifies the committed images.

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

Implement WP5 Decision scope/interaction discovery, direct final Allowed/NotAllowed recording, authorized read/list/detail HTTP contracts and the executable desktop-first Decision workspace; keep the existing preview guardrails until each real action is wired.
