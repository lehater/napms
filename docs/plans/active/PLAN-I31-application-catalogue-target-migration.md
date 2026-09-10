# I31 Application Catalogue Target Migration

Status: `active`.

Date: 2026-09-10.

## Goal

Implement the accepted PR #57 Application Definition / Application Deployment target from domain model through HTTP and Web while preserving existing downstream semantic identities, historical references and repository execution discipline.

The implementation is intentionally staged. Domain/contract uncertainty is resolved before infrastructure or Web work, and each coherent semantic stage is integrated through its own squash PR.

## Inputs

Canonical target:
- `docs/decisions/ADR-012-application-definition-deployment-model.md`;
- `docs/ui/application-catalogue-target.md`;
- `docs/ui/application-catalogue-wireframes.md`.

Current runtime truth and constraints:
- `docs/domain/application-communication-catalogue/tactical-model.md`;
- `docs/architecture/current-architecture.md`;
- `docs/decisions/ADR-011-i27-external-correlation-reference-input.md`;
- `src/napms/application_catalogue/`;
- `src/napms/runtime/catalogue_curation_http.py`;
- `src/napms/runtime/catalogue_application_workspace_http.py`;
- `web/src/features/catalogues/`;
- `e2e/test_j01_application_authoring.py`;
- downstream users of `DirectedInteractionIdentity` / `RuleSemanticIdentity`.

Execution roadmap:
- `docs/engineering/application-catalogue-target-migration-roadmap.md`.

## WP-0 — close target/migration contract

Responsibility: remove blocking semantic ambiguity before code migration.

Outputs:
- accepted compatibility projection from target Deployment Interaction to downstream stable interaction identity;
- canonical edit semantics for Interaction Definitions already used by active Deployments;
- canonical ownership/value semantics for Application `description/domain/owner`, Component `type/description`, and Deployment `company/environment/scope` fields required by the accepted UI;
- canonical active-reference retirement dependency rules and dependency projection;
- updated Tactical DDD / requirements / architecture / ADR / engineering API contract where each decision is owned;
- roadmap/capsule refreshed with the selected implementation boundary.

Local exit: no P0 unknown/conflict from the roadmap remains necessary to design domain/application code.

## WP-1 — domain, application and ports

Responsibility: implement the target ACC model without transport, persistence or Web coupling.

Outputs:
- target entities/value types/invariants for Interaction Definition, Application Deployment and Deployment Interaction;
- interaction-scoped source/destination Resource-binding semantics;
- task-oriented commands and bounded query ports;
- retirement dependency semantics;
- ACC-owned compatibility-projection port preserving downstream stable identity;
- domain/application/architecture tests.

Local exit: target use cases and compatibility identity are executable in memory and existing downstream contracts require no rewrite.

## WP-2 — PostgreSQL and compatibility projection

Responsibility: persist target truth additively and realize the selected downstream compatibility mapping.

Outputs:
- additive migrations and repository adapters;
- preserved legacy Component Deployment, DCS revision and binding IDs/facts;
- no inference of Company/Environment/Scope or target interaction ownership from legacy display names;
- deterministic persistence/concurrency/idempotency behavior;
- migration replay, repository integration and compatibility-projection tests.

Local exit: fresh target data and existing legacy data coexist without identity rewrite or ambiguous projection.

## WP-3 — HTTP and bounded read models

Responsibility: expose task-oriented target commands and scalable projections for the accepted UX.

Outputs:
- Definition list/detail projections with separately paged Components, Interactions and Deployments;
- global Application Deployment list/detail;
- paged Deployment connectivity rows and Resource-set drill-downs;
- server search/filter/stable sort/paging and totals required by the wireframes;
- task commands for target creation/edit/selection/binding flows;
- structured blocked-retirement dependencies;
- new product API does not expose compatibility Component Deployment IDs as authoring concepts;
- HTTP contract/security/integration tests.

Local exit: the accepted UI can be implemented without client-side whole-catalogue loading or client-manufactured internal identity combinations.

## WP-4 — Web target

Responsibility: replace the current I27 Applications projection with the accepted target information architecture.

Outputs:
- `Definitions | Deployments` working sets;
- Definition Overview / Components / Interactions / Deployments tabs;
- compact component and interaction authoring/edit surfaces;
- Application Deployment connectivity table with Resource counts;
- Resource-set drill-down and Add interaction flow;
- blocked-retirement dependency UX;
- normal working views exclude Retired entities and omit internal version/UUID noise;
- no hard-delete action;
- `make web-check` evidence.

Local exit: representative target user flow matches the accepted wireframes semantically and remains bounded for large datasets.

## WP-5 — journeys, screenshots and absorption

Responsibility: prove the new authoring projection and the unchanged downstream behavior end to end.

Outputs:
- J01 rewritten around Definition -> Components -> Interaction Definitions -> Application Deployment -> selected interactions -> Resource sets;
- target-authored interaction proven through existing Connectivity / final Decision / Access Policy paths as applicable;
- representative deterministic screenshot regressions for accepted Application Catalogue screens;
- Docker/local journey evidence;
- applicable hosted gates inspected and passed before final integration;
- current-state/engineering/canonical documentation absorbed and active plan removed on completion.

Local exit: the I31 completion criterion in the roadmap is executable and green.

## Exit criteria

- accepted target entities and UX are implemented end to end;
- existing downstream Requirements, Decisions, Rules, export facts and historical references remain valid;
- no target Product API/Web flow depends on users understanding compatibility Component Deployment IDs;
- unbounded Application Catalogue views use server-side bounded projections;
- Retired entities are terminal/history-preserving, normal working lists exclude them, and active-reference blockers are explainable;
- no hard-delete path is introduced;
- deterministic browser/screenshot evidence covers representative accepted wireframes;
- relevant core/PostgreSQL/Web/harness/knowledge/Docker/hosted gates pass according to touched scope.

## Blockers

- WP-0 contains blocking semantic To-Be choices listed in the migration roadmap. They must be resolved through canonical project truth rather than implementation convenience.

## Next

Execute WP-0 only. Resolve the downstream compatibility projection and the missing target field/context ownership semantics first; update canonical artifacts and keep the implementation gate closed until those decisions are accepted.