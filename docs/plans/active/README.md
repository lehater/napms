# Active execution

Current: **I27 Catalogue Curation**.

Selected objective: make the supported local product self-service for Resource Catalogue and Application Communication Catalogue data already consumed by Connectivity and related workflows.

Active plan:
- `docs/plans/active/PLAN-I27-catalogue-curation.md`.

Owner requirement:
- `docs/requirements/catalogue-curation.md`.

Ordered roadmap:
- `docs/engineering/catalogue-curation-roadmap.md`.

Current gate: **Stage 2 / Resource Catalogue core write-side in progress**.

Completed current-increment closure:
- Stage 0 P0 semantic decisions are accepted in Tactical DDD / ADR / architecture / command-contract owners;
- Stage 1 catalogue authority actions and owner-specific consuming adapters are implemented with fail-closed tests;
- the first `CreateResource` and `CreateApplication` application slices establish server-owned identity/provenance and idempotent command semantics, including concurrent-winner recovery.

Still closed:
- PostgreSQL schema/write repositories and migration;
- HTTP mutation routes;
- Web `Resources` / `Applications` mutation workspaces.

Next execution target:
- complete Resource Catalogue Domain/Application/Ports commands and invariants for rename/retire plus temporal realization, scope affiliation and responsibility maintenance;
- then complete the corresponding ACC core hierarchy/write commands before opening PostgreSQL Stage 4.

Primary restart points:
- `docs/domain/resource-catalogue/tactical-model.md`;
- `docs/domain/application-communication-catalogue/tactical-model.md`;
- `docs/engineering/catalogue-curation-command-contract.md`;
- `src/napms/resource_catalogue/application/curation.py`;
- `src/napms/application_catalogue/application/curation.py`;
- `docs/plans/active/PLAN-I27-catalogue-curation.md`.
