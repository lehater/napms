# Active execution

Current: `PLAN-I27-catalogue-curation.md`.

I27 Catalogue Curation makes supported local NAPMS self-service for Resource Catalogue and Application Communication Catalogue data consumed by Connectivity and related workflows.

Owner requirement: `docs/requirements/catalogue-curation.md`.
Roadmap: `docs/engineering/catalogue-curation-roadmap.md`.
Catalogue HTTP contract: `docs/engineering/catalogue-curation-http-api-contract.md`.

Current gate: **implementation + acceptance evidence present; second final hosted validation pending**.

Implemented:
- ACC `Application -> Component -> Component Deployment` hierarchy, lifecycle/version, immutable DCS authoring and temporal Deployment Resource Binding create/end;
- RC Resource create/rename/retire, realization create/replace, scope-affiliation create/end and responsibility create/end;
- explicit `CurateApplicationCatalogue` / `CurateResourceCatalogue` authority with server-selected catalogue scopes;
- owner-specific PostgreSQL repositories, optimistic concurrency, idempotency receipts, transition/end provenance and deterministic legacy deployment backfill;
- task-oriented authenticated `/api/v1/catalogues/**` routes with server-owned actor/time and required `Idempotency-Key` for mutations;
- Active ACC participant discovery, Resource binding discovery, and Resource workspace scope/search/completeness projection;
- Web `CATALOGUES -> Applications / Resources`, binding/unbinding, DCS authoring and Resource temporal maintenance;
- ADR-011 external Responsibility Scope / Person / Team correlation-reference input without deriving identity or authority.

Acceptance evidence:
- RC/ACC domain/application, authority, migration/backfill and transaction-policy tests;
- HTTP session/idempotency/validation/trust-boundary and temporal route tests;
- Resource workspace application/PostgreSQL/HTTP tests;
- fresh-data journey: catalogue curation -> Scoped Connectivity -> Connectivity Requirement -> `Required`;
- authenticated read allowed while mutation without catalogue curation authority returns `403` and persists nothing;
- local demo hierarchy/authority assertions.

First hosted gate on PR #51:
- passed: Web, knowledge, docker local runtime;
- harness failure was only invalid resume-capsule size/`Current:` format and is fixed here;
- core ran 708 passing tests with one architecture-name false positive; fixed by keeping the ACC domain import relative;
- PostgreSQL ran 126 passing tests with five failures: three stale parent-table cleanups and two nullable-parameter SQL inference failures; both causes are fixed on the current branch.

PR #51 remains draft while fixes accumulate. Mark ready again only for the second final hosted gate. If a material fix is required after that gate, return to draft before editing and gate again.

Primary restart points:
- `tests/integration/postgres/test_i27_fresh_data_journey.py`;
- `tests/integration/postgres/test_i27_catalogue_http_security.py`;
- `tests/integration/postgres/test_resource_catalogue_workspace_i27.py`;
- `src/napms/resource_catalogue/adapters/postgres/curation_list.py`;
- `src/napms/runtime/catalogue_*`;
- `web/src/features/catalogues/`.
