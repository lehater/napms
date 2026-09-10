# Active execution

Current: **I27 Catalogue Curation**.

Selected objective: make the supported local product self-service for Resource Catalogue and Application Communication Catalogue data already consumed by Connectivity and related workflows.

Active plan:
- `docs/plans/active/PLAN-I27-catalogue-curation.md`.

Owner requirement:
- `docs/requirements/catalogue-curation.md`.

Ordered roadmap:
- `docs/engineering/catalogue-curation-roadmap.md`.

Catalogue HTTP contract:
- `docs/engineering/catalogue-curation-http-api-contract.md`.

Current gate: **implementation and acceptance evidence present / final hosted repository validation pending**.

Implemented in the current branch:
- Stage 0 semantic decisions are accepted in Tactical DDD / ADR / architecture / command-contract owners;
- Stage 1 catalogue authority actions and owner-specific consuming adapters are implemented fail-closed;
- Stage 2 Resource Catalogue Domain/Application/Ports covers Resource create/rename/retire, realization create/replace, scope-affiliation create/end, responsibility create/end, owner list/detail reads, optimistic concurrency, idempotency and explicit transition/end provenance;
- Stage 3 ACC covers Application/Component/Component Deployment lifecycle curation, owner-owned hierarchy reads, immutable typed DCS revision authoring and temporal Deployment Resource Binding create/end semantics;
- Stage 4 additive PostgreSQL schemas/repositories persist first-class Application/Component/Deployment and Resource curation, command receipts, optimistic versions and deterministic legacy deployment backfill while preserving existing deployment/DCS identities;
- legacy PostgreSQL integration fixtures that create Component Deployments now use explicit Application -> Component -> Deployment parents or reuse corrected parent-aware seed helpers;
- catalogue composition keeps Authority, ACC and RC behind separate owner-specific connections/UoWs and uses an RC-owned adapter for ACC binding target checks;
- PostgreSQL curation commit policy distinguishes known pre-commit persistence errors from genuinely ambiguous commit acknowledgements;
- Stage 5 task-oriented HTTP routes exist for catalogue list/detail/create workflows, Resource temporal create/replace/end operations, binding create/end and DCS authoring; actor identity comes from the session, command time from the server and mutations require `Idempotency-Key`;
- ACC participant discovery exposes only fully Active Application -> Component -> Deployment chains for cross-entity selection;
- escaped catalogue domain validation at the HTTP process boundary maps to structured `422` rather than generic `500`;
- Stage 6/7 Web navigation includes `CATALOGUES -> Applications / Resources` with list/search/create and bookmarkable detail routes;
- Application detail supports Component/Deployment creation, Resource selection/binding/unbinding and immutable DCS authoring through backend participant discovery rather than manual NAPMS-owned UUID entry;
- Resource detail supports Resource creation, realization create/replace, Resource Scope Affiliation create/end and Resource Responsibility create/end;
- ADR-011 permits explicit input only for external Responsibility Scope / Person / Team correlation references when no registry adapter exists; those references do not grant authority;
- Resources workspace has an owner-side read projection with effective Responsibility Scope filtering, current responsibility/contact search and current-fact completeness indicators;
- frontend catalogue mutations preserve JSON `Content-Type` together with generated `Idempotency-Key` headers.

Executable evidence present in the branch:
- Resource and ACC domain/application curation tests;
- authority admission/denial and scope-substitution tests;
- PostgreSQL catalogue migration/backfill/idempotency tests;
- PostgreSQL curation repository and transaction-policy tests;
- PostgreSQL fresh-data I27 journey from catalogue curation into Scoped Connectivity and Connectivity Requirement declaration;
- PostgreSQL + HTTP read-allowed/mutation-denied security acceptance;
- ACC participant discovery repository/application/HTTP tests;
- catalogue HTTP session/idempotency/validation/transport-boundary tests;
- Resource temporal replacement/end route tests;
- Resource workspace application, PostgreSQL projection and HTTP boundary tests;
- local demo seed hierarchy/authority assertions.

Verification state:
- this chat execution environment cannot clone the repository because direct `github.com` DNS resolution is unavailable, so repository commands cannot be run locally here;
- PR #51 remains draft until this pre-gate synchronization is complete;
- hosted `core gate`, `postgres persistence gate` and `web gate` are configured to run on the PR `ready_for_review` transition;
- `make test`, `make postgres-test` and Web `npm run build` therefore remain the final executable gate before completion/absorption.

Remaining work before I27 completion claim:
1. update PR #51 body to the final implemented/acceptance state;
2. mark PR #51 ready for review to trigger hosted core/PostgreSQL/Web gates;
3. inspect and fix any gate failures; if code changes are required, return the PR to draft and gate again per repository policy;
4. after green final gate, absorb durable outcomes into `docs/engineering/current-state.md`, architecture/UI owners as needed, mark the I27 roadmap complete and retire this active PLAN;
5. squash-merge only after absorption and final green state.

Primary restart points if a gate fails:
- `tests/integration/postgres/test_i27_fresh_data_journey.py`;
- `tests/integration/postgres/test_i27_catalogue_read_vs_mutation_authority.py`;
- `tests/integration/postgres/test_resource_catalogue_workspace_i27.py`;
- `tests/runtime/test_catalogue_resource_workspace_http.py`;
- `src/napms/runtime/catalogue_curation_http.py`;
- `src/napms/runtime/catalogue_temporal_curation_http.py`;
- `src/napms/runtime/catalogue_resource_workspace_http.py`;
- `src/napms/resource_catalogue/adapters/postgres/curation_list.py`;
- `web/src/features/catalogues/`;
- `docs/engineering/catalogue-curation-http-api-contract.md`.
