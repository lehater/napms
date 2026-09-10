# Active execution

Current: `PLAN-I27-catalogue-curation.md`.

I27 Catalogue Curation makes supported local NAPMS self-service for Resource Catalogue and Application Communication Catalogue data consumed by Connectivity and related workflows.

Owner requirement: `docs/requirements/catalogue-curation.md`.
Roadmap: `docs/engineering/catalogue-curation-roadmap.md`.
Catalogue HTTP contract: `docs/engineering/catalogue-curation-http-api-contract.md`.

Current gate: **implementation + acceptance evidence present; final hosted validation in progress/retry pending**.

Implemented:
- ACC `Application -> Component -> Component Deployment` hierarchy, lifecycle/version, immutable DCS authoring and temporal Deployment Resource Binding create/end;
- RC Resource create/rename/retire, realization create/replace, scope-affiliation create/end and responsibility create/end;
- explicit `CurateApplicationCatalogue` / `CurateResourceCatalogue` authority with server-selected catalogue scopes;
- owner-specific PostgreSQL repositories, optimistic concurrency, idempotency receipts, creation plus retirement/end provenance and deterministic legacy deployment backfill;
- legacy PostgreSQL fixtures updated to explicit Application/Component parents or corrected parent-aware seed helpers;
- task-oriented authenticated `/api/v1/catalogues/**` routes with server-owned actor/time and required `Idempotency-Key` for mutations;
- Active ACC participant discovery for DCS authoring and Resource discovery for bindings;
- Web `CATALOGUES -> Applications / Resources`, list/search/create/detail, binding/unbinding, DCS authoring and Resource temporal maintenance;
- ADR-011 external Responsibility Scope / Person / Team correlation-reference input without deriving identity or authority;
- Resources workspace effective scope filter, responsibility/contact search and current-fact completeness indicators.

Acceptance evidence in branch:
- RC/ACC domain/application and authority tests;
- migration replay/backfill and transaction-policy PostgreSQL tests;
- HTTP session/idempotency/validation/trust-boundary tests;
- Resource temporal and binding-end route tests;
- Resource workspace application/PostgreSQL/HTTP tests;
- fresh-data journey: catalogue curation -> Scoped Connectivity -> Connectivity Requirement -> `Required`;
- authenticated read allowed while mutation without catalogue curation authority returns `403` and persists nothing;
- local demo hierarchy/authority assertions.

Final hosted gate was first requested on PR #51. Web and knowledge gates passed; harness failed only because the previous resume capsule exceeded 6144 bytes and used an invalid `Current:` format. This compact capsule fixes both harness invariants. Other first-attempt gate results must be inspected before the retry.

If any implementation fix is required after hosted validation, keep PR #51 draft while editing and mark ready again only for the next final gate.

Primary restart points:
- `tests/integration/postgres/test_i27_fresh_data_journey.py`;
- `tests/integration/postgres/test_i27_catalogue_read_vs_mutation_authority.py`;
- `tests/integration/postgres/test_resource_catalogue_workspace_i27.py`;
- `tests/runtime/test_catalogue_resource_workspace_http.py`;
- `src/napms/runtime/catalogue_*`;
- `src/napms/resource_catalogue/adapters/postgres/curation_list.py`;
- `web/src/features/catalogues/`.
