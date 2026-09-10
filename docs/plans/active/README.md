# Active execution

Current: **I27 Catalogue Curation**.

Selected objective: make the supported local product self-service for Resource Catalogue and Application Communication Catalogue data already consumed by Connectivity and related workflows.

Active plan:
- `docs/plans/active/PLAN-I27-catalogue-curation.md`.

Owner requirement:
- `docs/requirements/catalogue-curation.md`.

Ordered roadmap:
- `docs/engineering/catalogue-curation-roadmap.md`.

Current gate: **Stages 0-3 implemented; Stages 4-6 substantially implemented / repository validation and Stage 7 acceptance pending**.

Implemented in the current branch:
- Stage 0 semantic decisions are accepted in Tactical DDD / ADR / architecture / command-contract owners;
- Stage 1 catalogue authority actions and owner-specific consuming adapters are implemented fail-closed;
- Stage 2 Resource Catalogue Domain/Application/Ports covers Resource create/rename/retire, realization create/replace, scope-affiliation create/end, responsibility create/end, curation list/detail reads, optimistic concurrency, idempotency and explicit transition/end provenance;
- Stage 3 ACC covers Application/Component/Component Deployment lifecycle curation, owner-owned hierarchy reads, immutable typed DCS revision authoring and temporal Deployment Resource Binding create/end semantics;
- Stage 4 additive PostgreSQL schemas/repositories exist for first-class Application/Component/Deployment and Resource curation, command receipts and optimistic versions; local demo seed creates an explicit Application -> Component -> Deployment hierarchy;
- catalogue composition keeps Authority, ACC and RC behind separate owner-specific connections/UoWs and uses an RC-owned adapter for ACC binding target checks;
- PostgreSQL curation commit policy distinguishes known pre-commit persistence errors from genuinely ambiguous commit acknowledgements;
- Stage 5 task-oriented HTTP routes exist for catalogue list/detail/create workflows, Resource temporal facts, bindings and DCS authoring; actor identity comes from the session, command time from the server and mutations require `Idempotency-Key`;
- ACC participant discovery exposes only fully Active Application -> Component -> Deployment chains for cross-entity selection;
- escaped ACC domain validation at the HTTP process boundary maps to structured `422 CatalogueValidationError` rather than generic `500`;
- Stage 6 Web navigation now includes `CATALOGUES -> Applications / Resources` with list/search/create and bookmarkable detail routes;
- Application detail supports Component/Deployment creation, Resource selection/binding and immutable DCS authoring through backend participant discovery rather than manual UUID entry;
- Resource detail supports Resource creation and new technical-address realization entry and displays current scope affiliations/responsibility facts;
- frontend catalogue mutations preserve JSON `Content-Type` together with generated `Idempotency-Key` headers.

Executable evidence added in the branch:
- Resource and ACC domain/application curation tests;
- PostgreSQL I27 fresh-catalogue curation integration test;
- ACC participant discovery repository/application/HTTP tests;
- catalogue HTTP session/idempotency/transport-boundary tests;
- catalogue invariant-to-422 boundary test;
- ACC and RC transaction-policy tests for known pre-commit versus ambiguous commit failures;
- local demo seed hierarchy/authority assertions.

Verification state:
- this chat execution environment cannot clone the repository because it cannot resolve `github.com`, so local repository commands cannot be run here;
- PR #51 remains draft and no final hosted PR gate has been requested;
- `make test`, `make postgres-test` and `make web-check` therefore remain required before any completion claim.

Open P1 work before final gate:
- update legacy cross-context PostgreSQL integration fixtures that still insert `component_deployments` without explicit Application/Component parents after `application-catalogue/0003`; do not hide this with a permanent production compatibility trigger;
- prove fresh-start and upgrade/backfill behavior of the additive catalogue migrations under PostgreSQL;
- run backend/core, PostgreSQL and Web build gates and fix resulting failures;
- execute the Stage 7 fresh-data acceptance journey through catalogue onboarding into existing Connectivity/Need flow and prove mutation-denied/read-allowed behavior.

Known product boundary still unresolved for ordinary Web forms:
- Responsibility Scope and Responsible Party are opaque external references in the accepted I27 model and no canonical discovery registry is accepted yet;
- do not invent a Company/Organization context, equate session actor IDs with Person references, or reuse `ReadScopedConnectivity` discovery as catalogue mutation authority/discovery merely to make those forms convenient;
- current Resource detail therefore presents existing scope/responsibility facts while their normal create forms remain blocked on an accepted discovery/input contract.

Next execution target:
1. migrate the remaining PostgreSQL fixtures to explicit Application -> Component -> Deployment setup;
2. run/obtain `make test`, `make postgres-test` and `make web-check` evidence;
3. fix gate failures and fold temporary transaction-policy subclasses into the base repositories if the code remains clearer after verification;
4. complete Stage 7 acceptance, update PR #51 summary/checklist, then mark ready for the final hosted gate.

Primary restart points:
- `tests/integration/postgres/` legacy ACC fixture setup;
- `tests/integration/postgres/test_catalogue_curation_i27.py`;
- `src/napms/application_catalogue/adapters/postgres/transactional_curation_repository.py`;
- `src/napms/resource_catalogue/adapters/postgres/transactional_curation_repository.py`;
- `src/napms/runtime/catalogue_curation_http.py`;
- `web/src/features/catalogues/`;
- `docs/plans/active/PLAN-I27-catalogue-curation.md`.
