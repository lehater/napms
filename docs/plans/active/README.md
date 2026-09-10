# Active execution

Current: **I27 Catalogue Curation**.

Selected objective: make the supported local product self-service for Resource Catalogue and Application Communication Catalogue data already consumed by Connectivity and related workflows.

Active plan:
- `docs/plans/active/PLAN-I27-catalogue-curation.md`.

Owner requirement:
- `docs/requirements/catalogue-curation.md`.

Ordered roadmap:
- `docs/engineering/catalogue-curation-roadmap.md`.

Current gate: **Stage 3 core implemented / verification pending; Stage 4 additive persistence work started**.

Implemented in the current branch:
- Stage 0 P0 semantic decisions are accepted in Tactical DDD / ADR / architecture / command-contract owners;
- Stage 1 catalogue authority actions and owner-specific consuming adapters are implemented with fail-closed tests;
- Stage 2 Resource Catalogue Domain/Application/Ports covers Resource create/rename/retire, realization create/replace, scope-affiliation create/end, responsibility create/end, curation list/detail read contracts, optimistic concurrency, idempotency and explicit transition/end provenance;
- Stage 3 ACC covers Application/Component/Component Deployment create or lifecycle curation, owner-owned Application/Component/Deployment read hierarchy, immutable typed DCS revision authoring and temporal Deployment Resource Binding create/end semantics;
- DCS authoring semantics are ACC-owned value objects; the existing JSON projection codec is reached through an adapter rather than by introducing an ACC application dependency on Policy Export;
- Component Deployment now has mandatory immutable `componentId`, lifecycle/version and retirement provenance in the domain model;
- additive `application-catalogue/0003` creates Application/Component persistence and deterministically backfills every legacy Component Deployment without changing any existing deployment/DCS UUID;
- local demo seed now creates an explicit Application -> Component -> Deployment hierarchy and grants catalogue curation actions in their fixed catalogue authority scopes.

Verification state:
- executable tests have been added for Resource curation, ACC structural lifecycle, Component Deployment lifecycle, DCS authoring and Deployment Resource Binding semantics;
- this session cannot clone the repository because the execution container cannot resolve `github.com`;
- `make test` excludes PostgreSQL-marked integration suites, while PR #51 remains draft and the repository core workflow triggers on `ready_for_review`;
- no current-head repository gate result therefore exists, and implemented stages are not being represented as verified.

Stage 4 blockers / open work:
- implement PostgreSQL command repositories, idempotency receipts and optimistic version checks for RC/ACC;
- add persistence columns/migrations for Resource lifecycle/version/end provenance and Deployment Resource Binding version/end provenance;
- update remaining cross-context PostgreSQL fixtures that still insert Component Deployments without explicit parents; these are `postgres-test` blockers, not Stage 3 core blockers;
- prove `application-catalogue/0003` fresh-start and upgrade/backfill behavior in PostgreSQL integration tests.

Still closed:
- HTTP mutation routes;
- Web `Resources` / `Applications` mutation workspaces;
- end-to-end fresh-data acceptance through Connectivity.

Next execution target:
- complete additive Stage 4 schema for write-owned lifecycle/idempotency fields;
- implement the smallest PostgreSQL curation repositories for Application/Component/Deployment/DCS/Binding and Resource core commands;
- update PostgreSQL fixtures and migration tests before opening HTTP Stage 5.

Primary restart points:
- `src/napms/application_catalogue/application/deployment_curation.py`;
- `src/napms/application_catalogue/application/dcs_curation.py`;
- `src/napms/application_catalogue/application/binding_curation.py`;
- `src/napms/application_catalogue/adapters/postgres/migrations/0003_catalogue_hierarchy.sql`;
- `src/napms/application_catalogue/adapters/postgres/repository.py`;
- `src/napms/resource_catalogue/application/curation.py`;
- `docs/plans/active/PLAN-I27-catalogue-curation.md`.
