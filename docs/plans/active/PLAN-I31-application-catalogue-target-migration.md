# I31 Application Catalogue Target Migration

Status: `active`

Date: 2026-09-10.

## Goal

Implement the accepted Application Definition / Application Deployment target from domain model through HTTP and Web while preserving existing downstream semantic identities, historical references and repository execution discipline.

The implementation is staged. Domain/contract uncertainty is resolved before infrastructure or Web work, and each coherent semantic stage is integrated through its own squash PR.

## Inputs

Canonical target and M0 closure:
- `docs/decisions/ADR-012-application-definition-deployment-model.md`;
- `docs/decisions/ADR-013-i31-application-catalogue-compatibility-and-reference-semantics.md`;
- `docs/domain/application-communication-catalogue/target-tactical-model.md`;
- `docs/requirements/application-catalogue-target.md`;
- `docs/architecture/application-catalogue-target-boundary.md`;
- `docs/ui/application-catalogue-target.md`;
- `docs/ui/application-catalogue-wireframes.md`.

Current runtime truth and constraints:
- `docs/domain/application-communication-catalogue/tactical-model.md`;
- `docs/architecture/current-architecture.md`;
- `docs/decisions/ADR-011-i27-external-correlation-reference-input.md`;
- `src/napms/application_catalogue/`;
- downstream users of `DirectedInteractionIdentity` / `RuleSemanticIdentity`.

Execution roadmap:
- `docs/engineering/application-catalogue-target-migration-roadmap.md`.

## WP-0 — close target/migration contract

Responsibility: remove blocking semantic ambiguity before code migration.

Outputs:
- accepted per-Deployment-Interaction compatibility projection to the existing downstream stable interaction triple;
- accepted Interaction Definition endpoint/traffic edit semantics preserving immutable downstream snapshots;
- accepted ownership/value semantics for Application metadata, Component metadata and Deployment Company/Environment/Scope context;
- accepted active-reference retirement and traffic-edit dependency rules plus grouped dependency projection;
- target Tactical DDD, product requirement and architecture boundary;
- legacy I27 coexistence rule without fabricated target migration semantics.

Local exit: satisfied and integrated through PR #58.

## WP-1 — domain, application and ports

Responsibility: implement the target ACC model without transport, persistence or Web coupling.

Outputs:
- target entities/value types/invariants for Interaction Definition, Application Deployment and Deployment Interaction;
- interaction-scoped source/destination Resource-binding semantics;
- task-oriented commands and bounded query ports;
- retirement/traffic-edit dependency ports and semantics;
- ACC-owned compatibility-projection contracts preserving downstream stable identity;
- domain/application/architecture tests.

Local exit: satisfied and integrated through PR #59. Target use cases and compatibility identity are executable in memory and existing downstream contracts require no rewrite.

## WP-2 — PostgreSQL and compatibility projection

Responsibility: persist target truth additively and realize the selected downstream compatibility mapping.

Outputs:
- additive migrations and repository adapters;
- explicit Deployment Interaction -> compatibility side/DCS mapping;
- preserved legacy Component Deployment, DCS revision and binding IDs/facts;
- no inference of Company/Environment/Scope or target interaction ownership from legacy display names;
- deterministic persistence/concurrency/idempotency behavior;
- migration replay, repository integration and compatibility-projection tests.

Local exit: satisfied and integrated through PR #60. Fresh target data and existing legacy data coexist without identity rewrite or ambiguous projection.

## WP-3 — HTTP and bounded read models

Responsibility: expose task-oriented target commands and scalable projections for the accepted UX.

Outputs:
- Definition list/detail projections with separately paged Components, Interactions and Deployments;
- global Application Deployment list/detail;
- paged Deployment connectivity rows and Resource-set drill-downs;
- server search/filter/stable sort/paging and totals required by the wireframes;
- task commands for target creation/edit/selection/binding flows;
- structured blocked-retirement/traffic-edit dependencies;
- new product API does not expose compatibility Component Deployment IDs as authoring concepts;
- HTTP contract/security/integration tests.

Implementation state: coded in PR #61. The target read projection is bounded and explicit-time; Resource-set Scope enrichment is query-only composition over ACC membership and RC-owned facts; unsupported Resource Type/Binding-state assumptions were removed from UI truth. Target HTTP exposes Definition/Deployment working sets, task mutations, bounded available-interaction selection, interaction-side Resource membership and terminal retirement with exact dependency counts plus paged drill-down. Compatibility Component Deployment/DCS identities remain backend-only.

Local exit: pending final self-review and repository gates.

## WP-4 — Web target

Responsibility: replace the current I27 Applications projection with the accepted target information architecture.

Outputs:
- `Definitions | Deployments` working sets;
- Definition Overview / Components / Interactions / Deployments tabs;
- compact component and interaction authoring/edit surfaces;
- Application Deployment connectivity table with Resource counts;
- Resource-set drill-down and Add interaction flow;
- blocked dependency UX;
- normal working views exclude Retired entities and omit internal version/UUID noise;
- no hard-delete action;
- `make web-check` evidence.

Local exit: representative target user flow matches the accepted wireframes semantically and remains bounded for large datasets.

## WP-5 — journeys, screenshots and absorption

Responsibility: prove the new authoring projection and unchanged downstream behavior end to end.

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

None known. M0-M2 are integrated. PR #61 remains Draft until WP-3 self-review and all touched-scope gates are green.

## Next

Complete WP-3 diff/architecture review, fix any P0/P1 findings, validate focused HTTP and PostgreSQL proofs, then move PR #61 to Ready once so the repository CI triggers on the final head. If green, squash-merge M3 and start WP-4 from the resulting `main` in a new branch/PR.
