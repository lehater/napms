# Active execution

Current: **I27 Catalogue Curation**.

Selected objective: make the supported local product self-service for Resource Catalogue and Application Communication Catalogue data already consumed by Connectivity and related workflows.

Active plan:
- `docs/plans/active/PLAN-I27-catalogue-curation.md`.

Owner requirement:
- `docs/requirements/catalogue-curation.md`.

Ordered roadmap:
- `docs/engineering/catalogue-curation-roadmap.md`.

Current gate: **Stage 3 / ACC core hierarchy and write-side in progress**.

Implemented in the current branch:
- Stage 0 P0 semantic decisions are accepted in Tactical DDD / ADR / architecture / command-contract owners;
- Stage 1 catalogue authority actions and owner-specific consuming adapters are implemented with fail-closed tests;
- Stage 2 Resource Catalogue Domain/Application/Ports covers Resource create/rename/retire, realization create/replace, scope-affiliation create/end, responsibility create/end, curation list/detail read contracts, optimistic concurrency, idempotency and explicit transition/end provenance;
- Stage 3 ACC now has Application/Component domain identities plus Application rename/retire and Component create/rename/retire application commands with parent/lifecycle guards, optimistic concurrency, idempotency and explicit retirement provenance;
- existing Component Deployment and DCS semantic identifiers remain unchanged while hierarchy migration is still closed.

Verification state:
- executable tests have been added for the new core contracts;
- this session cannot clone the repository because external DNS access from the local execution container is unavailable;
- PR #51 is still draft, and the repository `core gate` workflow triggers on `ready_for_review`, so no current-head CI result exists yet;
- implementation progress is therefore not treated as a passed repository gate.

Still closed:
- Component Deployment parent/lifecycle persistence migration;
- ACC Deployment Resource Binding and DCS write commands that depend on the completed deployment lifecycle contract;
- PostgreSQL command repositories/idempotency storage;
- HTTP mutation routes;
- Web `Resources` / `Applications` mutation workspaces.

Next execution target:
- finish ACC owner-owned curation read contracts for Application/Component hierarchy;
- prepare the atomic Component Deployment hierarchy/schema migration so `componentId`, lifecycle and version are introduced without nullable transitional business semantics;
- then complete binding/DCS commands against that stable participant model before opening general HTTP/UI work.

Primary restart points:
- `docs/domain/application-communication-catalogue/tactical-model.md`;
- `docs/domain/resource-catalogue/tactical-model.md`;
- `docs/engineering/catalogue-curation-command-contract.md`;
- `src/napms/application_catalogue/application/structure_curation.py`;
- `src/napms/resource_catalogue/application/curation.py`;
- `src/napms/resource_catalogue/application/realization_curation.py`;
- `docs/plans/active/PLAN-I27-catalogue-curation.md`.
